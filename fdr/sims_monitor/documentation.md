# 📖 Simulator Monitor - Documentation Complète

*Module unifié pour MSFS/P3D et X-Plane 12 - Enregistrement des données de vol en temps réel*

---

## 📦 Table des Matières

1. [Présentation](#présentation)
2. [Installation](#installation)
3. [Utilisation Rapide](#utilisation-rapide)
4. [API de Base](#api-de-base)
5. [Modes de Connexion](#modes-de-connexion)
6. [Détection Automatique Décollage/Atterrissage](#détection-automatique-décollageatterrissage)
7. [Classes et Méthodes](#classes-et-méthodes)
8. [Messages de Callback](#messages-de-callback)
9. [Exemples Complets](#exemples-complets)
10. [Conformité RFC 7946](#conformité-rfc-7946)
11. [Gestion des Erreurs](#gestion-des-erreurs)

---

## 🎯 Présentation

Le module **sim_monitor** fournit une interface unifiée pour :
- **Enregistrer** les données de vol en temps réel depuis **MSFS 2020/2024**, **P3D** ou **X-Plane 12**
- **Stocker** les données au format **GeoJSON** (conforme RFC 7946)
- **Détecter automatiquement** le décollage et l'atterrissage
- **Gérer** les connexions en mode **automatique** ou **manuel** (pour intégration GUI)

---

## 💻 Installation

### Dépendances

```bash
# Pour X-Plane (API REST)
pip install requests

# Pour MSFS/P3D (SimConnect - Windows uniquement)
pip install SimConnect
```

### Intégration

```python
from fdr.sims_monitor.sim_monitor import create_monitor, SimulatorType, FlightState
```

---

## ⚡ Utilisation Rapide

### Version Basique (Points uniquement)

```python
monitor = create_monitor(
    simulator_type=SimulatorType.XPLANE.value,
    geojson_path="/data/vol001.json"
)
monitor.start_monitoring()
# ... vol en cours ...
monitor.stop_monitoring()
```

### Version avec Trajectoire (Points + LineString pour QGIS)

```python
monitor = create_monitor(
    simulator_type=SimulatorType.XPLANE.value,
    geojson_path="/data/trajectoire.geojson",
    include_trajectory=True  # Ajoute une LineString pour visualisation
)
monitor.start_monitoring()
```

### Version avec Connexion Manuelle (pour GUI)

```python
monitor = create_monitor(
    simulator_type=SimulatorType.XPLANE.value,
    geojson_path="/data/vol002.json",
    auto_connect=False  # Mode manuel
)
monitor.set_connection_callback(on_connection_change)
monitor.start_monitoring()

# Quand l'utilisateur clique sur "Se connecter" dans le GUI :
monitor.connect()
```

---

## 🎚️ API de Base

### Création du Moniteur

```python
monitor = create_monitor(
    simulator_type: str,      # "msfs" ou "xplane"
    geojson_path: str,        # Chemin du fichier de sortie
    poll_interval: float = 1.0,  # Intervalle de polling (secondes)
    host: str = "127.0.0.1",  # Adresse IP (X-Plane uniquement)
    port: int = 8086,         # Port (X-Plane uniquement)
    include_trajectory: bool = False,  # Ajouter LineString pour QGIS
    auto_connect: bool = True  # Mode de connexion (NOUVEAU)
) -> BaseSimulatorMonitor
```

### Types Disponibles

```python
from sim_monitor import SimulatorType, FlightState

SimulatorType.MSFS    # "msfs"    - Microsoft Flight Simulator
SimulatorType.XPLANE  # "xplane"  - X-Plane 12

FlightState.WAITING     # En attente du décollage
FlightState.IN_FLIGHT   # En vol (enregistrement actif)
FlightState.LANDED      # Atterrissage détecté
```

### Propriétés du Moniteur

| Propriété | Type | Description |
|-----------|------|-------------|
| `is_connected` | `bool` | État de la connexion au simulateur |
| `flight_state` | `FlightState` | État actuel du vol |
| `auto_connect` | `bool` | Mode de connexion configuré |
| `poll_interval` | `float` | Intervalle de polling (secondes) |

---

## 🔌 Modes de Connexion

### 🔄 Mode Automatique (`auto_connect=True` - **défaut**)

- La connexion est tentée **automatiquement** au démarrage du monitoring
- **Reconnexion automatique** en cas de perte de connexion
- Idéal pour les scripts autonomes

```python
monitor = create_monitor(
    simulator_type=SimulatorType.XPLANE.value,
    geojson_path="/data/vol.json",
    auto_connect=True  # Défaut
)
monitor.start_monitoring()  # Connexion automatique
```

### 🖱️ Mode Manuel (`auto_connect=False` - **pour GUI**)

- **Pas de connexion automatique** au démarrage
- L'utilisateur doit appeler `monitor.connect()` manuellement
- Permet un contrôle fin via l'interface graphique

```python
monitor = create_monitor(
    simulator_type=SimulatorType.XPLANE.value,
    geojson_path="/data/vol.json",
    auto_connect=False  # Mode manuel
)

def on_connection_change(connected: bool, message: str):
    print(f"Connexion: {connected} - {message}")
    # Mettre à jour l'UI ici

monitor.set_connection_callback(on_connection_change)
monitor.start_monitoring()

# Quand l'utilisateur clique sur "Se connecter" :
if monitor.connect():
    print("Connexion établie !")
else:
    print("Échec de la connexion")
```

### Comparaison des Modes

| Fonctionnalité | Mode Automatique | Mode Manuel |
|---------------|------------------|--------------|
| Connexion initiale | ✅ Automatique | ❌ Manuelle |
| Reconnexion après perte | ✅ Automatique | ❌ Manuelle |
| Contrôle via GUI | ❌ Non applicable | ✅ Recommandé |
| Utilisation en script | ✅ Idéal | ❌ Possible |
| Callback de statut | ✅ Oui | ✅ Oui |

---

## ✈️ Détection Automatique Décollage/Atterrissage

Le module détecte automatiquement les phases de vol pour **optimiser l'enregistrement** :

| Phase | Condition | Action |
|-------|-----------|--------|
| **Décollage** | GS > 30kt **ET** AGL > 0 pendant > 5s | ✅ Début de l'enregistrement |
| **En Vol** | Conditions de décollage maintenues | ✅ Enregistrement actif |
| **Atterrissage** | GS ≤ 30kt **ET** AGL ≈ 0 pendant > 5s | ❌ Arrêt de l'enregistrement |

### Seuils Configurables (dans `BaseSimulatorMonitor`)

```python
TAKEOFF_GS_THRESHOLD_KT = 30.0    # Vitesse sol (kt)
TAKEOFF_AGL_THRESHOLD_FT = 0.0    # Altitude AGL (pieds)
LANDING_GS_THRESHOLD_KT = 30.0     # Vitesse sol (kt)
LANDING_AGL_THRESHOLD_FT = 0.0     # Altitude AGL (pieds)
DETECTION_DURATION_SEC = 5.0       # Durée minimale (secondes)
```

### Utilisation

```python
monitor.start_monitoring()

# Vérifier l'état de vol
if monitor.flight_state == FlightState.IN_FLIGHT:
    print("En vol - Enregistrement actif")
elif monitor.flight_state == FlightState.WAITING:
    print("En attente du décollage")
else:
    print("Atterrissage détecté - Arrêt")
```

---

## 🏗️ Classes et Méthodes

---

### 📍 `GeoJSONWriter`

Gère l'écriture thread-safe des données au format GeoJSON (RFC 7946).

#### Constructeur

```python
writer = GeoJSONWriter(
    filepath: str,              # Chemin du fichier
    include_trajectory: bool = False  # Ajouter LineString
)
```

#### Méthodes

```python
writer.add_point(data: dict)  # Ajoute un point de mesure
```

---

### 🎮 `BaseSimulatorMonitor` (Classe Abstraite)

Classe de base pour tous les moniteurs.

#### Constructeur

```python
monitor = BaseSimulatorMonitor(
    geojson_path: str,           # Chemin du fichier GeoJSON
    poll_interval: float = 1.0,  # Intervalle de polling (s)
    include_trajectory: bool = False,
    auto_connect: bool = True    # Mode de connexion
)
```

#### Propriétés

```python
monitor.is_connected      # bool - État de la connexion
monitor.flight_state      # FlightState - État du vol
monitor.auto_connect      # bool - Mode de connexion
monitor.poll_interval     # float - Intervalle de polling
```

#### Méthodes Publiques

```python
monitor.connect() -> bool           # Établit la connexion (manuel)
monitor.disconnect()                # Ferme la connexion
monitor.start_monitoring()          # Démarre le monitoring
monitor.stop_monitoring()           # Arrête le monitoring
monitor.set_connection_callback(callback)  # Définit le callback
```

#### Méthodes Abstraites (implémentées par les enfants)

```python
monitor._do_connect() -> bool       # Connexion spécifique
monitor.get_data() -> dict          # Récupère les données
monitor.disconnect()                # Déconnexion spécifique
```

---

### 🪟 `MSFSMonitor` (MSFS 2020/2024 / P3D)

Moniteur pour **Microsoft Flight Simulator** via **SimConnect**.

#### Constructeur

```python
monitor = MSFSMonitor(
    geojson_path: str,
    poll_interval: float = 1.0,
    include_trajectory: bool = False,
    auto_connect: bool = True
)
```

#### Spécificités

- **Windows uniquement** (SimConnect est une API native Windows)
- Pas besoin de configurateur `host`/`port` (connexion locale via SimConnect)
- Supporte jusqu'à **4 moteurs** (MAX_ENGINES)

#### Données Récupérées

| Champ | Description | Unité | Format |
|-------|-------------|-------|--------|
| `latitude` | Latitude | ° | float (±90) |
| `longitude` | Longitude | ° | float (±180) |
| `sim_time` | Heure simulation | - | ISO 8601 |
| `alt_msl` | Altitude MSL | pieds | int |
| `alt_agl` | Altitude AGL | pieds | int |
| `heading_true` | Cap vrai | ° | float |
| `heading_mag` | Cap magnétique | ° | float |
| `ias` | Vitesse indiquée | kt | float |
| `gs` | Vitesse sol | kt | float |
| `power` | Puissance totale | HP | int |
| `acf_icao` | Code ICAO appareil | - | str |
| `acf_name` | Nom appareil | - | str |

---

### ✈️ `XPlaneMonitor` (X-Plane 12)

Moniteur pour **X-Plane 12** via **API REST**.

#### Constructeur

```python
monitor = XPlaneMonitor(
    geojson_path: str,
    host: str = "127.0.0.1",     # Adresse IP
    port: int = 8086,           # Port de l'API REST
    poll_interval: float = 1.0,
    include_trajectory: bool = False,
    auto_connect: bool = True
)
```

#### Spécificités

- **Multiplateforme** (via API REST)
- Nécessite l'activation du **plugin HTTP** dans X-Plane
- Port par défaut : **8086**

#### Datarefs Utilisées

| Dataref X-Plane | Champ | Conversion |
|----------------|-------|------------|
| `sim/flightmodel/position/latitude` | `latitude` | ° → float |
| `sim/flightmodel/position/longitude` | `longitude` | ° → float |
| `sim/time/zulu_time_sec` | `sim_time` | → ISO 8601 |
| `sim/flightmodel/position/elevation` | `alt_msl` | m → pieds |
| `sim/flightmodel/position/y_agl` | `alt_agl` | m → pieds |
| `sim/flightmodel/position/psi` | `heading_true` | rad → ° |
| `sim/flightmodel/position/mag_psi` | `heading_mag` | rad → ° |
| `sim/flightmodel/position/indicated_airspeed` | `ias` | m/s → kt |
| `sim/flightmodel/position/groundspeed` | `gs` | m/s → kt |
| `sim/flightmodel/engine/ENGN_power` | `power` | W → HP |
| `sim/aircraft/view/acf_ICAO` | `acf_icao` | - |
| `sim/aircraft/view/acf_descrip` | `acf_name` | - |

---

### 🏭 `check_simulator_available()`

Vérifie si un simulateur est disponible **sans démarrer le monitoring**.

```python
from sim_monitor import check_simulator_available, SimulatorType

# Vérifier X-Plane
if check_simulator_available(SimulatorType.XPLANE.value, host="127.0.0.1", port=8086):
    print("X-Plane est disponible !")

# Vérifier MSFS
if check_simulator_available(SimulatorType.MSFS.value):
    print("MSFS est disponible !")
```

---

## 📡 Messages de Callback

Le callback est appelé avec deux paramètres :
- `connected: bool` - État de la connexion
- `message: str` - Message décrivant l'événement

### Messages Standard

| Message | Signification | Quand ? |
|---------|---------------|---------|
| `"CONNECTED"` | Connexion établie avec succès | Après `monitor.connect()` |
| `"CONNECTED_WAITING_TAKEOFF"` | Connecté, en attente du décollage | Début du monitoring (mode auto) |
| `"WAITING_MANUAL_CONNECTION"` | Mode manuel, attente de connexion | Début du monitoring (mode manuel) |
| `"RECONNECTED"` | Reconnexion après perte | Réessai réussi (mode auto) |
| `"INITIAL_CONNECTION_FAILED"` | Échec de la connexion initiale | Démarrage du monitoring |
| `"CONNECTION_FAILED"` | Échec générique de connexion | Après `monitor.connect()` |
| `"DISCONNECTED"` | Déconnexion | Fin du monitoring |
| `"MONITORING_STOPPED"` | Monitoring arrêté | Après `stop_monitoring()` |
| `"TAKEOFF_DETECTED"` | Décollage détecté | Début de l'enregistrement |
| `"LANDING_DETECTED"` | Atterrissage détecté | Fin de l'enregistrement |
| `"DATA_RETRIEVAL_ERROR"` | Erreur de récupération des données | Dans la boucle de monitoring |

### Messages Spécifiques X-Plane

| Message | Signification |
|---------|---------------|
| `"XPLANE_CONNECTION_FAILED"` | Erreur de connexion à l'API X-Plane |
| `"REQUESTS_NOT_INSTALLED"` | La bibliothèque `requests` n'est pas installée |

### Messages Spécifiques MSFS

| Message | Signification |
|---------|---------------|
| `"SIMCONNECT_CONNECTION_FAILED"` | Erreur de connexion SimConnect |
| `"SIMCONNECT_NOT_INSTALLED"` | SimConnect n'est pas installé |

### Exemple d'Utilisation

```python
def on_connection_change(connected: bool, message: str):
    status = "✅" if connected else "❌"
    print(f"[{status}] {message}")

monitor.set_connection_callback(on_connection_change)
```

---

## 📝 Exemples Complets

---

### 🎯 Exemple 1 : Enregistrement Basique

```python
from fdr.sims_monitor.sim_monitor import create_monitor, SimulatorType

# Créer le moniteur
monitor = create_monitor(
    simulator_type=SimulatorType.XPLANE.value,
    geojson_path="/data/mon_vol.json",
    poll_interval=1.0
)

# Démarrer le monitoring
monitor.start_monitoring()

# ... vol en cours ...

# Arrêter le monitoring
monitor.stop_monitoring()
print("Données enregistrées dans /data/mon_vol.json")
```

---

### 🗺️ Exemple 2 : Avec Trajectoire pour QGIS

```python
from fdr.sims_monitor.sim_monitor import create_monitor, SimulatorType

monitor = create_monitor(
    simulator_type=SimulatorType.MSFS.value,
    geojson_path="/data/trajectoire.geojson",
    include_trajectory=True,  # Ajoute une LineString
    poll_interval=0.5        # Polling plus fréquent
)

monitor.start_monitoring()
# ... vol en cours ...
monitor.stop_monitoring()

# Le fichier contiendra :
# - Une Feature LineString (trajectoire complète)
# - Les Features Point individuelles (pour analyses)
```

---

### 🖥️ Exemple 3 : Intégration GUI (PyQt)

```python
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from fdr.sims_monitor.sim_monitor import create_monitor, SimulatorType, FlightState

class FlightMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AirRallies - Moniteur de Vol")
        self.setup_ui()

        # Créer le moniteur en mode manuel
        self.monitor = create_monitor(
            simulator_type=SimulatorType.XPLANE.value,
            geojson_path="/data/vol_gui.json",
            auto_connect=False  # Connexion manuelle
        )
        self.monitor.set_connection_callback(self.on_connection_change)

    def setup_ui(self):
        self.status_label = QLabel("Déconnecté")
        self.flight_state_label = QLabel("État: WAITING")

        self.btn_connect = QPushButton("Se connecter")
        self.btn_connect.clicked.connect(self.connect_simulator)

        self.btn_start = QPushButton("Démarrer Monitoring")
        self.btn_start.clicked.connect(self.start_monitoring)

        self.btn_stop = QPushButton("Arrêter Monitoring")
        self.btn_stop.clicked.connect(self.stop_monitoring)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.flight_state_label)
        layout.addWidget(self.btn_connect)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def connect_simulator(self):
        if self.monitor.connect():
            self.status_label.setText("Connecté")
        else:
            self.status_label.setText("Échec de la connexion")

    def start_monitoring(self):
        self.monitor.start_monitoring()

    def stop_monitoring(self):
        self.monitor.stop_monitoring()

    def on_connection_change(self, connected, message):
        self.status_label.setText(f"{'Connecté' if connected else 'Déconnecté'}: {message}")
        if connected:
            self.btn_connect.setEnabled(False)
        else:
            self.btn_connect.setEnabled(True)
        self.flight_state_label.setText(f"État: {self.monitor.flight_state.value}")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = FlightMonitorApp()
    window.show()
    sys.exit(app.exec_())
```

---

### 📊 Exemple 4 : Monitoring avec Statistiques

```python
from fdr.sims_monitor.sim_monitor import create_monitor, SimulatorType, FlightState
import time

class FlightStats:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.max_altitude = 0
        self.max_speed = 0
        self.points_count = 0

stats = FlightStats()

def on_connection_change(connected, message):
    global stats
    if connected and "TAKEOFF" in message:
        stats.start_time = time.time()
        print("✈️ Décollage détecté !")
    elif not connected and "LANDING" in message:
        stats.end_time = time.time()
        duration = stats.end_time - stats.start_time
        print(f"🛬 Atterrissage détecté après {duration:.1f} secondes")
        print(f"   Altitude max: {stats.max_altitude} pieds")
        print(f"   Vitesse max: {stats.max_speed} kt")
        print(f"   Points enregistrés: {stats.points_count}")

monitor = create_monitor(
    simulator_type=SimulatorType.XPLANE.value,
    geojson_path="/data/vol_stats.json",
    include_trajectory=True
)
monitor.set_connection_callback(on_connection_change)

# Personnaliser get_data pour collecter des stats
original_get_data = monitor.get_data
def custom_get_data():
    data = original_get_data()
    if data:
        alt = float(data.get("alt_msl", "0").replace("ft", "").replace(",", "").strip())
        speed = float(data.get("gs", "0").replace("kt", "").replace(",", "").strip())
        stats.max_altitude = max(stats.max_altitude, alt)
        stats.max_speed = max(stats.max_speed, speed)
        stats.points_count += 1
    return data

monitor.get_data = custom_get_data
monitor.start_monitoring()
```

---

### 🔍 Exemple 5 : Vérification de Disponibilité

```python
from fdr.sims_monitor.sim_monitor import check_simulator_available, SimulatorType, create_monitor

def detect_available_simulators():
    simulators = []

    # Vérifier X-Plane
    if check_simulator_available(SimulatorType.XPLANE.value, host="127.0.0.1", port=8086):
        simulators.append("X-Plane 12")

    # Vérifier MSFS
    if check_simulator_available(SimulatorType.MSFS.value):
        simulators.append("MSFS 2020/2024")

    return simulators

available = detect_available_simulators()
if available:
    print(f"Simulateurs disponibles: {', '.join(available)}")
    # Créer automatiquement un moniteur pour le premier disponible
    sim_type = SimulatorType.XPLANE.value if "X-Plane" in available[0] else SimulatorType.MSFS.value
    monitor = create_monitor(simulator_type=sim_type, geojson_path="/data/auto.json")
    monitor.start_monitoring()
else:
    print("Aucun simulateur disponible")
```

---

## 🌍 Conformité RFC 7946

Le module génère des fichiers **GeoJSON 100% conformes à la RFC 7946** :

### Structure du GeoJSON

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[lon1, lat1, alt1], [lon2, lat2, alt2], ...]
      },
      "properties": {
        "type": "trajectory",
        "point_count": 123,
        "acf_icao": "A320",
        "acf_name": "Airbus A320",
        "start_time": "2024-06-28T14:30:00 Z",
        "end_time": "2024-06-28T15:45:00 Z"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [lon, lat, alt]
      },
      "properties": {
        "sim_time": "2024-06-28T14:35:23 Z",
        "alt_msl_m": 10000.5,
        "alt_agl_m": 2500.0,
        "heading_true_deg": 45.5,
        "heading_mag_deg": 35.2,
        "ias_kt": 250.0,
        "gs_kt": 265.5,
        "power_hp": 15000.0,
        "acf_icao": "A320",
        "acf_name": "Airbus A320"
      }
    }
  ]
}
```

### Règles de Conformité Appliquées

| Règle RFC 7946 | Implémentation |
|---------------|----------------|
| Coordonnées : `[longitude, latitude]` ou `[longitude, latitude, altitude]` | ✅ Respecté |
| Altitude en **mètres** (WGS 84) | ✅ Converti depuis les pieds |
| Propriétés : valeurs **numériques** (pas de chaînes) | ✅ `alt_msl_m: 10000.5` |
| Valeurs manquantes : `null` (pas de chaînes comme "—") | ✅ Nettoyé avant écriture |
| Extensions : `.json` ou `.geojson` | ✅ Normalisé automatiquement |
| Encodage : UTF-8 | ✅ Spécifié à l'écriture |

### Extensions Valides

- `.json` (recommandé)
- `.geojson`

> ⚠️ **Note** : Si aucune extension n'est spécifiée, `.json` est ajouté automatiquement.

---

## ⚠️ Gestion des Erreurs

### Exceptions Levées

| Exception | Cause | Solution |
|-----------|-------|----------|
| `ValueError` | `geojson_path` vide | Spécifier un chemin valide |
| `ValueError` | `simulator_type` invalide | Utiliser `SimulatorType.MSFS.value` ou `SimulatorType.XPLANE.value` |
| `ImportError` | `requests` non installé (X-Plane) | `pip install requests` |
| `ImportError` | `SimConnect` non installé (MSFS) | `pip install SimConnect` (Windows) |
| `ConnectionError` | Simulateur non disponible | Vérifier que le simulateur est lancé |

### Messages d'Erreur Courants

| Message | Cause | Solution |
|---------|-------|----------|
| `"FILE_PATH_EMPTY"` | Chemin vide | `geojson_path="/data/vol.json"` |
| `"INITIAL_CONNECTION_FAILED"` | Connexion initiale échouée | Vérifier que le simulateur est lancé |
| `"SIMCONNECT_NOT_INSTALLED"` | SimConnect manquant | Windows + MSFS requis |
| `"REQUESTS_NOT_INSTALLED"` | Bibliothèque `requests` manquante | `pip install requests` |
| `"XPLANE_CONNECTION_FAILED"` | API X-Plane inaccessible | Vérifier l'IP/port et le plugin HTTP |
| `"DATAREF_NOT_FOUND"` | Dataref X-Plane introuvable | Vérifier la version de X-Plane |
| `"LATITUDE_MISSING"` / `"LONGITUDE_MISSING"` | Coordonnées invalides | Le simulateur ne fournit pas de position |
| `"UNKNOWN_SIMULATOR_TYPE"` | Type de simulateur invalide | Utiliser `"msfs"` ou `"xplane"` |

### Bonnes Pratiques de Gestion d'Erreurs

```python
from fdr.sims_monitor.sim_monitor import create_monitor, SimulatorType

try:
    monitor = create_monitor(
        simulator_type=SimulatorType.XPLANE.value,
        geojson_path="/data/vol.json"
    )

    def on_error(connected, message):
        if not connected:
            print(f"⚠️ Erreur: {message}")
            # Gérer l'erreur (afficher dans l'UI, logger, etc.)

    monitor.set_connection_callback(on_error)
    monitor.start_monitoring()

except ValueError as e:
    print(f"❌ Erreur de configuration: {e}")
except ImportError as e:
    print(f"❌ Dépendance manquante: {e}")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
```

---

## 📜 Annexes

---

### 📊 Diagramme de Classes

```
+---------------------+
|   BaseSimulatorMonitor |
+---------------------+
| - geojson_writer     |
| - poll_interval      |
| - _running           |
| - _connected         |
| - _auto_connect      |
| - _flight_state      |
+---------------------+
| + __init__()         |
| + connect()          |
| + disconnect()       |
| + start_monitoring() |
| + stop_monitoring()  |
| + set_connection...()|
+---------------------+
         ^
         |
+--------+--------+
|                 |
v                 v
+----------+   +------------+
| MSFS     |   | XPlane     |
| Monitor  |   | Monitor    |
+----------+   +------------+
| _do_connect() | | _do_connect() |
| get_data()    | | get_data()    |
| disconnect()  | | disconnect()  |
+----------+   +------------+
```

---

### 🔧 Configuration Recommandée

#### X-Plane 12

1. Activer le **plugin HTTP** dans X-Plane
2. Vérifier le **port** (par défaut : 8086)
3. Autoriser les connexions **locales** (127.0.0.1)

#### MSFS 2020/2024

1. **Windows uniquement** (SimConnect est une API native)
2. Installer `pip install SimConnect`
3. Lancer MSFS **avant** le script Python

#### P3D (Prepar3D)

- Même configuration que MSFS (SimConnect)

---

### 📁 Emplacement des Fichiers

- **Module** : `/home/laurent/AirRallies/fdr/sims_monitor/sim_monitor.py`
- **Traductions** : `/home/laurent/AirRallies/fdr/sims_monitor/translations.py`
- **Fichiers de sortie** : Spécifiés par `geojson_path` (ex: `/data/vol.json`)

---

### 🎓 Glossaire

| Terme | Définition |
|-------|------------|
| **AGL** | Above Ground Level - Altitude au-dessus du sol |
| **MSL** | Mean Sea Level - Altitude par rapport au niveau de la mer |
| **GS** | Ground Speed - Vitesse sol |
| **IAS** | Indicated Airspeed - Vitesse indiquée |
| **kt** | Knots - Nœuds (1 kt = 1.852 km/h) |
| **HP** | Horsepower - Cheval-vapeur |
| **WGS 84** | World Geodetic System 1984 - Système géodésique standard |
| **GeoJSON** | Format de données géospatiales basé sur JSON |
| **RFC 7946** | Standard définissant le format GeoJSON |
| **SimConnect** | API Microsoft pour communiquer avec MSFS/P3D |

---

### 📞 Support et Contributions

- **Auteurs** : Adapté des moniteurs originaux MSFS et X-Plane
- **Problèmes** : Vérifier les messages d'erreur et les logs
- **Contributions** : Les pull requests sont les bienvenues

---

**© 2024 AirRallies - Documentation générée pour le module sim_monitor**
