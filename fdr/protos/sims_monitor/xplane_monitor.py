"""
X-Plane 12 — Moniteur de datarefs
GUI PySide6 / Qt Fusion  |  Groupes thématiques : Position / Vol / Moteur & Appareil

API X-Plane 12 Web REST v3 (port 8086)
Protocole :
  1. GET /api/v3/datarefs?filter[name]=<path>   → résolution path → id (une fois au démarrage)
  2. GET /api/v3/datarefs/<id>/value             → lecture de la valeur (chaque cycle)
  Les datarefs de type "data" (string) sont retournées encodées en base64.

Dépendances :
    pip install PySide6 requests

Lancement :
    python xplane_monitor.py

Datarefs surveillées :
    sim/flightmodel/position/latitude          → Latitude (°)
    sim/flightmodel/position/longitude         → Longitude (°)
    sim/time/zulu_time_sec                    → Secondes UTC depuis minuit
    sim/time/local_date_days                  → Jours depuis le 1er janvier de l'année en cours
    sim/flightmodel/position/elevation        → Altitude MSL (m)
    sim/flightmodel/position/y_agl             → Altitude AGL (m)
    sim/flightmodel/position/psi              → Cap vrai (°)
    sim/flightmodel/position/mag_psi           → Cap magnétique (°)
    sim/flightmodel/position/indicated_airspeed → IAS (m/s)
    sim/flightmodel/position/groundspeed      → GS (m/s)
    sim/flightmodel/engine/ENGN_power         → Puissance moteur (W) — tableau
    sim/aircraft/view/acf_ICAO                → Code OACI de l'appareil
    sim/aircraft/view/acf_descrip             → Nom complet de l'appareil
"""

import base64
import sys
import time
from datetime import datetime, timedelta, timezone

import requests
from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

XPLANE_HOST      = "127.0.0.1"
XPLANE_PORT      = 8086
BASE_URL         = f"http://{XPLANE_HOST}:{XPLANE_PORT}/api/v3"
POLL_INTERVAL_MS = 1000

# ---------------------------------------------------------------------------
# Constantes de conversion
# ---------------------------------------------------------------------------

M_TO_FT   = 3.28084
MPS_TO_KT = 1.94384
W_TO_HP   = 0.00134102

# ---------------------------------------------------------------------------
# Datarefs à surveiller
# ---------------------------------------------------------------------------

DATAREF_PATHS: dict[str, str] = {
    "latitude":       "sim/flightmodel/position/latitude",
    "longitude":      "sim/flightmodel/position/longitude",
    "zulu_sec":       "sim/time/zulu_time_sec",
    "date_days":      "sim/time/local_date_days",
    "alt_msl_m":      "sim/flightmodel/position/elevation",
    "alt_agl_m":      "sim/flightmodel/position/y_agl",
    "heading_true":   "sim/flightmodel/position/psi",
    "heading_mag":    "sim/flightmodel/position/mag_psi",
    "ias_mps":        "sim/flightmodel/position/indicated_airspeed",
    "gs_mps":         "sim/flightmodel/position/groundspeed",
    "engine_power_w": "sim/flightmodel/engine/ENGN_power",
    "acf_icao":       "sim/aircraft/view/acf_ICAO",
    "acf_name":       "sim/aircraft/view/acf_descrip",
}

# ---------------------------------------------------------------------------
# Couche réseau
# ---------------------------------------------------------------------------

class XPlaneAPI:
    """
    Encapsule le protocole REST X-Plane 12 v3 :
      - Étape 1 (init) : GET /datarefs?filter[name]=<path>  → id numérique (mis en cache)
      - Étape 2 (poll) : GET /datarefs/<id>/value           → valeur courante
    """

    def __init__(self, host: str, port: int) -> None:
        self._base    = f"http://{host}:{port}/api/v3"
        self._cache: dict[str, int] = {}          # clé → id numérique
        self._types:  dict[str, str] = {}         # clé → value_type
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    # ── Résolution des IDs (appelée une seule fois au démarrage) ────────────

    def resolve_ids(self, paths: dict[str, str]) -> None:
        for key, path in paths.items():
            resp = self._session.get(
                f"{self._base}/datarefs",
                params={"filter[name]": path},
                timeout=5,
            )
            resp.raise_for_status()
            records = resp.json()["data"]
            if not records:
                raise ValueError(f"Dataref introuvable : {path}")
            self._cache[key] = records[0]["id"]
            self._types[key] = records[0]["value_type"]

    # ── Lecture d'une valeur via /datarefs/<id>/value ────────────────────────

    def _fetch_value(self, key: str) -> object:
        dr_id = self._cache[key]
        resp  = self._session.get(
            f"{self._base}/datarefs/{dr_id}/value",
            timeout=3,
        )
        resp.raise_for_status()
        return resp.json()["data"]

    # ── API publique ─────────────────────────────────────────────────────────

    def get_float(self, key: str) -> float:
        return float(self._fetch_value(key))

    def get_float_array(self, key: str) -> list[float]:
        val = self._fetch_value(key)
        if isinstance(val, list):
            return [float(v) for v in val if v is not None]
        return [float(val)]

    def get_string(self, key: str) -> str:
        """
        Les datarefs de type 'data' sont retournées encodées en base64.
        On décode et on retire les octets nuls de fin.
        """
        raw = self._fetch_value(key)
        if isinstance(raw, str):
            try:
                decoded = base64.b64decode(raw)
                return decoded.rstrip(b"\x00").decode("utf-8", errors="replace").strip()
            except Exception:
                return raw.strip()
        # Cas de repli : liste d'entiers (anciens firmwares)
        if isinstance(raw, list):
            return bytes(b for b in raw if b != 0).decode("utf-8", errors="replace").strip()
        return str(raw).strip()

