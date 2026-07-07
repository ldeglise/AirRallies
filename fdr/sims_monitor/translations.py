"""
Module de traduction pour sim_monitor.

Ce module fournit un système d'internationalisation (i18n) pour tous les
messages destinés à l'utilisateur dans le module sim_monitor.

Ce système utilise des identifiants uniques pour chaque message,
ce qui permet de changer de langue sans modifier le code source.

Utilisation :
    from translations import gettext as _, set_language, get_language
    
    # Dans le code - utiliser des identifiants UNIQUES
    raise ValueError(_("FILE_PATH_EMPTY"))
    _notify(_("CONNECTED_WAITING_TAKEOFF"))
    
    # Pour changer de langue
    set_language("en")  # Anglais
    set_language("fr")  # Français
"""

import threading
from typing import Optional, Dict

# ---------------------------------------------------------------------------
# Dictionnaires de traduction - IDENTIFIANTS -> MESSAGES
# ---------------------------------------------------------------------------

# Français
_FR_TRANSLATIONS: Dict[str, str] = {
    # GeoJSONWriter errors
    "FILE_PATH_EMPTY": "Le chemin du fichier ne peut pas être vide",
    "LATITUDE_MISSING": "Latitude manquante",
    "LATITUDE_INVALID": "Latitude invalide: {value}",
    "LATITUDE_OUT_OF_RANGE": "Latitude hors plage: {result} (doit être entre -90 et 90)",
    "LONGITUDE_MISSING": "Longitude manquante",
    "LONGITUDE_INVALID": "Longitude invalide: {value}",
    "LONGITUDE_OUT_OF_RANGE": "Longitude hors plage: {result} (doit être entre -180 et 180)",
    
    # BaseSimulatorMonitor messages
    "TAKEOFF_DETECTED": "Décollage détecté - Enregistrement démarré",
    "LANDING_DETECTED": "Atterrissage détecté - Enregistrement arrêté",
    "CONNECTED_WAITING_TAKEOFF": "Connecté au simulateur - En attente de décollage",
    "INITIAL_CONNECTION_FAILED": "Échec de la connexion initiale au simulateur",
    "DATA_RETRIEVAL_ERROR": "Erreur lors de la récupération des données: {error}",
    "DISCONNECTED": "Déconnecté",
    "MONITORING_STOPPED": "Monitoring arrêté",
    
    # MSFSMonitor errors
    "SIMCONNECT_NOT_INSTALLED": "Module SimConnect non installé (Windows uniquement)",
    "SIMCONNECT_CONNECTION_FAILED": "Échec de connexion SimConnect: {error}",
    
    # XPlaneMonitor errors
    "REQUESTS_NOT_INSTALLED": "Module 'requests' non installé",
    "XPLANE_CONNECTION_FAILED": "Échec de connexion X-Plane: {error}",
    "XPLANE_NOT_RUNNING": "X-Plane n'est pas en cours d'exécution ou l'API REST n'est pas accessible sur {host}:{port}",
    "XPLANE_API_TIMEOUT": "Timeout lors de la connexion à l'API X-Plane sur {host}:{port}",
    "XPLANE_API_ERROR": "Erreur de l'API X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Erreur réseau lors de la connexion à X-Plane: {error}",
    "XPLANE_WRONG_ENDPOINT": "Impossible de se connecter à l'API X-Plane sur {host}:{port}. Vérifiez que le plugin X-Plane Connect est installé ou que l'API native est activée dans les paramètres de X-Plane.",
    "XPLANE_CHECK_HTTP_SERVER": "Vérifiez que 'Enable HTTP Server' est activé dans Settings > Network de X-Plane (port par défaut: 8080).",
    "XPLANE_INCOMING_TRAFFIC_DISABLED": "Le trafic entrant est désactivé dans les paramètres réseau de X-Plane. Activez 'Enable Incoming Traffic' dans Settings > Network.",
    "XPLANE_INVALID_API_RESPONSE_FORMAT": "Format de réponse de l'API X-Plane invalide.",
    "XPLANE_DATAREF_TIMEOUT": "Timeout lors de la lecture de la dataref {key} (ID: {id}).",
    "XPLANE_HTTP_ERROR": "Erreur HTTP {status} lors de la connexion à X-Plane.",
    
    # _XPlaneAPI errors
    "DATAREF_NOT_FOUND": "Dataref introuvable: {path}",
    "XPLANE_INVALID_API_RESPONSE": "Réponse de l'API X-Plane invalide: {error}",
    
    # create_monitor errors
    "UNKNOWN_SIMULATOR_TYPE": "Type de simulateur inconnu: '{simulator_type}'. Utilisez '{msfs}' ou '{xplane}'",
}

