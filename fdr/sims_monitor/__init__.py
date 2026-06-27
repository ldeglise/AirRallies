"""
Package sims_monitor - Moniteurs de simulateurs de vol unifiés

Ce package fournit des classes pour se connecter à MSFS/P3D ou X-Plane 12
et enregistrer les données de vol dans un fichier GeoJSON.

Modules:
    sim_monitor: Module principal avec les classes de monitoring

Exemple d'utilisation:
    from sims_monitor.sim_monitor import create_monitor, SimulatorType
    
    monitor = create_monitor(
        simulator_type=SimulatorType.XPLANE.value,
        geojson_path="/chemin/vers/track.geojson"
    )
    monitor.start_monitoring()
"""

from .sim_monitor import (
    BaseSimulatorMonitor,
    MSFSMonitor,
    XPlaneMonitor,
    SimulatorType,
    GeoJSONWriter,
    create_monitor,
    check_simulator_available,
)

__all__ = [
    "BaseSimulatorMonitor",
    "MSFSMonitor", 
    "XPlaneMonitor",
    "SimulatorType",
    "GeoJSONWriter",
    "create_monitor",
    "check_simulator_available",
]
