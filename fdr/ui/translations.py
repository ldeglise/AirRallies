"""
Module de traduction pour l'interface utilisateur (GUI).

Ce module fournit un système d'internationalisation (i18n) pour toute l'interface
graphique de Flight Data Recorder.

Utilisation :
    from ui.translations import gettext as _, set_language, get_language, retranslate_ui
    
    # Dans fdr.py - pour traduire une chaîne
    title = _("FLIGHT_DATA_RECORDER_TITLE")
    
    # Pour changer de langue
    set_language("fr")  # Français
    set_language("en")  # Anglais
    
    # Pour retraduire l'UI après changement de langue
    retranslate_ui(main_window)

Synchronisation avec sim_monitor :
    Ce module partage la même détection de langue et le même fallback
    vers l'anglais que sim_monitor/translations.py.
"""

import threading
from typing import Optional, Dict, Callable


# ---------------------------------------------------------------------------
# Dictionnaires de traduction - IDENTIFIANTS -> MESSAGES
# ---------------------------------------------------------------------------

# Français
_FR_TRANSLATIONS: Dict[str, str] = {
    # Fenêtre principale
    "FLIGHT_DATA_RECORDER_TITLE": "Enregistreur de Données de Vol",
    "FILE_MENU": "Fichier",
    "HELP_MENU": "Aide",
    "EXIT_ACTION": "Quitter",
    "ABOUT_ACTION": "À propos",
    
    # Menu Langue (ajouté)
    "LANGUAGE_MENU": "Langue",
    "LANGUAGE_ENGLISH": "Anglais",
    "LANGUAGE_FRENCH": "Français",
    
    # Onglets
    "MAIN_TAB": "Principal",
    "ADVANCED_TAB": "Avancé",
    
    # Onglet Main - Paramètres Simulateur
    "SIMULATOR_SETTINGS": "Paramètres du Simulateur",
    "SIMULATOR_TYPE": "Type de simulateur :",
    "SIMULATOR_XPLANE_12": "X-Plane 12",
    "SIMULATOR_MSFS_P3D": "MSFS 2020/2024 / P3D",
    "HOST": "Hôte :",
    "HOST_PLACEHOLDER": "Entrez l'adresse IP",
    "PORT": "Port :",
    "POLL_INTERVAL": "Intervalle de sondage (s) :",
    
    # Onglet Main - Paramètres de Sortie
    "OUTPUT_SETTINGS": "Paramètres de Sortie",
    "OUTPUT_FILE": "Fichier de sortie :",
    "OUTPUT_FILE_PLACEHOLDER": "Sélectionnez le chemin du fichier de sortie...",
    "BROWSE_BUTTON": "Parcourir...",
    "INCLUDE_TRAJECTORY": "Inclure la ligne de trajectoire",
    "INCLUDE_TRAJECTORY_TOOLTIP": "Ajoute une fonction LineString pour la visualisation de la trajectoire dans QGIS",
    "AUTO_CONNECT": "Connexion automatique au démarrage",
    "AUTO_CONNECT_TOOLTIP": "Se connecte automatiquement au simulateur lorsque le monitoring commence",
    
    # Onglet Main - Contrôles
    "CONTROLS": "Contrôles",
    "CONNECT_BUTTON": "Se connecter",
    "DISCONNECT_BUTTON": "Se déconnecter",
    "START_MONITORING": "Démarrer le Monitoring",
    "STOP_MONITORING": "Arrêter le Monitoring",
    
    # Onglet Main - Statut
    "STATUS": "Statut",
    "CONNECTION": "Connexion :",
    "CONNECTION_CONNECTED": "Connecté",
    "CONNECTION_DISCONNECTED": "Déconnecté",
    "FLIGHT_STATE": "État de vol :",
    "FLIGHT_STATE_WAITING": "En attente",
    "FLIGHT_STATE_IN_FLIGHT": "En vol",
    "FLIGHT_STATE_LANDED": "Atterri",
    "MONITORING": "Monitoring :",
    "MONITORING_RUNNING": "En cours",
    "MONITORING_STOPPED": "Arrêté",
    
    # Status bar
    "READY": "Prêt",
    
    # File dialog filter
    "FILE_FILTER_GEOJSON": "Fichiers GeoJSON (*.json *.geojson);;Tous les fichiers (*)",
    
    # Log initial
    "LOG_STARTUP": "Application démarrée. Prête pour le monitoring.",
    
    # Onglet Advanced
    "ADVANCED_TAB": "Avancé",
    "AIRCRAFT_INFORMATION": "Informations sur l'appareil",
    "ICAO_CODE": "Code ICAO :",
    "AIRCRAFT_NAME": "Nom de l'appareil :",
    "LIVE_DATA": "Données en temps réel",
    "LATITUDE": "Latitude :",
    "LONGITUDE": "Longitude :",
    "ALTITUDE_MSL": "Altitude (MSL) :",
    "ALTITUDE_AGL": "Altitude (AGL) :",
    "HEADING": "Cap :",
    "GROUND_SPEED": "Vitesse sol :",
    "INDICATED_SPEED": "Vitesse indiquée :",
    "POWER": "Puissance :",
    "SIMULATION_TIME": "Heure de simulation :",
    "N_A": "N/D",
    
    # Dialogues et messages
    "SELECT_OUTPUT_FILE": "Sélectionner le fichier de sortie",
    "ERROR_NO_OUTPUT_FILE": "Erreur : Aucun fichier de sortie spécifié",
    "ERROR_SPECIFY_OUTPUT_FILE": "Veuillez spécifier un chemin de fichier de sortie.",
    "MONITOR_CREATED": "Moniteur créé pour le simulateur {sim_type}",
    "ERROR_CREATING_MONITOR": "Erreur lors de la création du moniteur : {error}",
    "FAILED_CREATE_MONITOR": "Échec de la création du moniteur : {error}",
    "CONNECTED_SUCCESS": "Connexion au simulateur réussie",
    "CONNECT_FAILED": "Échec de la connexion au simulateur",
    "CONNECTION_ERROR": "Erreur de connexion : {error}",
    "DISCONNECTED_SUCCESS": "Déconnecté du simulateur",
    "DISCONNECT_ERROR": "Erreur lors de la déconnexion : {error}",
    "OUTPUT_CHANGED": "Les paramètres de sortie ont changé, recréation du moniteur...",
    "MONITORING_STARTED": "Monitoring démarré",
    "ERROR_STARTING_MONITORING": "Erreur lors du démarrage du monitoring : {error}",
    "FAILED_START_MONITORING": "Échec du démarrage du monitoring : {error}",
    "MONITORING_STOPPED": "Monitoring arrêté",
    "ERROR_STOPPING_MONITORING": "Erreur lors de l'arrêt du monitoring : {error}",
    "ERROR_POLLING_DATA": "Erreur lors du sondage des données : {error}",
    "ERROR_UPDATING_DATA": "Erreur lors de la mise à jour de l'affichage des données : {error}",
    
    # Boîte About
    "ABOUT_TITLE": "À propos de l'Enregistreur de Données de Vol",
    "ABOUT_VERSION": "Version 1.0.0",
    "ABOUT_DESCRIPTION": "Un outil pour enregistrer les données de vol des simulateurs au format GeoJSON.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Simulateurs supportés :</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (via API REST sur le port 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (via SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (via SimConnect)",
    "ABOUT_FEATURES": "<b>Fonctionnalités :</b>",
    "ABOUT_FEATURE_REALTIME": "Enregistrement des données de vol en temps réel",
    "ABOUT_FEATURE_AUTO_DETECT": "Détection automatique du décollage et de l'atterrissage",
    "ABOUT_FEATURE_GEOJSON": "Sortie GeoJSON (conforme RFC 7946)",
    "ABOUT_FEATURE_TRAJECTORY": "Ligne de trajectoire LineString optionnelle pour visualisation dans QGIS",
    "ABOUT_FEATURE_CONNECTION_MODES": "Modes de connexion manuel ou automatique",
    "ABOUT_OUTPUT_DESC": "<b>Sortie :</b> Fichiers GeoJSON avec des fonctionnalités Point pour chaque échantillon de données, incluant éventuellement une fonctionnalité LineString pour la visualisation de la trajectoire.",
    "ABOUT_AUTHOR": "<b>Auteur :</b> Équipe de Développement AirRallies",
}

