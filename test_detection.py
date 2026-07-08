#!/usr/bin/env python3
"""
Test script pour vérifier que la détection de décollage/atterrissage fonctionne
"""

import sys
import os

# Ajouter le répertoire fdr au path
fdr_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fdr'))
sys.path.insert(0, fdr_path)

from sims_monitor.sim_monitor import create_monitor, SimulatorType, FlightState
from datetime import datetime, timezone, timedelta
import time

# Créer un mock de data pour simuler un décollage
class MockXPlaneMonitor:
    def __init__(self):
        from sims_monitor.sim_monitor import BaseSimulatorMonitor
        # N'utilisons pas vraiment BaseSimulatorMonitor, juste pour tester la logique
        self._flight_state = FlightState.WAITING
        self._data_history = []
        self.TAKEOFF_GS_THRESHOLD_KT = 30.0
        self.TAKEOFF_AGL_THRESHOLD_FT = 0.0
        self.LANDING_GS_THRESHOLD_KT = 30.0
        self.LANDING_AGL_THRESHOLD_FT = 0.0
        self.DETECTION_DURATION_SEC = 5.0
    
    def _parse_gs_kt(self, data):
        """Extrait GS depuis des données mock"""
        return data.get("gs_kt")
    
    def _parse_alt_agl_ft(self, data):
        """Extrait AGL depuis des données mock"""
        return data.get("alt_agl_ft")
    
    def _clean_old_history(self, now):
        """Nettoie l'historique"""
        cutoff = now - timedelta(seconds=self.DETECTION_DURATION_SEC)
        self._data_history = [(gs, agl, ts) for gs, agl, ts in self._data_history if ts >= cutoff]
    
    def _check_takeoff_condition(self):
        """Vérifie conditions de décollage"""
        if len(self._data_history) < 2:
            return False
        
        agl_tolerance_ft = 0.1
        
        for gs_kt, alt_agl_ft, _ in self._data_history:
            if gs_kt is None or alt_agl_ft is None:
                print(f"    DEBUG: Found None in history: gs_kt={gs_kt}, alt_agl_ft={alt_agl_ft}")
                return False
            if gs_kt <= self.TAKEOFF_GS_THRESHOLD_KT or alt_agl_ft <= self.TAKEOFF_AGL_THRESHOLD_FT - agl_tolerance_ft:
                print(f"    DEBUG: Condition failed: gs_kt={gs_kt} <= {self.TAKEOFF_GS_THRESHOLD_KT} OR alt_agl_ft={alt_agl_ft} <= {self.TAKEOFF_AGL_THRESHOLD_FT - agl_tolerance_ft}")
                return False
        
        first_time = self._data_history[0][2]
        last_time = self._data_history[-1][2]
        duration = (last_time - first_time).total_seconds()
        print(f"    DEBUG: History duration: {duration:.1f}s (need {self.DETECTION_DURATION_SEC}s), history_count={len(self._data_history)}")
        return duration >= self.DETECTION_DURATION_SEC
    
    def _check_landing_condition(self):
        """Vérifie conditions d'atterrissage"""
        if len(self._data_history) < 2:
            return False
        
        agl_tolerance_ft = 0.5
        
        for gs_kt, alt_agl_ft, _ in self._data_history:
            if gs_kt is None or alt_agl_ft is None:
                return False
            if gs_kt > self.LANDING_GS_THRESHOLD_KT or abs(alt_agl_ft) > agl_tolerance_ft:
                return False
        
        first_time = self._data_history[0][2]
        last_time = self._data_history[-1][2]
        duration = (last_time - first_time).total_seconds()
        return duration >= self.DETECTION_DURATION_SEC
    
    def _update_flight_state(self, data):
        """Met à jour l'état de vol (NOUVELLE VERSION)"""
        now = datetime.now(timezone.utc)
        
        # Extraire GS et AGL
        gs_kt = self._parse_gs_kt(data)
        alt_agl_ft = self._parse_alt_agl_ft(data)
        
        # Si les données nécessaires sont manquantes, on ne peut pas faire de détection fiable
        # Si on est déjà en vol, continuer à enregistrer ce point
        # Sinon, ignorer ce point (ne pas enregistrer et ne pas mettre à jour l'état)
        if gs_kt is None or alt_agl_ft is None:
            return self._flight_state == FlightState.IN_FLIGHT
        
        # Ajouter à l'historique (seulement si les données sont valides)
        self._data_history.append((gs_kt, alt_agl_ft, now))
        
        # Nettoyer l'historique
        self._clean_old_history(now)
        
        # Vérifier les conditions selon l'état actuel
        if self._flight_state == FlightState.WAITING:
            if self._check_takeoff_condition():
                self._flight_state = FlightState.IN_FLIGHT
                print(f"[{now}] DÉCOLLAGE DÉTECTÉ!")
                return True
            return False
            
        elif self._flight_state == FlightState.IN_FLIGHT:
            if self._check_landing_condition():
                self._flight_state = FlightState.LANDED
                print(f"[{now}] ATTERRISSAGE DÉTECTÉ!")
                return False
            return True
            
        elif self._flight_state == FlightState.LANDED:
            return False
        
        return self._flight_state == FlightState.IN_FLIGHT