# ---------------------------------------------------------------------------
# Construction de l'horodatage ISO 8601
# ---------------------------------------------------------------------------

def build_iso(zulu_sec: float, date_days: float) -> str:
    year = datetime.now(timezone.utc).year
    jan1 = datetime(year, 1, 1, tzinfo=timezone.utc)
    dt   = (jan1
            + timedelta(days=int(date_days) - 1)
            + timedelta(seconds=float(zulu_sec)))
    return dt.strftime("%Y-%m-%dT%H:%M:%S Z")

# ---------------------------------------------------------------------------
# Worker — thread de polling
# ---------------------------------------------------------------------------

class PollerWorker(QObject):

    data_ready  = Signal(dict)
    error       = Signal(str)
    init_failed = Signal(str)

    def __init__(self, interval_ms: int = POLL_INTERVAL_MS) -> None:
        super().__init__()
        self._interval = interval_ms / 1000.0
        self._running  = True
        self._api      = XPlaneAPI(XPLANE_HOST, XPLANE_PORT)

    def run(self) -> None:
        # ── Étape 1 : résolution des IDs ──────────────────────────────────
        try:
            self._api.resolve_ids(DATAREF_PATHS)
        except Exception as e:
            self.init_failed.emit(f"Résolution des IDs échouée : {e}")
            return

        # ── Étape 2 : boucle de polling ───────────────────────────────────
        while self._running:
            try:
                s: dict = {}

                s["latitude"]  = f"{self._api.get_float('latitude'):.6f} °"
                s["longitude"] = f"{self._api.get_float('longitude'):.6f} °"

                zulu = self._api.get_float("zulu_sec")
                days = self._api.get_float("date_days")
                s["sim_time"] = build_iso(zulu, days)

                s["alt_msl"] = f"{self._api.get_float('alt_msl_m') * M_TO_FT:,.0f} ft"
                s["alt_agl"] = f"{self._api.get_float('alt_agl_m') * M_TO_FT:,.0f} ft"
                s["heading_true"] = f"{self._api.get_float('heading_true'):.1f} °"
                s["heading_mag"]  = f"{self._api.get_float('heading_mag'):.1f} °"
                s["ias"]     = f"{self._api.get_float('ias_mps') * MPS_TO_KT:.1f} kt"
                s["gs"]      = f"{self._api.get_float('gs_mps')  * MPS_TO_KT:.1f} kt"

                power_arr = self._api.get_float_array("engine_power_w")
                s["power"] = f"{sum(power_arr) * W_TO_HP:.0f} hp"

                s["acf_icao"] = self._api.get_string("acf_icao")
                s["acf_name"] = self._api.get_string("acf_name")

                self.data_ready.emit(s)

            except requests.ConnectionError:
                self.error.emit("Connexion refusée — X-Plane lancé ?")
            except requests.Timeout:
                self.error.emit("Timeout — X-Plane ne répond pas.")
            except requests.HTTPError as e:
                self.error.emit(f"Erreur HTTP {e.response.status_code}")
            except Exception as e:
                self.error.emit(f"Erreur : {e}")

            # Pause interruptible par tranches de 100 ms
            elapsed, step = 0.0, 0.1
            while self._running and elapsed < self._interval:
                time.sleep(step)
                elapsed += step

    def stop(self) -> None:
        self._running = False

# ---------------------------------------------------------------------------
# Widget DataRow — une ligne label / valeur
# ---------------------------------------------------------------------------