# Anglais
_EN_TRANSLATIONS: Dict[str, str] = {
    # Fenêtre principale
    "FLIGHT_DATA_RECORDER_TITLE": "Flight Data Recorder",
    "FILE_MENU": "File",
    "HELP_MENU": "Help",
    "EXIT_ACTION": "Exit",
    "ABOUT_ACTION": "About",
    
    # Menu Langue (ajouté)
    "LANGUAGE_MENU": "Language",
    "LANGUAGE_ENGLISH": "English",
    "LANGUAGE_FRENCH": "French",
    
    # Tabs
    "MAIN_TAB": "Main",
    "ADVANCED_TAB": "Advanced",
    
    # Onglet Main - Paramètres Simulateur
    "SIMULATOR_SETTINGS": "Simulator Settings",
    "SIMULATOR_TYPE": "Simulator Type:",
    "SIMULATOR_XPLANE_12": "X-Plane 12",
    "SIMULATOR_MSFS_P3D": "MSFS 2020/2024 / P3D",
    "HOST": "Host:",
    "HOST_PLACEHOLDER": "Enter IP address",
    "PORT": "Port:",
    "POLL_INTERVAL": "Poll Interval (s):",
    
    # Onglet Main - Paramètres de Sortie
    "OUTPUT_SETTINGS": "Output Settings",
    "OUTPUT_FILE": "Output File:",
    "OUTPUT_FILE_PLACEHOLDER": "Select output file path...",
    "BROWSE_BUTTON": "Browse...",
    "INCLUDE_TRAJECTORY": "Include Trajectory Line",
    "INCLUDE_TRAJECTORY_TOOLTIP": "Add a LineString feature for trajectory visualization in QGIS",
    "AUTO_CONNECT": "Auto-connect on Start",
    "AUTO_CONNECT_TOOLTIP": "Automatically connect to simulator when monitoring starts",
    
    # Onglet Main - Contrôles
    "CONTROLS": "Controls",
    "CONNECT_BUTTON": "Connect",
    "DISCONNECT_BUTTON": "Disconnect",
    "START_MONITORING": "Start Monitoring",
    "STOP_MONITORING": "Stop Monitoring",
    
    # Onglet Main - Statut
    "STATUS": "Status",
    "CONNECTION": "Connection:",
    "CONNECTION_CONNECTED": "Connected",
    "CONNECTION_DISCONNECTED": "Disconnected",
    "FLIGHT_STATE": "Flight State:",
    "FLIGHT_STATE_WAITING": "Waiting",
    "FLIGHT_STATE_IN_FLIGHT": "In Flight",
    "FLIGHT_STATE_LANDED": "Landed",
    "MONITORING": "Monitoring:",
    "MONITORING_RUNNING": "Running",
    "MONITORING_STOPPED": "Stopped",
    
    # Status bar
    "READY": "Ready",
    
    # File dialog filter
    "FILE_FILTER_GEOJSON": "GeoJSON Files (*.json *.geojson);;All Files (*)",
    
    # Log initial
    "LOG_STARTUP": "Application started. Ready for monitoring.",
    
    # Onglet Advanced
    "ADVANCED_TAB": "Advanced",
    "AIRCRAFT_INFORMATION": "Aircraft Information",
    "ICAO_CODE": "ICAO Code:",
    "AIRCRAFT_NAME": "Aircraft Name:",
    "LIVE_DATA": "Live Data",
    "LATITUDE": "Latitude:",
    "LONGITUDE": "Longitude:",
    "ALTITUDE_MSL": "Altitude (MSL):",
    "ALTITUDE_AGL": "Altitude (AGL):",
    "HEADING": "Heading:",
    "GROUND_SPEED": "Ground Speed:",
    "INDICATED_SPEED": "Indicated Speed:",
    "POWER": "Power:",
    "SIMULATION_TIME": "Simulation Time:",
    "N_A": "N/A",
    
    # Dialogues et messages
    "SELECT_OUTPUT_FILE": "Select Output File",
    "ERROR_NO_OUTPUT_FILE": "Error: No output file specified",
    "ERROR_SPECIFY_OUTPUT_FILE": "Please specify an output file path.",
    "MONITOR_CREATED": "Monitor created for {sim_type} simulator",
    "ERROR_CREATING_MONITOR": "Error creating monitor: {error}",
    "FAILED_CREATE_MONITOR": "Failed to create monitor: {error}",
    "CONNECTED_SUCCESS": "Successfully connected to simulator",
    "CONNECT_FAILED": "Failed to connect to simulator",
    "CONNECTION_ERROR": "Connection error: {error}",
    "DISCONNECTED_SUCCESS": "Disconnected from simulator",
    "DISCONNECT_ERROR": "Error disconnecting: {error}",
    "OUTPUT_CHANGED": "Output settings changed, recreating monitor...",
    "MONITORING_STARTED": "Monitoring started",
    "ERROR_STARTING_MONITORING": "Error starting monitoring: {error}",
    "FAILED_START_MONITORING": "Failed to start monitoring: {error}",
    "MONITORING_STOPPED": "Monitoring stopped",
    "ERROR_STOPPING_MONITORING": "Error stopping monitoring: {error}",
    "ERROR_POLLING_DATA": "Error polling data: {error}",
    "ERROR_UPDATING_DATA": "Error updating data display: {error}",
    
    # Boîte About
    "ABOUT_TITLE": "About Flight Data Recorder",
    "ABOUT_VERSION": "Version 1.0.0",
    "ABOUT_DESCRIPTION": "A tool for recording flight data from flight simulators to GeoJSON format.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Supported Simulators:</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (via REST API on port 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (via SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (via SimConnect)",
    "ABOUT_FEATURES": "<b>Features:</b>",
    "ABOUT_FEATURE_REALTIME": "Real-time flight data recording",
    "ABOUT_FEATURE_AUTO_DETECT": "Auto-detection of takeoff and landing",
    "ABOUT_FEATURE_GEOJSON": "GeoJSON output (RFC 7946 compliant)",
    "ABOUT_FEATURE_TRAJECTORY": "Optional trajectory LineString for QGIS visualization",
    "ABOUT_FEATURE_CONNECTION_MODES": "Manual or automatic connection modes",
    "ABOUT_OUTPUT_DESC": "<b>Output:</b> GeoJSON files with Point features for each data sample, optionally including a LineString feature for trajectory visualization.",
    "ABOUT_AUTHOR": "<b>Author:</b> AirRallies Development Team",
}

