"""
MSFS 2020 / MSFS 2024 / P3D v5-v6 — Moniteur de SimVars
GUI PySide6 / Qt Fusion  |  Groupes thématiques : Position / Vol / Moteur & Appareil

Prérequis :
    pip install PySide6 SimConnect

Contrainte :
    SimConnect est une API Windows native (DLL).
    Ce script doit tourner sur la MÊME machine que le simulateur,
    ou sur le réseau si SimConnect.cfg est configuré en conséquence.

SimVars lues :
    PLANE LATITUDE              → Latitude (°)
    PLANE LONGITUDE             → Longitude (°)
    ABSOLUTE TIME               → Secondes depuis epoch J2000 → ISO 8601 UTC
    INDICATED ALTITUDE          → Altitude MSL (ft)
    PLANE ALT ABOVE GROUND      → Altitude AGL (ft)
    PLANE HEADING DEGREES TRUE  → Cap vrai (°)
    PLANE HEADING DEGREES MAGNETIC → Cap magnétique (°)
    AIRSPEED INDICATED          → IAS (kt)
    GROUND VELOCITY             → GS (kt)
    GENERAL ENG BRAKE POWER:1..4→ Puissance moteur (hp) — somme des moteurs actifs
    ATC TYPE                    → Type OACI
    TITLE                       → Nom complet de l'appareil
"""

import sys
import time
from datetime import datetime, timedelta, timezone

from SimConnect import SimConnect, AircraftRequests
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

POLL_INTERVAL_MS = 1000       # ms entre deux cycles
MAX_ENGINES      = 4          # slots moteurs à sommer (MSFS supporte jusqu'à 4)

# ---------------------------------------------------------------------------
# Constantes de conversion
# ---------------------------------------------------------------------------

# J2000 epoch : 1er janvier 2000 à 12h00 UTC
J2000_EPOCH = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

# ---------------------------------------------------------------------------
# Couche SimConnect
# ---------------------------------------------------------------------------

class SimVarReader:
    """
    Encapsule la connexion SimConnect et la lecture des SimVars.
    Utilise AircraftRequests pour un accès simple par nom de variable.
    """

    def __init__(self) -> None:
        self._sm: SimConnect | None = None
        self._aq: AircraftRequests | None = None

    def connect(self) -> None:
        """Établit la connexion au simulateur. Lève une exception si indisponible."""
        self._sm = SimConnect()
        # _time=0 : pas de cache côté bibliothèque, on lit la valeur fraîche à chaque appel
        self._aq = AircraftRequests(self._sm, _time=0)

    def disconnect(self) -> None:
        if self._sm:
            try:
                self._sm.exit()
            except Exception:
                pass
            self._sm = None
            self._aq = None

    @property
    def connected(self) -> bool:
        return self._sm is not None and self._aq is not None

    def get(self, simvar: str):
        """Retourne la valeur brute d'une SimVar, ou None si indisponible."""
        if not self.connected:
            return None
        try:
            return self._aq.get(simvar)
        except Exception:
            return None

    def get_engine_power_hp(self) -> float:
        """
        Somme la puissance de tous les moteurs actifs.
        GENERAL ENG BRAKE POWER:N est en ft-lb/s → conversion en HP (1 HP = 550 ft-lb/s).
        """
        total = 0.0
        for i in range(1, MAX_ENGINES + 1):
            val = self.get(f"GENERAL ENG BRAKE POWER:{i}")
            if val is not None:
                try:
                    total += float(val)
                except (TypeError, ValueError):
                    pass
        return total / 550.0     # ft-lb/s → HP

# ---------------------------------------------------------------------------
# Construction de l'horodatage ISO 8601
# ---------------------------------------------------------------------------

def absolute_time_to_iso(abs_time: float) -> str:
    """
    ABSOLUTE TIME = secondes écoulées depuis l'epoch J2000 (01/01/2000 12:00 UTC).
    """
    try:
        dt = J2000_EPOCH + timedelta(seconds=float(abs_time))
        return dt.strftime("%Y-%m-%dT%H:%M:%S Z")
    except Exception:
        return "—"

# ---------------------------------------------------------------------------
# Worker — thread de polling
# ---------------------------------------------------------------------------