class DataRow(QWidget):

    def __init__(self, label: str, val_width: int = 200) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self._lbl = QLabel(label)
        self._lbl.setFixedWidth(150)
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._val = QLabel("—")
        self._val.setFixedWidth(val_width)
        self._val.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._val.setFont(font)

        layout.addWidget(self._lbl)
        layout.addWidget(self._val)
        layout.addStretch()

    def set_value(self, text: str) -> None:
        self._val.setText(text)

# ---------------------------------------------------------------------------
# Fenêtre principale
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("X-Plane 12 — Moniteur de datarefs")
        self.setMinimumWidth(520)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        # ── Groupe : Appareil ────────────────────────────────────────────
        grp_acf = QGroupBox("Appareil")
        lay_acf = QGridLayout(grp_acf)
        self._row_icao = DataRow("Code OACI")
        self._row_name = DataRow("Modèle", val_width=260)
        lay_acf.addWidget(self._row_icao, 0, 0)
        lay_acf.addWidget(self._row_name, 1, 0)
        root.addWidget(grp_acf)

        # ── Groupe : Position ────────────────────────────────────────────
        grp_pos = QGroupBox("Position")
        lay_pos = QGridLayout(grp_pos)
        self._row_lat  = DataRow("Latitude")
        self._row_lon  = DataRow("Longitude")
        self._row_time = DataRow("Heure sim (UTC)", val_width=220)
        lay_pos.addWidget(self._row_lat,  0, 0)
        lay_pos.addWidget(self._row_lon,  1, 0)
        lay_pos.addWidget(self._row_time, 2, 0)
        root.addWidget(grp_pos)

        # ── Groupe : Vol ─────────────────────────────────────────────────
        grp_vol = QGroupBox("Vol")
        lay_vol = QGridLayout(grp_vol)
        self._row_msl = DataRow("Altitude MSL")
        self._row_agl = DataRow("Altitude AGL")
        self._row_hdg_true = DataRow("Cap vrai")
        self._row_hdg_mag  = DataRow("Cap magnétique")
        self._row_ias = DataRow("Vitesse IAS")
        self._row_gs  = DataRow("Vitesse GS")
        lay_vol.addWidget(self._row_msl,      0, 0)
        lay_vol.addWidget(self._row_agl,      1, 0)
        lay_vol.addWidget(self._row_hdg_true, 2, 0)
        lay_vol.addWidget(self._row_hdg_mag,  3, 0)
        lay_vol.addWidget(self._row_ias,      4, 0)
        lay_vol.addWidget(self._row_gs,       5, 0)
        root.addWidget(grp_vol)

        # ── Groupe : Moteur ──────────────────────────────────────────────
        grp_eng = QGroupBox("Moteur")
        lay_eng = QGridLayout(grp_eng)
        self._row_pwr = DataRow("Puissance totale")
        lay_eng.addWidget(self._row_pwr, 0, 0)
        root.addWidget(grp_eng)

        root.addStretch()

        # ── Barre de statut ──────────────────────────────────────────────
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Résolution des datarefs en cours…")

        # ── Thread de polling ────────────────────────────────────────────
        self._thread = QThread(self)
        self._worker = PollerWorker(POLL_INTERVAL_MS)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.data_ready.connect(self._on_data)
        self._worker.error.connect(self._on_error)
        self._worker.init_failed.connect(self._on_init_failed)

        self._thread.start()

    # ── Slots ─────────────────────────────────────────────────────────────

    def _on_data(self, s: dict) -> None:
        self._row_icao.set_value(s.get("acf_icao", "—"))
        self._row_name.set_value(s.get("acf_name", "—"))
        self._row_lat.set_value(s.get("latitude",  "—"))
        self._row_lon.set_value(s.get("longitude", "—"))
        self._row_time.set_value(s.get("sim_time", "—"))
        self._row_msl.set_value(s.get("alt_msl",  "—"))
        self._row_agl.set_value(s.get("alt_agl",  "—"))
        self._row_hdg_true.set_value(s.get("heading_true", "—"))
        self._row_hdg_mag.set_value(s.get("heading_mag",  "—"))
        self._row_ias.set_value(s.get("ias",      "—"))
        self._row_gs.set_value(s.get("gs",        "—"))
        self._row_pwr.set_value(s.get("power",    "—"))
        self._status.showMessage(
            f"Connecté  |  Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}"
        )

    def _on_error(self, msg: str) -> None:
        self._status.showMessage(f"⚠  {msg}")

    def _on_init_failed(self, msg: str) -> None:
        self._status.showMessage(f"✖  {msg}")

    # ── Arrêt propre ──────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._worker.stop()
        self._thread.quit()
        self._thread.wait(3000)
        event.accept()

# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
