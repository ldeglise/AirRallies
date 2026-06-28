"""
Simulator Monitor - Module unifié pour MSFS/P3D et X-Plane 12
Enregistre les données de vol en temps réel dans un fichier GeoJSON (RFC 7946).

Utilisation :
    from sim_monitor import create_monitor, SimulatorType, FlightState
    
    # Version basique : uniquement des Points (pour analyses)
    monitor = create_monitor(
        simulator_type=SimulatorType.XPLANE.value,
        geojson_path="/chemin/vers/fichier.json",
        poll_interval=1.0,
        host="127.0.0.1",
        port=8086
    )
    
    # Version avec trajectoire : Points + LineString (pour QGIS)
    monitor = create_monitor(
        simulator_type=SimulatorType.XPLANE.value,
        geojson_path="/chemin/vers/trajectoire.geojson",
        poll_interval=1.0,
        include_trajectory=True  # Ajoute une LineString pour visualisation
    )
    
    monitor.set_connection_callback(lambda connected, msg: print(f"Statut: {connected}, {msg}"))
    monitor.start_monitoring()
    
    # ... plus tard ...
    monitor.stop_monitoring()

Dépendances :
    - Pour X-Plane : pip install requests
    - Pour MSFS/P3D : pip install SimConnect (Windows uniquement)

Notes :
    - Les extensions .json et .geojson sont toutes deux conformes à la RFC 7946.
    - Avec include_trajectory=True, le GeoJSON contient :
      * Une Feature LineString (trajectoire complète)
      * Les Features Point individuelles (pour analyses)
    - Sans include_trajectory (défaut), seul les Points sont enregistrés.
    
    Détection automatique décollage/atterrissage:
    - L'enregistrement commence automatiquement au décollage (GS > 30kt ET AGL > 0 pendant > 5s)
    - L'enregistrement s'arrête automatiquement à l'atterrissage (GS <= 30kt ET AGL = 0 pendant > 5s)
    - Utilise monitor.flight_state pour connaître l'état actuel (WAITING, IN_FLIGHT, LANDED)

Auteurs : Adapté des moniteurs originaux MSFS et X-Plane
"""

import json
import os
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional, Deque

# Import des fonctions de traduction
from .translations import gettext as _, set_language, get_language

# ---------------------------------------------------------------------------
# Types et constantes
# ---------------------------------------------------------------------------

class SimulatorType(Enum):
    """Types de simulateurs supportés."""
    MSFS = "msfs"
    XPLANE = "xplane"


class FlightState(Enum):
    """États de vol pour la détection décollage/atterrissage."""
    WAITING = "waiting"      # En attente du décollage
    IN_FLIGHT = "in_flight"  # En vol (enregistrement actif)
    LANDED = "landed"        # Atterrissage détecté (arrêt enregistrement)


# Constantes de conversion
M_TO_FT = 3.28084
MPS_TO_KT = 1.94384
W_TO_HP = 0.00134102
FT_LB_PER_S_TO_HP = 550.0

# J2000 epoch pour MSFS (1er janvier 2000 à 12h00 UTC)
J2000_EPOCH = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

# ---------------------------------------------------------------------------
# Writer GeoJSON Thread-Safe
# ---------------------------------------------------------------------------