class PollerWorker(QObject):

    data_ready  = Signal(dict)
    error       = Signal(str)
    status_msg  = Signal(str)

    def __init__(self, interval_ms: int = POLL_INTERVAL_MS) -> None:
        super().__init__()
        self._interval = interval_ms / 1000.0
        self._running  = True
        self._reader   = SimVarReader()

    def run(self) -> None:
        # ── Connexion initiale (avec retry) ──────────────────────────────
        self.status_msg.emit("Connexion au simulateur…")
        while self._running and not self._reader.connected:
            try:
                self._reader.connect()
                self.status_msg.emit("Connecté — lecture en cours…")
            except Exception:
                self.error.emit("Simulateur introuvable — en attente…")
                self._sleep(3.0)

        # ── Boucle de polling ─────────────────────────────────────────────
        while self._running:
            try:
                s: dict = {}

                lat = self._reader.get("PLANE LATITUDE")
                lon = self._reader.get("PLANE LONGITUDE")
                s["latitude"]  = f"{float(lat):.6f} °" if lat is not None else "—"
                s["longitude"] = f"{float(lon):.6f} °" if lon is not None else "—"

                abs_t = self._reader.get("ABSOLUTE TIME")
                s["sim_time"] = absolute_time_to_iso(abs_t) if abs_t is not None else "—"

                alt_msl = self._reader.get("INDICATED ALTITUDE")
                alt_agl = self._reader.get("PLANE ALT ABOVE GROUND")
                s["alt_msl"] = f"{float(alt_msl):,.0f} ft" if alt_msl is not None else "—"
                s["alt_agl"] = f"{float(alt_agl):,.0f} ft" if alt_agl is not None else "—"

                hdg_true = self._reader.get("PLANE HEADING DEGREES TRUE")
                hdg_mag  = self._reader.get("PLANE HEADING DEGREES MAGNETIC")
                s["heading_true"] = f"{float(hdg_true):.1f} °" if hdg_true is not None else "—"
                s["heading_mag"]  = f"{float(hdg_mag):.1f} °"  if hdg_mag  is not None else "—"

                ias = self._reader.get("AIRSPEED INDICATED")
                gs  = self._reader.get("GROUND VELOCITY")
                s["ias"] = f"{float(ias):.1f} kt" if ias is not None else "—"
                s["gs"]  = f"{float(gs):.1f} kt"  if gs  is not None else "—"

                power_hp = self._reader.get_engine_power_hp()
                s["power"] = f"{power_hp:.0f} hp"

                acf_type  = self._reader.get("ATC TYPE")
                acf_title = self._reader.get("TITLE")
                s["acf_icao"] = str(acf_type).strip()  if acf_type  else "—"
                s["acf_name"] = str(acf_title).strip() if acf_title else "—"

                self.data_ready.emit(s)

            except Exception as e:
                # Perte de connexion → tentative de reconnexion
                self.error.emit(f"Connexion perdue : {e} — reconnexion…")
                self._reader.disconnect()
                self._sleep(3.0)
                try:
                    self._reader.connect()
                    self.status_msg.emit("Reconnecté.")
                except Exception:
                    pass

            self._sleep(self._interval)

    def _sleep(self, duration: float) -> None:
        """Pause interruptible par tranches de 100 ms."""
        elapsed, step = 0.0, 0.1
        while self._running and elapsed < duration:
            time.sleep(step)
            elapsed += step

    def stop(self) -> None:
        self._running = False
        self._reader.disconnect()

# ---------------------------------------------------------------------------
# Widget DataRow — label + valeur monospace
# ---------------------------------------------------------------------------

class DataRow(QWidget):

    def __init__(self, label: str, val_width: int = 200) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self._lbl = QLabel(label)
        self._lbl.setFixedWidth(160)
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
        self.setWindowTitle("MSFS / P3D — Moniteur SimConnect")
        self.setMinimumWidth(540)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        # ── Groupe : Appareil ────────────────────────────────────────────
        grp_acf = QGroupBox("Appareil")
        lay_acf = QGridLayout(grp_acf)
        self._row_icao = DataRow("Code OACI / Type")
        self._row_name = DataRow("Modèle", val_width=280)
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
        self._status.showMessage("Démarrage…")

        # ── Thread de polling ────────────────────────────────────────────
        self._thread = QThread(self)
        self._worker = PollerWorker(POLL_INTERVAL_MS)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.data_ready.connect(self._on_data)
        self._worker.error.connect(self._on_error)
        self._worker.status_msg.connect(self._on_status)

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

    def _on_status(self, msg: str) -> None:
        self._status.showMessage(msg)

    # ── Arrêt propre ──────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._worker.stop()
        self._thread.quit()
        self._thread.wait(4000)
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