# Dictionnaire des traductions disponibles
_AVAILABLE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": _FR_TRANSLATIONS,
    "en": _EN_TRANSLATIONS,
}


# ---------------------------------------------------------------------------
# Gestionnaire de traductions (partagé avec sim_monitor si possible)
# ---------------------------------------------------------------------------

class TranslationManager:
    """Gère le chargement et la sélection des traductions. Thread-safe."""
    
    _instance: Optional['TranslationManager'] = None
    _lock = threading.Lock()
    _current_language: Optional[str]
    _custom_translations: Dict[str, Dict[str, str]]
    _retranslate_callbacks: list[Callable[[str], None]]
    
    def __new__(cls):
        with TranslationManager._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._current_language = None
                cls._instance._custom_translations = {}
                cls._instance._retranslate_callbacks = []
            return cls._instance
    
    def _detect_system_language(self) -> str:
        """Détecte la langue du système. Retourne 'en' si la détection échoue."""
        import locale
        try:
            lang = locale.getdefaultlocale()[0]
            if lang is not None:
                lang = lang[:2].lower()  # Prendre seulement le code langue et en minuscules
            else:
                lang = "en"
        except Exception:
            lang = "en"
        return lang
    
    def set_language(self, lang: Optional[str] = None) -> None:
        """
        Définit la langue active.
        
        Args:
            lang: Code de langue (ex: 'fr', 'en') ou None pour détection automatique
        """
        with self._lock:
            if lang is None:
                lang = self._detect_system_language()
            
            # Normaliser en minuscules
            lang = lang.lower()
            
            # Vérifier si la langue est disponible
            if lang not in _AVAILABLE_TRANSLATIONS and lang not in self._custom_translations:
                lang = "en"  # Repli vers l'anglais
            
            old_lang = self._current_language
            self._current_language = lang
            
            # Si la langue a changé, notifier les callbacks
            if old_lang != lang:
                for callback in self._retranslate_callbacks:
                    try:
                        callback(lang)
                    except Exception:
                        pass  # Ne pas propager les erreurs des callbacks
    
    def get_current_language(self) -> Optional[str]:
        """Retourne la langue actuelle."""
        with self._lock:
            return self._current_language
    
    def add_translations(self, lang: str, translations: Dict[str, str]) -> None:
        """Ajoute des traductions personnalisées."""
        with self._lock:
            self._custom_translations[lang.lower()] = translations
    
    def gettext(self, message_id: str, **kwargs) -> str:
        """
        Traduit un identifiant de message.
        
        Args:
            message_id: Identifiant unique du message
            **kwargs: Paramètres pour le formatage de chaîne
            
        Returns:
            La traduction ou l'identifiant si non trouvé (fallback)
        """
        with self._lock:
            lang = self._current_language
            if lang is None:
                # Détecter la langue système sans acquérir le lock à nouveau
                lang = self._detect_system_language()
                if lang not in _AVAILABLE_TRANSLATIONS and lang not in self._custom_translations:
                    lang = "en"
                self._current_language = lang
            
            # Fusionner les traductions disponibles
            translations = _AVAILABLE_TRANSLATIONS.get(lang, {}).copy()
            translations.update(self._custom_translations.get(lang, {}))
            
            # Récupérer le message
            message_template = translations.get(message_id, message_id)
            
            # Formater avec les kwargs si nécessaire
            if kwargs:
                try:
                    return message_template.format(**kwargs)
                except (KeyError, ValueError):
                    return message_template
            
            return message_template
    
    def on_language_change(self, callback: Callable[[str], None]) -> None:
        """
        Enregistre un callback à appeler lorsque la langue change.
        
        Args:
            callback: Fonction appelée avec le nouveau code de langue
        """
        with self._lock:
            if callback not in self._retranslate_callbacks:
                self._retranslate_callbacks.append(callback)
    
    def remove_language_change_callback(self, callback: Callable[[str], None]) -> None:
        """Retire un callback."""
        with self._lock:
            if callback in self._retranslate_callbacks:
                self._retranslate_callbacks.remove(callback)