class GeoJSONWriter:
    """
    Gère l'écriture des points de mesure au format GeoJSON conforme RFC 7946.
    Thread-safe pour utilisation avec plusieurs threads.
    
    Conformité RFC 7946:
    - Coordonnées : [longitude, latitude] ou [longitude, latitude, altitude]
    - Altitude en mètres (WGS 84)
    - Propriétés : valeurs numériques sans unités (unités documentées séparément)
    - Valeurs manquantes : null (pas de chaînes comme "—")
    - Extensions supportées : .json (recommandé) ou .geojson
    """
    
    # Extensions valides selon RFC 7946
    VALID_EXTENSIONS = (".json", ".geojson")

    def __init__(self, filepath: str, include_trajectory: bool = False):
        """
        Args:
            filepath: Chemin complet vers le fichier de sortie.
                     Accepte .json ou .geojson (RFC 7946).
                     Si aucune extension ou extension invalide, .json est ajouté.
            include_trajectory: Si True, ajoute une LineString connectant 
                               tous les points pour une meilleure visualisation 
                               dans QGIS (défaut: False pour rétrocompatibilité).
        
        Raises:
            ValueError: Si le chemin est vide ou invalide.
        """
        if not filepath:
            raise ValueError(_("Le chemin du fichier ne peut pas être vide"))
        
        # Normaliser le chemin et vérifier l'extension
        self.filepath = self._normalize_filepath(filepath)
        
        self._features = []
        self._trajectory_coords = []  # Coordonnées pour la LineString
        self._include_trajectory = include_trajectory
        self._lock = threading.Lock()
        
        # Créer le dossier parent s'il n'existe pas
        dirname = os.path.dirname(self.filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        
        # Écrire l'en-tête initial
        self._write_all()
    
    def _normalize_filepath(self, filepath: str) -> str:
        """
        Normalise le chemin du fichier pour s'assurer qu'il a une extension valide.
        Si le fichier n'a pas d'extension ou a une extension invalide, 
        remplace/ajoute .json par défaut.
        Normalise l'extension en minuscules pour cohérence.
        
        Args:
            filepath: Chemin à normaliser
            
        Returns:
            Chemin avec extension valide (.json ou .geojson en minuscules)
        """
        # Séparer le chemin et l'extension
        base, ext = os.path.splitext(filepath)
        
        # Normaliser l'extension en minuscules
        ext_lower = ext.lower()
        
        # Si pas d'extension ou extension invalide, utiliser .json par défaut
        if not ext or ext_lower not in self.VALID_EXTENSIONS:
            # Si pas d'extension du tout, ajouter .json
            if not ext:
                return f"{filepath}.json"
            # Sinon, remplacer l'extension invalide par .json
            else:
                return f"{base}.json"
        
        # Sinon, retourner avec extension en minuscules
        return f"{base}{ext_lower}"

    def _write_all(self):
        """Écrit le fichier GeoJSON complet avec points et éventuellement la trajectoire."""
        features = self._features.copy()
        
        # Ajouter la LineString de trajectoire en premier si activé
        if self._include_trajectory and len(self._trajectory_coords) >= 2:
            trajectory_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": self._trajectory_coords
                },
                "properties": {
                    "type": "trajectory",
                    "point_count": len(self._trajectory_coords),
                    "acf_icao": self._features[-1]["properties"].get("acf_icao") if self._features else None,
                    "acf_name": self._features[-1]["properties"].get("acf_name") if self._features else None,
                    "start_time": self._features[0]["properties"].get("sim_time") if self._features else None,
                    "end_time": self._features[-1]["properties"].get("sim_time") if self._features else None
                }
            }
            features.insert(0, trajectory_feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False, allow_nan=False)

    def add_point(self, data: dict) -> None:
        """
        Ajoute un point de mesure au GeoJSON en conformité RFC 7946.
        
        Args:
            data: Dictionnaire contenant les données du simulateur
        """
        with self._lock:
            # Extraire et valider les coordonnées
            lat_raw = data.get("latitude")
            lon_raw = data.get("longitude")
            alt_raw = data.get("alt_msl")
            
            # Parser et valider latitude [-90, 90]
            try:
                lat_float = self._parse_latitude(lat_raw)
            except ValueError:
                # Coordonnée invalide -> ignorer ce point
                return
            
            # Parser et valider longitude [-180, 180]
            try:
                lon_float = self._parse_longitude(lon_raw)
            except ValueError:
                return
            
            # Parser altitude (pieds -> mètres) - peut être None
            alt_m = self._parse_altitude_m(alt_raw)
            
            # Construire les coordonnées RFC 7946
            # 2D si altitude inconnue, 3D sinon
            if alt_m is not None:
                coordinates = [lon_float, lat_float, alt_m]
            else:
                coordinates = [lon_float, lat_float]

            # Créer la feature avec propriétés numériques (RFC 7946 compliant)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": coordinates
                },
                "properties": self._build_rfc7946_properties(data)
            }

            self._features.append(feature)
            
            # Ajouter les coordonnées à la trajectoire si activé
            if self._include_trajectory:
                if alt_m is not None:
                    self._trajectory_coords.append([lon_float, lat_float, alt_m])
                else:
                    self._trajectory_coords.append([lon_float, lat_float])

            # Réécrire le fichier complet (avec trajectoire si activée)
            self._write_all()

    def _parse_latitude(self, value) -> float:
        """Parse et valide la latitude. RFC 7946 : doit être entre -90 et 90."""
        if value is None or value == "—":
            raise ValueError(_("Latitude manquante"))
        try:
            clean = str(value).replace('°', '').strip()
            result = float(clean)
        except (ValueError, TypeError):
            raise ValueError(_("Latitude invalide: {value}", value=value))
        if not (-90 <= result <= 90):
            raise ValueError(_("Latitude hors plage: {result} (doit être entre -90 et 90)", result=result))
        return result

    def _parse_longitude(self, value) -> float:
        """Parse et valide la longitude. RFC 7946 : doit être entre -180 et 180."""
        if value is None or value == "—":
            raise ValueError(_("Longitude manquante"))
        try:
            clean = str(value).replace('°', '').strip()
            result = float(clean)
        except (ValueError, TypeError):
            raise ValueError(_("Longitude invalide: {value}", value=value))
        if not (-180 <= result <= 180):
            raise ValueError(_("Longitude hors plage: {result} (doit être entre -180 et 180)", result=result))
        return result

    def _parse_altitude_m(self, value) -> Optional[float]:
        """Parse l'altitude en pieds et convertit en mètres (WGS 84).
        Retourne None si l'altitude est manquante ou invalide."""
        if value is None or value == "—":
            return None
        try:
            # Nettoyer : enlever 'ft', virgules, espaces
            clean = str(value).replace('ft', '').replace(',', '').strip()
            if not clean:
                return None
            alt_ft = float(clean)
            return alt_ft / M_TO_FT  # Convertir en mètres
        except (ValueError, TypeError):
            return None

    def _parse_numeric_value(self, value, unit: str = "") -> Optional[float]:
        """Parse une valeur numérique depuis une chaîne formatée.
        Gère les unités (kt, hp, ft, °) et les virgules comme séparateurs de milliers."""
        if value is None or value == "—":
            return None
        try:
            # Nettoyer la chaîne : enlever unités et virgules
            clean = str(value)
            for u in [unit, 'ft', 'kt', 'hp', '°', ',']:
                clean = clean.replace(u, '').strip()
            if not clean:
                return None
            return float(clean)
        except (ValueError, TypeError):
            return None

    def _build_rfc7946_properties(self, data: dict) -> dict:
        """Construire les propriétés conformes RFC 7946.
        
        Tous les valeurs numériques sont stockées comme des nombres (pas de chaînes).
        Les valeurs manquantes sont null (pas de chaînes comme "—").
        Les unités sont documentées dans les noms de propriétés ou séparément.
        """
        props = {}
        
        # Timestamp - toujours présent
        sim_time = data.get("sim_time")
        if sim_time and sim_time != "—":
            props["sim_time"] = str(sim_time)
        else:
            props["sim_time"] = datetime.now(timezone.utc).isoformat()
        
        # Altitudes en mètres (WGS 84)
        props["alt_msl_m"] = self._parse_altitude_m(data.get("alt_msl"))
        props["alt_agl_m"] = self._parse_altitude_m(data.get("alt_agl"))
        
        # Caps en degrés
        props["heading_true_deg"] = self._parse_numeric_value(data.get("heading_true"), "°")
        props["heading_mag_deg"] = self._parse_numeric_value(data.get("heading_mag"), "°")
        
        # Vitesses en kt
        props["ias_kt"] = self._parse_numeric_value(data.get("ias"), "kt")
        props["gs_kt"] = self._parse_numeric_value(data.get("gs"), "kt")
        
        # Puissance en hp
        props["power_hp"] = self._parse_numeric_value(data.get("power"), "hp")
        
        # Appareil (chaînes)
        props["acf_icao"] = data.get("acf_icao") or None
        props["acf_name"] = data.get("acf_name") or None
        
        # Nettoyer : supprimer les clés avec valeur None
        return {k: v for k, v in props.items() if v is not None}

