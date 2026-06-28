"""
Package sims_monitor - Module unifié pour MSFS/P3D et X-Plane 12.

Ce package fournit des outils pour enregistrer les données de vol en temps réel
dans un fichier GeoJSON (RFC 7946) avec détection automatique du décollage et
de l'atterrissage.

Utilisation :
    from sims_monitor import create_monitor, SimulatorType, FlightState
    from sims_monitor.translations import set_language, gettext as _
    
    # Définir la langue (optionnel, par défaut utilise la langue du système)
    set_language("en")  # Anglais
    set_language("fr")  # Français
    
    # Créer un moniteur
    monitor = create_monitor(
        simulator_type=SimulatorType.XPLANE.value,
        geojson_path="/chemin/vers/fichier.json",
        poll_interval=1.0
    )
    
    # Définir un callback pour les notifications
    monitor.set_connection_callback(lambda connected, msg: print(f"{msg}"))
    
    # Démarrer le monitoring
    monitor.start_monitoring()
    
    # ... plus tard ...
    monitor.stop_monitoring()

Fonctionnalités :
    - Détection automatique du décollage et atterrissage
    - Support de MSFS 2020/2024/P3D via SimConnect
    - Support de X-Plane 12 via API REST
    - Export GeoJSON conforme RFC 7946
    - Support de l'internationalisation (i18n)
"""

# Exporter les classes et fonctions principales depuis sim_monitor
from .sim_monitor import (
    BaseSimulatorMonitor,
    MSFSMonitor,
    XPlaneMonitor,
    SimulatorType,
    FlightState,
    GeoJSONWriter,
    create_monitor,
    check_simulator_available,
)

# Exporter les fonctions de traduction depuis translations
from .translations import (
    gettext as _,
    set_language,
    get_language,
    TranslationManager,
)

__all__ = [
    # Moniteurs
    "BaseSimulatorMonitor",
    "MSFSMonitor", 
    "XPlaneMonitor",
    # Types
    "SimulatorType",
    "FlightState",
    # Writer GeoJSON
    "GeoJSONWriter",
    # Factory
    "create_monitor",
    "check_simulator_available",
    # Traductions
    "_",
    "set_language",
    "get_language",
    "TranslationManager",
]

__version__ = "1.0.0"