# ---------------------------------------------------------------------------
# Instance globale et fonctions publiques
# ---------------------------------------------------------------------------

_translation_manager = TranslationManager()


def set_language(lang: Optional[str] = None) -> None:
    """
    Définit la langue active pour toute l'application.
    
    Args:
        lang: Code de langue ('fr', 'en') ou None pour détection automatique
    """
    _translation_manager.set_language(lang)


def get_language() -> Optional[str]:
    """Retourne la langue actuelle."""
    return _translation_manager.get_current_language()


def gettext(message_id: str, **kwargs) -> str:
    """
    Traduit un identifiant de message.
    
    Args:
        message_id: Identifiant unique du message
        **kwargs: Paramètres pour le formatage
        
    Returns:
        La traduction ou l'identifiant si non trouvé
    """
    return _translation_manager.gettext(message_id, **kwargs)


def add_translations(lang: str, translations: Dict[str, str]) -> None:
    """Ajoute des traductions personnalisées."""
    _translation_manager.add_translations(lang, translations)


def on_language_change(callback: Callable[[str], None]) -> None:
    """Enregistre un callback pour les changements de langue."""
    _translation_manager.on_language_change(callback)


def remove_language_change_callback(callback: Callable[[str], None]) -> None:
    """Retire un callback pour les changements de langue."""
    _translation_manager.remove_language_change_callback(callback)


# Alias pour compatibilité avec gettext
_ = gettext


# ---------------------------------------------------------------------------
# Fonctions utilitaires pour la synchronisation avec sim_monitor
# ---------------------------------------------------------------------------

def sync_with_sim_monitor():
    """
    Synchronise la langue du GUI avec celle de sim_monitor.
    
    Cette fonction doit être appelée après l'import de sim_monitor
    pour s'assurer que les deux modules utilisent la même langue.
    """
    try:
        from sims_monitor.translations import set_language as sim_set_language, get_language as sim_get_language
        current_lang = get_language()
        if current_lang is None:
            # Détecter la langue
            current_lang = _translation_manager._detect_system_language()
        sim_set_language(current_lang)
    except ImportError:
        pass  # sim_monitor non disponible, ignorer


def set_language_both(lang: Optional[str] = None) -> None:
    """
    Définit la langue pour le GUI et sim_monitor simultanément.
    
    Args:
        lang: Code de langue ou None pour détection automatique
    """
    set_language(lang)
    try:
        from sims_monitor.translations import set_language as sim_set_language
        sim_set_language(lang)
    except ImportError:
        pass