# ---------------------------------------------------------------------------
# Interface de base pour les moniteurs
# ---------------------------------------------------------------------------

class BaseSimulatorMonitor(ABC):
    """
    Classe de base abstraite pour les moniteurs de simulateur.
    
    Fournit une interface unifiée pour la connexion, la déconnexion,
    et la récupération des données de vol.
    
    Détection automatique du décollage et atterrissage:
    - Décollage: GS > 30kt ET altitude AGL > 0 pendant > 5 secondes
    - Atterrissage: GS <= 30kt ET altitude AGL = 0 pendant > 5 secondes
    """

    # Critères de détection (en unités simulation: kt et pieds)
    TAKEOFF_GS_THRESHOLD_KT = 30.0
    TAKEOFF_AGL_THRESHOLD_FT = 0.0
    LANDING_GS_THRESHOLD_KT = 30.0
    LANDING_AGL_THRESHOLD_FT = 0.0
    DETECTION_DURATION_SEC = 5.0

    def __init__(self, geojson_path: str, poll_interval: float = 1.0, include_trajectory: bool = False):
        """
        Args:
            geojson_path: Chemin vers le fichier de sortie.
                         Accepte .json ou .geojson (RFC 7946).
                         Si aucune extension, .json est ajouté automatiquement.
            poll_interval: Intervalle de polling en secondes (default: 1.0)
            include_trajectory: Si True, ajoute une LineString pour visualiser 
                               la trajectoire dans QGIS (défaut: False).
        """
        self.geojson_writer = GeoJSONWriter(geojson_path, include_trajectory)
        self.poll_interval = poll_interval
        self._running = False
        self._connected = False
        self._connection_callback: Optional[Callable[[bool, str], None]] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # État de vol pour détection décollage/atterrissage
        self._flight_state = FlightState.WAITING
        
        # Historique des données pour détection sur durée
        # Chaque entrée: (gs_kt, alt_agl_ft, timestamp)
        self._data_history: Deque[tuple[float, float, datetime]] = Deque()
        
        # Durée minimale pour la détection (en secondes)
        self._detection_duration = self.DETECTION_DURATION_SEC

    @abstractmethod
    def connect(self) -> bool:
        """
        Établit la connexion au simulateur.
        
        Returns:
            True si la connexion a réussi, False sinon
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Ferme la connexion au simulateur."""
        pass

    @abstractmethod
    def get_data(self) -> dict:
        """
        Récupère les données actuelles du simulateur.
        
        Returns:
            Dictionnaire contenant les données de vol
        """
        pass

    @property
    def is_connected(self) -> bool:
        """Retourne True si connecté au simulateur."""
        return self._connected

    def set_connection_callback(self, callback: Callable[[bool, str], None]) -> None:
        """
        Définit un callback pour les changements de statut de connexion.
        
        Args:
            callback: Fonction appelée avec (is_connected: bool, message: str)
        """
        self._connection_callback = callback

    @property
    def flight_state(self) -> FlightState:
        """Retourne l'état de vol actuel."""
        return self._flight_state

    def _parse_gs_kt(self, data: dict) -> Optional[float]:
        """Extrait la vitesse sol (GS) en kt depuis les données."""
        gs_raw = data.get("gs")
        if gs_raw is None or gs_raw == "—":
            return None
        try:
            clean = str(gs_raw).replace('kt', '').replace(',', '').strip()
            if clean:
                return float(clean)
        except (ValueError, TypeError):
            pass
        return None

    def _parse_alt_agl_ft(self, data: dict) -> Optional[float]:
        """Extrait l'altitude AGL en pieds depuis les données."""
        alt_agl_raw = data.get("alt_agl")
        if alt_agl_raw is None or alt_agl_raw == "—":
            return None
        try:
            clean = str(alt_agl_raw).replace('ft', '').replace(',', '').strip()
            if clean:
                return float(clean)
        except (ValueError, TypeError):
            pass
        return None

    def _update_flight_state(self, data: dict) -> bool:
        """
        Met à jour l'état de vol et vérifie si on doit enregistrer le point.
        
        Args:
            data: Dictionnaire des données du simulateur
            
        Returns:
            True si le point doit être enregistré, False sinon
        """
        now = datetime.now(timezone.utc)
        
        # Extraire GS et AGL
        gs_kt = self._parse_gs_kt(data)
        alt_agl_ft = self._parse_alt_agl_ft(data)
        
        # Si on ne peut pas extraire les données nécessaires, on garde l'état actuel
        if gs_kt is None or alt_agl_ft is None:
            # Nettoyer l'historique trop vieux
            self._clean_old_history(now)
            return self._flight_state == FlightState.IN_FLIGHT
        
        # Ajouter à l'historique
        self._data_history.append((gs_kt, alt_agl_ft, now))
        
        # Nettoyer l'historique (garder seulement les données des dernières DETECTION_DURATION_SEC)
        self._clean_old_history(now)
        
        # Vérifier les conditions selon l'état actuel
        if self._flight_state == FlightState.WAITING:
            # Vérifier si conditions de décollage sont remplies
            if self._check_takeoff_condition():
                self._flight_state = FlightState.IN_FLIGHT
                self._notify_connection_status(
                    True, 
                    _("Décollage détecté - Enregistrement démarré")
                )
                return True  # Enregistrer ce point
            return False
            
        elif self._flight_state == FlightState.IN_FLIGHT:
            # Vérifier si conditions d'atterrissage sont remplies
            if self._check_landing_condition():
                self._flight_state = FlightState.LANDED
                self._notify_connection_status(
                    True,
                    _("Atterrissage détecté - Enregistrement arrêté")
                )
                return False  # Ne pas enregistrer
            return True  # Enregistrer
            
        elif self._flight_state == FlightState.LANDED:
            # Plus d'enregistrement une fois atterri
            return False
        
        return self._flight_state == FlightState.IN_FLIGHT

    def _clean_old_history(self, now: datetime) -> None:
        """Nettoie l'historique des données trop anciennes."""
        cutoff = now - timedelta(seconds=self._detection_duration)
        while self._data_history and self._data_history[0][2] < cutoff:
            self._data_history.popleft()

    def _check_takeoff_condition(self) -> bool:
        """
        Vérifie si les conditions de décollage sont remplies:
        GS > 30kt ET altitude AGL > 0 pendant > 5 secondes.
        """
        if len(self._data_history) < 2:
            return False
        
        # Tolérance pour les comparaisons de flottants
        agl_tolerance_ft = 1.0  # 1 pied de tolérance
        
        # Vérifier que TOUTES les entrées de l'historique remplissent les conditions
        for gs_kt, alt_agl_ft, _ in self._data_history:
            if gs_kt <= self.TAKEOFF_GS_THRESHOLD_KT or alt_agl_ft <= self.TAKEOFF_AGL_THRESHOLD_FT + agl_tolerance_ft:
                return False
        
        # Vérifier que la durée couverte par l'historique est >= DETECTION_DURATION_SEC
        first_time = self._data_history[0][2]
        last_time = self._data_history[-1][2]
        duration = (last_time - first_time).total_seconds()
        return duration >= self._detection_duration

    def _check_landing_condition(self) -> bool:
        """
        Vérifie si les conditions d'atterrissage sont remplies:
        GS <= 30kt ET altitude AGL = 0 pendant > 5 secondes.
        """
        if len(self._data_history) < 2:
            return False
        
        # Tolérance pour les comparaisons de flottants
        agl_tolerance_ft = 1.0  # 1 pied de tolérance
        
        # Vérifier que TOUTES les entrées de l'historique remplissent les conditions
        for gs_kt, alt_agl_ft, _ in self._data_history:
            if gs_kt > self.LANDING_GS_THRESHOLD_KT or abs(alt_agl_ft) > agl_tolerance_ft:
                return False
        
        # Vérifier que la durée couverte par l'historique est >= DETECTION_DURATION_SEC
        first_time = self._data_history[0][2]
        last_time = self._data_history[-1][2]
        duration = (last_time - first_time).total_seconds()
        return duration >= self._detection_duration

    def _notify_connection_status(self, connected: bool, message: str) -> None:
        """
        Notifie le callback de changement de statut de connexion.
        Thread-safe.
        """
        with self._lock:
            self._connected = connected
            if self._connection_callback:
                try:
                    self._connection_callback(connected, message)
                except Exception:
                    pass  # Ne pas propager les erreurs du callback

    def start_monitoring(self) -> None:
        """
        Démarre la boucle de monitoring dans un thread séparé.
        
        Le monitoring récupère les données toutes les `poll_interval` secondes
        et les enregistre dans le fichier GeoJSON.
        L'enregistrement commence automatiquement au décollage et s'arrête à l'atterrissage.
        """
        if self._running:
            return

        # Réinitialiser l'état de vol et l'historique
        self._flight_state = FlightState.WAITING
        self._data_history.clear()
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """
        Arrête la boucle de monitoring et ferme la connexion.
        """
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
            self._monitor_thread = None
        self.disconnect()
        self._flight_state = FlightState.WAITING
        self._data_history.clear()
        self._notify_connection_status(False, _("Monitoring arrêté"))

    def _monitor_loop(self) -> None:
        """
        Boucle principale de monitoring.
        Doit être appelée dans un thread séparé.
        
        Enregistre uniquement les points entre le décollage et l'atterrissage.
        """
        # Tentative de connexion initiale
        if not self.connect():
            self._notify_connection_status(
                False,
                _("Échec de la connexion initiale au simulateur")
            )
            self._running = False
            return

        self._notify_connection_status(True, _("Connecté au simulateur - En attente de décollage"))

        # Boucle de polling
        while self._running:
            try:
                data = self.get_data()
                if data:
                    # Vérifier si on doit enregistrer ce point (selon état de vol)
                    should_record = self._update_flight_state(data)
                    
                    if should_record:
                        # Enregistrer dans GeoJSON
                        self.geojson_writer.add_point(data)
                    
                    # Si atterrissage détecté, on peut s'arrêter automatiquement
                    if self._flight_state == FlightState.LANDED:
                        self._running = False
                        break
                
                # Attendre l'intervalle de polling
                for _ in range(int(self.poll_interval * 10)):
                    if not self._running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                self._notify_connection_status(
                    False,
                    _("Erreur lors de la récupération des données: {error}", error=str(e))
                )
                self._running = False
                break

        self._notify_connection_status(False, _("Déconnecté"))