def test_detection():
    print("Test de détection de décollage/atterrissage")
    print("=" * 50)
    
    mock = MockXPlaneMonitor()
    
    # Simuler des données au sol (GS=0, AGL=0) - devrait rester en WAITING
    print("\n1. Au sol (GS=0, AGL=0):")
    mock._data_history.clear()  # Réinitialiser l'historique
    for i in range(10):
        data = {"gs_kt": 0.0, "alt_agl_ft": 0.0}
        should_record = mock._update_flight_state(data)
        time.sleep(0.1)
        print(f"   Point {i+1}: flight_state={mock._flight_state.value}, should_record={should_record}")
    
    print(f"\n   État après données au sol: {mock._flight_state.value}")
    
    # Simuler le roulage (GS=20, AGL=0) - devrait rester en WAITING
    print("\n2. Roulage (GS=20, AGL=0):")
    mock._data_history.clear()  # Réinitialiser l'historique
    for i in range(10):
        data = {"gs_kt": 20.0, "alt_agl_ft": 0.0}
        should_record = mock._update_flight_state(data)
        time.sleep(0.1)
        print(f"   Point {i+1}: flight_state={mock._flight_state.value}, should_record={should_record}")
    
    print(f"\n   État après roulage: {mock._flight_state.value}")
    
    # Simuler le décollage (GS=50, AGL=10) pendant plus de 5 secondes
    print("\n3. Décollage (GS=50, AGL=10) pendant 6 secondes:")
    mock._data_history.clear()  # Réinitialiser l'historique
    mock._flight_state = FlightState.WAITING  # Réinitialiser l'état
    for i in range(60):
        data = {"gs_kt": 50.0, "alt_agl_ft": 10.0}
        should_record = mock._update_flight_state(data)
        time.sleep(0.1)
        if i % 10 == 0:
            print(f"   Point {i+1}: flight_state={mock._flight_state.value}, should_record={should_record}")
    
    print(f"\n   État après décollage: {mock._flight_state.value}")
    
    # Simuler le vol (GS=100, AGL=5000) - devrait enregistrer
    print("\n4. En vol (GS=100, AGL=5000):")
    for i in range(5):
        data = {"gs_kt": 100.0, "alt_agl_ft": 5000.0}
        should_record = mock._update_flight_state(data)
        time.sleep(0.1)
        print(f"   Point {i+1}: flight_state={mock._flight_state.value}, should_record={should_record}")
    
    # Simuler l'approche (GS=50, AGL=100) - devrait toujours enregistrer
    print("\n5. Approche (GS=50, AGL=100):")
    for i in range(5):
        data = {"gs_kt": 50.0, "alt_agl_ft": 100.0}
        should_record = mock._update_flight_state(data)
        time.sleep(0.1)
        print(f"   Point {i+1}: flight_state={mock._flight_state.value}, should_record={should_record}")
    
    # Simuler l'atterrissage (GS=0, AGL=0) pendant plus de 5 secondes
    print("\n6. Atterrissage (GS=0, AGL=0) pendant 6 secondes:")
    mock._data_history.clear()  # Réinitialiser l'historique pour le test d'atterrissage
    for i in range(60):
        data = {"gs_kt": 0.0, "alt_agl_ft": 0.0}
        should_record = mock._update_flight_state(data)
        time.sleep(0.1)
        if i % 10 == 0:
            print(f"   Point {i+1}: flight_state={mock._flight_state.value}, should_record={should_record}")
    
    print(f"\n   État après atterrissage: {mock._flight_state.value}")
    
    # Essayons de voler à nouveau
    print("\n7. Vol à nouveau (GS=60, AGL=100):")
    mock._data_history.clear()  # Réinitialiser l'historique
    for i in range(5):
        data = {"gs_kt": 60.0, "alt_agl_ft": 100.0}
        should_record = mock._update_flight_state(data)
        time.sleep(0.1)
        print(f"   Point {i+1}: flight_state={mock._flight_state.value}, should_record={should_record}")
    
    print(f"\n   État final: {mock._flight_state.value}")


if __name__ == "__main__":
    test_detection()
