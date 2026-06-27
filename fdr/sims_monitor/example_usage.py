#!/usr/bin/env python3
"""
Exemple d'utilisation du module sim_monitor.

Ce script montre comment :
1. Créer un moniteur pour X-Plane ou MSFS
2. Configurer un callback pour l'état de connexion
3. Démarrer et arrêter le monitoring
4. Enregistrer les données dans un fichier GeoJSON

Usage:
    python example_usage.py xplane /tmp/flight_track.geojson
    python example_usage.py msfs /tmp/flight_track.geojson
"""

import sys
import time

# Ajouter le dossier parent au path si nécessaire
if __name__ == "__main__":
    from sims_monitor.sim_monitor import create_monitor, SimulatorType


def connection_callback(connected: bool, message: str) -> None:
    """Callback appelé lorsque l'état de connexion change."""
    status = "✓ CONNECTÉ" if connected else "✗ DÉCONNECTÉ"
    print(f"[{time.strftime('%H:%M:%S')}] {status}: {message}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python example_usage.py <simulator_type> <geojson_path>")
        print("  simulator_type: 'xplane' ou 'msfs'")
        print("  geojson_path: chemin vers le fichier GeoJSON de sortie")
        print("\nExemple:")
        print("  python example_usage.py xplane /tmp/flight_track.geojson")
        print("  python example_usage.py msfs C:/temp/flight_track.geojson")
        sys.exit(1)

    simulator_type = sys.argv[1].lower()
    geojson_path = sys.argv[2]

    # Paramètres optionnels pour X-Plane
    host = "127.0.0.1"
    port = 8086

    # Vérification des paramètres
    if simulator_type not in ["xplane", "msfs"]:
        print(f"Erreur: type de simulateur invalide: '{simulator_type}'")
        print("Utilisez 'xplane' ou 'msfs'")
        sys.exit(1)

    print(f"Démarrage du moniteur {simulator_type}...")
    print(f"Fichier GeoJSON: {geojson_path}")
    print("Appuyez sur Ctrl+C pour arrêter...")
    print("-" * 60)

    try:
        # Créer le moniteur
        monitor = create_monitor(
            simulator_type=simulator_type,
            geojson_path=geojson_path,
            poll_interval=1.0,
            host=host,
            port=port
        )

        # Configurer le callback de connexion
        monitor.set_connection_callback(connection_callback)

        # Démarrer le monitoring
        monitor.start_monitoring()

        # Attendre que l'utilisateur arrête avec Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nArrêt demandé par l'utilisateur...")

        # Arrêter proprement
        monitor.stop_monitoring()
        print(f"Données enregistrées dans: {geojson_path}")
        print("Au revoir!")

    except ValueError as e:
        print(f"Erreur: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