# ---------------------------------------------------------------------------
# Moniteur MSFS (SimConnect)
# ---------------------------------------------------------------------------

class MSFSMonitor(BaseSimulatorMonitor):
    """
    Moniteur pour MSFS 2020/2024/P3D via SimConnect.
    
    Note: SimConnect est une API Windows native. Ce moniteur ne fonctionnera
    que sur Windows avec le simulateur en cours d'exécution.
    """

    MAX_ENGINES = 4

    def __init__(self, geojson_path: str, poll_interval: float = 1.0, include_trajectory: bool = False):
        """
        Args:
            geojson_path: Chemin vers le fichier de sortie (.json ou .geojson)
            poll_interval: Intervalle de polling en secondes
            include_trajectory: Si True, ajoute une LineString pour QGIS
        """
        super().__init__(geojson_path, poll_interval, include_trajectory)
        self._sm = None
        self._aq = None

    def connect(self) -> bool:
        """Établit la connexion SimConnect."""
        try:
            # Import dynamique pour éviter les erreurs sur les systèmes non-Windows
            from SimConnect import SimConnect, AircraftRequests
            self._sm = SimConnect()
            # _time=0 : pas de cache côté bibliothèque, on lit la valeur fraîche
            self._aq = AircraftRequests(self._sm, _time=0)
            return True
        except ImportError:
            self._notify_connection_status(
                False,
                _("Module SimConnect non installé (Windows uniquement)")
            )
            return False
        except Exception as e:
            self._notify_connection_status(
                False,
                _("Échec de connexion SimConnect: {error}", error=str(e))
            )
            return False

    def disconnect(self) -> None:
        """Ferme la connexion SimConnect."""
        if self._sm:
            try:
                self._sm.exit()
            except Exception:
                pass
            self._sm = None
            self._aq = None

    def get_data(self) -> dict:
        """Récupère les données MSFS."""
        if not self._aq:
            return {}

        s = {}

        try:
            # Position
            lat = self._aq.get("PLANE LATITUDE")
            lon = self._aq.get("PLANE LONGITUDE")
            s["latitude"] = f"{float(lat):.6f} °" if lat is not None else "—"
            s["longitude"] = f"{float(lon):.6f} °" if lon is not None else "—"

            # Temps (ABSOLUTE TIME = secondes depuis J2000 epoch)
            abs_t = self._aq.get("ABSOLUTE TIME")
            s["sim_time"] = self._absolute_time_to_iso(abs_t) if abs_t is not None else "—"

            # Altitudes
            alt_msl = self._aq.get("INDICATED ALTITUDE")
            alt_agl = self._aq.get("PLANE ALT ABOVE GROUND")
            s["alt_msl"] = f"{float(alt_msl):,.0f} ft" if alt_msl is not None else "—"
            s["alt_agl"] = f"{float(alt_agl):,.0f} ft" if alt_agl is not None else "—"

            # Caps
            hdg_true = self._aq.get("PLANE HEADING DEGREES TRUE")
            hdg_mag = self._aq.get("PLANE HEADING DEGREES MAGNETIC")
            s["heading_true"] = f"{float(hdg_true):.1f} °" if hdg_true is not None else "—"
            s["heading_mag"] = f"{float(hdg_mag):.1f} °" if hdg_mag is not None else "—"

            # Vitesse
            ias = self._aq.get("AIRSPEED INDICATED")
            gs = self._aq.get("GROUND VELOCITY")
            s["ias"] = f"{float(ias):.1f} kt" if ias is not None else "—"
            s["gs"] = f"{float(gs):.1f} kt" if gs is not None else "—"

            # Puissance moteur (GENERAL ENG BRAKE POWER:N en ft-lb/s → HP)
            s["power"] = f"{self._get_engine_power_hp():.0f} hp"

            # Appareil
            acf_type = self._aq.get("ATC TYPE")
            acf_title = self._aq.get("TITLE")
            s["acf_icao"] = str(acf_type).strip() if acf_type else "—"
            s["acf_name"] = str(acf_title).strip() if acf_title else "—"

        except Exception as e:
            s["error"] = str(e)

        return s

    def _absolute_time_to_iso(self, abs_time: float) -> str:
        """
        Convertit ABSOLUTE TIME (secondes depuis J2000) en ISO 8601 UTC.
        """
        try:
            dt = J2000_EPOCH + timedelta(seconds=float(abs_time))
            return dt.strftime("%Y-%m-%dT%H:%M:%S Z")
        except Exception:
            return "—"

    def _get_engine_power_hp(self) -> float:
        """
        Somme la puissance de tous les moteurs actifs.
        GENERAL ENG BRAKE POWER:N est en ft-lb/s → conversion en HP.
        """
        total = 0.0
        for i in range(1, self.MAX_ENGINES + 1):
            val = self._aq.get(f"GENERAL ENG BRAKE POWER:{i}")
            if val is not None:
                try:
                    total += float(val)
                except (TypeError, ValueError):
                    pass
        return total / FT_LB_PER_S_TO_HP