# Anglais
_EN_TRANSLATIONS: Dict[str, str] = {
    # GeoJSONWriter errors
    "FILE_PATH_EMPTY": "File path cannot be empty",
    "LATITUDE_MISSING": "Missing latitude",
    "LATITUDE_INVALID": "Invalid latitude: {value}",
    "LATITUDE_OUT_OF_RANGE": "Latitude out of range: {result} (must be between -90 and 90)",
    "LONGITUDE_MISSING": "Missing longitude",
    "LONGITUDE_INVALID": "Invalid longitude: {value}",
    "LONGITUDE_OUT_OF_RANGE": "Longitude out of range: {result} (must be between -180 and 180)",
    
    # BaseSimulatorMonitor messages
    "TAKEOFF_DETECTED": "Takeoff detected - Recording started",
    "LANDING_DETECTED": "Landing detected - Recording stopped",
    "CONNECTED_WAITING_TAKEOFF": "Connected to simulator - Waiting for takeoff",
    "INITIAL_CONNECTION_FAILED": "Initial connection to simulator failed",
    "DATA_RETRIEVAL_ERROR": "Error retrieving data: {error}",
    "DISCONNECTED": "Disconnected",
    "MONITORING_STOPPED": "Monitoring stopped",
    
    # MSFSMonitor errors
    "SIMCONNECT_NOT_INSTALLED": "SimConnect module not installed (Windows only)",
    "SIMCONNECT_CONNECTION_FAILED": "SimConnect connection failed: {error}",
    
    # XPlaneMonitor errors
    "REQUESTS_NOT_INSTALLED": "'requests' module not installed",
    "XPLANE_CONNECTION_FAILED": "X-Plane connection failed: {error}",
    "XPLANE_NOT_RUNNING": "X-Plane is not running or REST API is not accessible at {host}:{port}",
    "XPLANE_API_TIMEOUT": "Timeout connecting to X-Plane API at {host}:{port}",
    "XPLANE_API_ERROR": "X-Plane API error: {error}",
    "XPLANE_NETWORK_ERROR": "Network error connecting to X-Plane: {error}",
    "XPLANE_WRONG_ENDPOINT": "Cannot connect to X-Plane API at {host}:{port}. Check that X-Plane Connect plugin is installed or that the native HTTP server is enabled in X-Plane Settings > Network.",
    "XPLANE_CHECK_HTTP_SERVER": "Check that 'Enable HTTP Server' is enabled in X-Plane Settings > Network (default port: 8080).",
    "XPLANE_INCOMING_TRAFFIC_DISABLED": "Incoming traffic is disabled in X-Plane Network settings. Enable 'Allow Incoming Traffic' in Settings > Network.",
    "XPLANE_INVALID_API_RESPONSE_FORMAT": "Invalid X-Plane API response format.",
    "XPLANE_DATAREF_TIMEOUT": "Timeout reading dataref {key} (ID: {id}).",
    "XPLANE_HTTP_ERROR": "HTTP error {status} connecting to X-Plane.",
    
    # _XPlaneAPI errors
    "DATAREF_NOT_FOUND": "Dataref not found: {path}",
    "XPLANE_INVALID_API_RESPONSE": "Invalid X-Plane API response: {error}",
    
    # create_monitor errors
    "UNKNOWN_SIMULATOR_TYPE": "Unknown simulator type: '{simulator_type}'. Use '{msfs}' or '{xplane}'",
}

# Dictionnaire des traductions disponibles
_AVAILABLE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": _FR_TRANSLATIONS,
    "en": _EN_TRANSLATIONS,
}


# ---------------------------------------------------------------------------
# Gestionnaire de traductions
# ---------------------------------------------------------------------------

class TranslationManager:
    """Gère le chargement et la sélection des traductions. Thread-safe."""
    
    _instance: Optional['TranslationManager'] = None
    _lock = threading.Lock()
    _current_language: Optional[str]
    _custom_translations: Dict[str, Dict[str, str]]
    
    def __new__(cls):
        with TranslationManager._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._current_language = None
                cls._instance._custom_translations = {}
            return cls._instance
    
    def _detect_system_language(self) -> str:
        """Détecte la langue du système. Retourne 'en' si la détection échoue."""
        import locale
        try:
            lang = locale.getdefaultlocale()[0]
            if lang is not None:
                lang = lang[:2]  # Prendre seulement le code langue
            else:
                lang = "en"
        except Exception:
            lang = "en"
        return lang
    
    def set_language(self, lang: Optional[str] = None) -> None:
        """Définit la langue active."""
        with self._lock:
            if lang is None:
                lang = self._detect_system_language()
            
            if lang not in _AVAILABLE_TRANSLATIONS and lang not in self._custom_translations:
                lang = "en"
            
            self._current_language = lang
    
    def get_current_language(self) -> Optional[str]:
        return self._current_language
    
    def add_translations(self, lang: str, translations: Dict[str, str]) -> None:
        """Ajoute des traductions personnalisées."""
        with self._lock:
            self._custom_translations[lang] = translations
    
    def gettext(self, message_id: str, **kwargs) -> str:
        """Traduit un identifiant de message."""
        with self._lock:
            lang = self._current_language
            if lang is None:
                # Détecter la langue système sans acquérir le lock à nouveau
                lang = self._detect_system_language()
                if lang not in _AVAILABLE_TRANSLATIONS and lang not in self._custom_translations:
                    lang = "en"
                self._current_language = lang
            
            translations = _AVAILABLE_TRANSLATIONS.get(lang, {}).copy()
            translations.update(self._custom_translations.get(lang, {}))
            
            message_template = translations.get(message_id, message_id)
            
            if kwargs:
                try:
                    return message_template.format(**kwargs)
                except (KeyError, ValueError):
                    return message_template
            
            return message_template


# ---------------------------------------------------------------------------
# Fonctions publiques
# ---------------------------------------------------------------------------

_translation_manager = TranslationManager()
# La langue sera détectée automatiquement lors du premier appel à gettext()
# ou peut être définie explicitement via set_language()


def set_language(lang: Optional[str] = None) -> None:
    """Définit la langue active."""
    _translation_manager.set_language(lang)


def get_language() -> Optional[str]:
    """Retourne la langue actuelle."""
    return _translation_manager.get_current_language()


def gettext(message_id: str, **kwargs) -> str:
    """Traduit un identifiant de message."""
    return _translation_manager.gettext(message_id, **kwargs)


def add_translations(lang: str, translations: Dict[str, str]) -> None:
    """Ajoute des traductions personnalisées."""
    _translation_manager.add_translations(lang, translations)


# Alias
_ = gettext