# ---------------------------------------------------------------------------
# API X-Plane (interne)
# ---------------------------------------------------------------------------

class _XPlaneAPI:
    """
    Encapsule le protocole REST X-Plane 12 v3.
    
    Protocole:
      1. GET /api/v3/datarefs?filter[name]=<path> → résolution path → id
      2. GET /api/v3/datarefs/<id>/value → lecture de la valeur
    
    Les datarefs de type "data" (string) sont retournées encodées en base64.
    """

    def __init__(self, host: str, port: int):
        self._base = f"http://{host}:{port}/api/v3"
        self._cache: dict[str, int] = {}
        self._types: dict[str, str] = {}
        self._session = None

    def resolve_ids(self, paths: dict[str, str]) -> None:
        """
        Résout les IDs numériques des datarefs.
        
        Args:
            paths: Dictionnaire {clé: chemin_dataref}
        
        Raises:
            ValueError: Si une dataref est introuvable
            requests.exceptions.RequestException: En cas d'erreur réseau
        """
        import requests
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({"Accept": "application/json"})

        for key, path in paths.items():
            resp = self._session.get(
                f"{self._base}/datarefs",
                params={"filter[name]": path},
                timeout=5,
            )
            resp.raise_for_status()
            records = resp.json()["data"]
            if not records:
                raise ValueError(f"Dataref introuvable: {path}")
            self._cache[key] = records[0]["id"]
            self._types[key] = records[0]["value_type"]

    def _fetch_value(self, key: str) -> Any:
        """Récupère la valeur brute d'une dataref."""
        dr_id = self._cache[key]
        resp = self._session.get(
            f"{self._base}/datarefs/{dr_id}/value",
            timeout=3,
        )
        resp.raise_for_status()
        return resp.json()["data"]

    def get_float(self, key: str) -> float:
        """Récupère une valeur flottante."""
        return float(self._fetch_value(key))

    def get_float_array(self, key: str) -> list[float]:
        """Récupère un tableau de flottants."""
        val = self._fetch_value(key)
        if isinstance(val, list):
            return [float(v) for v in val if v is not None]
        return [float(val)]

    def get_string(self, key: str) -> str:
        """
        Récupère une chaîne de caractères.
        Décode base64 si nécessaire et retire les octets nuls.
        """
        import base64
        raw = self._fetch_value(key)
        if isinstance(raw, str):
            try:
                decoded = base64.b64decode(raw)
                return decoded.rstrip(b"\x00").decode("utf-8", errors="replace").strip()
            except Exception:
                return raw.strip()
        if isinstance(raw, list):
            return bytes(b for b in raw if b != 0).decode("utf-8", errors="replace").strip()
        return str(raw).strip()

    def close(self) -> None:
        """Ferme la session HTTP."""
        if self._session:
            self._session.close()
            self._session = None

# ---------------------------------------------------------------------------
# Moniteur X-Plane
# ---------------------------------------------------------------------------

class XPlaneMonitor(BaseSimulatorMonitor):
    """
    Moniteur pour X-Plane 12 via API REST (port 8086 par défaut).
    """

    # Datarefs à surveiller
    DATAREF_PATHS = {
        "latitude": "sim/flightmodel/position/latitude",
        "longitude": "sim/flightmodel/position/longitude",
        "zulu_sec": "sim/time/zulu_time_sec",
        "date_days": "sim/time/local_date_days",
        "alt_msl_m": "sim/flightmodel/position/elevation",
        "alt_agl_m": "sim/flightmodel/position/y_agl",
        "heading_true": "sim/flightmodel/position/psi",
        "heading_mag": "sim/flightmodel/position/mag_psi",
        "ias_mps": "sim/flightmodel/position/indicated_airspeed",
        "gs_mps": "sim/flightmodel/position/groundspeed",
        "engine_power_w": "sim/flightmodel/engine/ENGN_power",
        "acf_icao": "sim/aircraft/view/acf_ICAO",
        "acf_name": "sim/aircraft/view/acf_descrip",
    }

    def __init__(
        self,
        geojson_path: str,
        host: str = "127.0.0.1",
        port: int = 8086,
        poll_interval: float = 1.0,
        include_trajectory: bool = False
    ):
        """
        Args:
            geojson_path: Chemin vers le fichier de sortie (.json ou .geojson)
            host: Adresse IP de X-Plane (default: 127.0.0.1)
            port: Port de l'API REST X-Plane (default: 8086)
            poll_interval: Intervalle de polling en secondes
            include_trajectory: Si True, ajoute une LineString pour QGIS
        """
        super().__init__(geojson_path, poll_interval, include_trajectory)
        self.host = host
        self.port = port
        self._api = _XPlaneAPI(host, port)
        self._ids_resolved = False

    def connect(self) -> bool:
        """
        Résout les IDs des datarefs et teste la connexion.
        """
        try:
            self._api.resolve_ids(self.DATAREF_PATHS)
            self._ids_resolved = True
            # Test de connexion avec une dataref simple
            self._api.get_float("latitude")
            return True
        except ImportError:
            self._notify_connection_status(
                False,
                _("Module 'requests' non installé")
            )
            return False
        except Exception as e:
            self._notify_connection_status(
                False,
                _("Échec de connexion X-Plane: {error}", error=str(e))
            )
            return False

    def disconnect(self) -> None:
        """Ferme la session HTTP."""
        self._api.close()
        self._ids_resolved = False

    def get_data(self) -> dict:
        """Récupère les données X-Plane."""
        if not self._ids_resolved:
            return {}

        s = {}

        try:
            # Position
            s["latitude"] = f"{self._api.get_float('latitude'):.6f} °"
            s["longitude"] = f"{self._api.get_float('longitude'):.6f} °"

            # Temps
            zulu = self._api.get_float("zulu_sec")
            days = self._api.get_float("date_days")
            s["sim_time"] = self._build_iso(zulu, days)

            # Altitudes (conversion m → ft)
            s["alt_msl"] = f"{self._api.get_float('alt_msl_m') * M_TO_FT:,.0f} ft"
            s["alt_agl"] = f"{self._api.get_float('alt_agl_m') * M_TO_FT:,.0f} ft"

            # Caps
            s["heading_true"] = f"{self._api.get_float('heading_true'):.1f} °"
            s["heading_mag"] = f"{self._api.get_float('heading_mag'):.1f} °"

            # Vitesse (conversion m/s → kt)
            s["ias"] = f"{self._api.get_float('ias_mps') * MPS_TO_KT:.1f} kt"
            s["gs"] = f"{self._api.get_float('gs_mps') * MPS_TO_KT:.1f} kt"

            # Puissance (conversion W → HP)
            power_arr = self._api.get_float_array("engine_power_w")
            s["power"] = f"{sum(power_arr) * W_TO_HP:.0f} hp"

            # Appareil
            s["acf_icao"] = self._api.get_string("acf_icao")
            s["acf_name"] = self._api.get_string("acf_name")

        except Exception as e:
            s["error"] = str(e)

        return s

    def _build_iso(self, zulu_sec: float, date_days: float) -> str:
        """
        Construit un timestamp ISO 8601 à partir des données X-Plane.
        
        Args:
            zulu_sec: Secondes UTC depuis minuit
            date_days: Jours depuis le 1er janvier de l'année en cours
        """
        year = datetime.now(timezone.utc).year
        jan1 = datetime(year, 1, 1, tzinfo=timezone.utc)
        dt = (jan1
              + timedelta(days=int(date_days) - 1)
              + timedelta(seconds=float(zulu_sec)))
        return dt.strftime("%Y-%m-%dT%H:%M:%S Z")

# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_monitor(
    simulator_type: str,
    geojson_path: str,
    poll_interval: float = 1.0,
    host: str = "127.0.0.1",
    port: int = 8086,
    include_trajectory: bool = False
) -> BaseSimulatorMonitor:
    """
    Factory pour créer un moniteur de simulateur.
    
    Args:
        simulator_type: Type de simulateur - "msfs" ou "xplane"
        geojson_path: Chemin vers le fichier de sortie.
                     Accepte .json (recommandé) ou .geojson.
                     Si aucune extension, .json est ajouté automatiquement.
        poll_interval: Intervalle de polling en secondes (default: 1.0)
        host: Adresse IP pour X-Plane (ignoré pour MSFS, default: 127.0.0.1)
        port: Port pour X-Plane (ignoré pour MSFS, default: 8086)
        include_trajectory: Si True, ajoute une LineString dans le GeoJSON 
                          pour une meilleure visualisation dans QGIS.
                          Les points individuels sont toujours conservés pour 
                          les analyses (default: False).
    
    Returns:
        Instance de MSFSMonitor ou XPlaneMonitor
    
    Raises:
        ValueError: Si simulator_type est invalide
    
    Exemple:
        >>> # Avec extension .json (recommandé)
        >>> monitor = create_monitor(
        ...     simulator_type="xplane",
        ...     geojson_path="/tmp/flight_track.json",
        ...     poll_interval=1.0
        ... )
        >>> monitor.set_connection_callback(lambda c, m: print(m))
        >>> monitor.start_monitoring()
        
        >>> # Avec extension .geojson et trajectoire pour QGIS
        >>> monitor = create_monitor(
        ...     simulator_type="msfs",
        ...     geojson_path="/tmp/track.geojson",
        ...     include_trajectory=True
        ... )
        >>> monitor.start_monitoring()
    """
    if simulator_type == SimulatorType.MSFS.value:
        return MSFSMonitor(geojson_path, poll_interval, include_trajectory)
    elif simulator_type == SimulatorType.XPLANE.value:
        return XPlaneMonitor(geojson_path, host, port, poll_interval, include_trajectory)
    else:
        raise ValueError(
            f"Type de simulateur inconnu: '{simulator_type}'. "
            f"Utilisez '{SimulatorType.MSFS.value}' ou '{SimulatorType.XPLANE.value}'"
        )

# ---------------------------------------------------------------------------
# Fonction utilitaire pour vérifier la disponibilité
# ---------------------------------------------------------------------------

def check_simulator_available(simulator_type: str, host: str = "127.0.0.1", port: int = 8086) -> bool:
    """
    Vérifie si un simulateur est disponible sans démarrer le monitoring.
    
    Args:
        simulator_type: "msfs" ou "xplane"
        host: Adresse IP pour X-Plane
        port: Port pour X-Plane
    
    Returns:
        True si le simulateur est disponible, False sinon
    """
    try:
        if simulator_type == SimulatorType.MSFS.value:
            from SimConnect import SimConnect, AircraftRequests
            sm = SimConnect()
            aq = AircraftRequests(sm, _time=0)
            # Test avec une SimVar simple
            aq.get("PLANE LATITUDE")
            sm.exit()
            return True
        elif simulator_type == SimulatorType.XPLANE.value:
            import requests
            api = _XPlaneAPI(host, port)
            # Résoudre une dataref simple pour tester
            api.resolve_ids({"test": "sim/flightmodel/position/latitude"})
            api.get_float("test")
            api.close()
            return True
        else:
            return False
    except Exception:
        return False
