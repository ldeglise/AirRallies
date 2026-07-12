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
    "LANGUAGE_ITALIAN": "Italien",
    "LANGUAGE_SPANISH": "Espagnol",
    "LANGUAGE_PORTUGUESE": "Portugais",
    "LANGUAGE_GERMAN": "Allemand",
    
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
    "POLL_INTERVAL": "Intervalle de mesure (s) :",
    
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
    "HEADING_TRUE": "Cap vrai :",
    "HEADING_MAG": "Cap magnétique :",
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
    "ERROR_POLLING_DATA": "Erreur lors de la mesure des données : {error}",
    "ERROR_UPDATING_DATA": "Erreur lors de la mise à jour de l'affichage des données : {error}",
    "NOT_CONNECTED": "Non connecté",
    "CONNECT_FIRST": "Veuillez vous connecter au simulateur d'abord.",
    "CONNECTION_FAILED": "Échec de la connexion",
    "XPLANE_NOT_RUNNING": "X-Plane n'est pas en cours d'exécution ou l'API REST n'est pas accessible sur {host}:{port}",
    "XPLANE_API_TIMEOUT": "Timeout lors de la connexion à l'API X-Plane sur {host}:{port}",
    "XPLANE_API_ERROR": "Erreur de l'API X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Erreur réseau lors de la connexion à X-Plane: {error}",
    "REQUESTS_NOT_INSTALLED": "Module 'requests' non installé",
    
    # Boîte About
    "ABOUT_TITLE": "À propos de l'Enregistreur de Données de Vol",
    "ABOUT_VERSION": "Version 0.0.5",
    "ABOUT_DESCRIPTION": "Un outil pour enregistrer les données de vol des simulateurs au format GeoJSON.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Simulateurs supportés :</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (via API REST sur le port 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (via SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (via SimConnect)",
    "ABOUT_LICENSE": "<b>Licence :</b> MIT",
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
    "LANGUAGE_ITALIAN": "Italian",
    "LANGUAGE_SPANISH": "Spanish",
    "LANGUAGE_PORTUGUESE": "Portuguese",
    "LANGUAGE_GERMAN": "German",
    
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
    "HEADING_TRUE": "Heading (True):",
    "HEADING_MAG": "Heading (Mag):",
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
    "NOT_CONNECTED": "Not Connected",
    "CONNECT_FIRST": "Please connect to the simulator first.",
    "CONNECTION_FAILED": "Connection Failed",
    "XPLANE_NOT_RUNNING": "X-Plane is not running or REST API is not accessible at {host}:{port}",
    "XPLANE_API_TIMEOUT": "Timeout connecting to X-Plane API at {host}:{port}",
    "XPLANE_API_ERROR": "X-Plane API error: {error}",
    "XPLANE_NETWORK_ERROR": "Network error connecting to X-Plane: {error}",
    "REQUESTS_NOT_INSTALLED": "'requests' module not installed",
    
    # Boîte About
    "ABOUT_TITLE": "About Flight Data Recorder",
    "ABOUT_VERSION": "Version 0.0.5",
    "ABOUT_DESCRIPTION": "A tool for recording flight data from flight simulators to GeoJSON format.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Supported Simulators:</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (via REST API on port 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (via SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (via SimConnect)",
    "ABOUT_LICENSE": "<b>License:</b> MIT",
    "ABOUT_AUTHOR": "<b>Author:</b> AirRallies Development Team",
}

# Italien
_IT_TRANSLATIONS: Dict[str, str] = {
    # Finestra principale
    "FLIGHT_DATA_RECORDER_TITLE": "Registratore Dati di Volo",
    "FILE_MENU": "File",
    "HELP_MENU": "Aiuto",
    "EXIT_ACTION": "Esci",
    "ABOUT_ACTION": "Informazioni",
    
    # Menu Lingua
    "LANGUAGE_MENU": "Lingua",
    "LANGUAGE_ENGLISH": "Inglese",
    "LANGUAGE_FRENCH": "Francese",
    "LANGUAGE_ITALIAN": "Italiano",
    "LANGUAGE_SPANISH": "Spagnolo",
    "LANGUAGE_PORTUGUESE": "Portoghese",
    "LANGUAGE_GERMAN": "Tedesco",
    
    # Schede
    "MAIN_TAB": "Principale",
    "ADVANCED_TAB": "Avanzate",
    
    # Scheda Main - Impostazioni Simulatore
    "SIMULATOR_SETTINGS": "Impostazioni Simulatore",
    "SIMULATOR_TYPE": "Tipo di simulatore:",
    "SIMULATOR_XPLANE_12": "X-Plane 12",
    "SIMULATOR_MSFS_P3D": "MSFS 2020/2024 / P3D",
    "HOST": "Host:",
    "HOST_PLACEHOLDER": "Inserisci l'indirizzo IP",
    "PORT": "Porta:",
    "POLL_INTERVAL": "Intervallo di campionamento (s):",
    
    # Scheda Main - Impostazioni di Output
    "OUTPUT_SETTINGS": "Impostazioni di Output",
    "OUTPUT_FILE": "File di output:",
    "OUTPUT_FILE_PLACEHOLDER": "Seleziona il percorso del file di output...",
    "BROWSE_BUTTON": "Sfoglia...",
    "INCLUDE_TRAJECTORY": "Includi linea di traccia",
    "INCLUDE_TRAJECTORY_TOOLTIP": "Aggiunge una funzione LineString per la visualizzazione della traccia in QGIS",
    "AUTO_CONNECT": "Connessione automatica all'avvio",
    "AUTO_CONNECT_TOOLTIP": "Si connette automaticamente al simulatore quando il monitoraggio inizia",
    
    # Scheda Main - Controlli
    "CONTROLS": "Controlli",
    "CONNECT_BUTTON": "Collegati",
    "DISCONNECT_BUTTON": "Disconnetti",
    "START_MONITORING": "Avvia Monitoraggio",
    "STOP_MONITORING": "Ferma Monitoraggio",
    
    # Scheda Main - Stato
    "STATUS": "Stato",
    "CONNECTION": "Connessione:",
    "CONNECTION_CONNECTED": "Connesso",
    "CONNECTION_DISCONNECTED": "Disconnesso",
    "FLIGHT_STATE": "Stato del volo:",
    "FLIGHT_STATE_WAITING": "In attesa",
    "FLIGHT_STATE_IN_FLIGHT": "In volo",
    "FLIGHT_STATE_LANDED": "Atterrato",
    "MONITORING": "Monitoraggio:",
    "MONITORING_RUNNING": "In corso",
    "MONITORING_STOPPED": "Fermato",
    
    # Barra di stato
    "READY": "Pronto",
    
    # Filtro dialogo file
    "FILE_FILTER_GEOJSON": "File GeoJSON (*.json *.geojson);;Tutti i file (*)",
    
    # Log iniziale
    "LOG_STARTUP": "Applicazione avviata. Pronto per il monitoraggio.",
    
    # Scheda Advanced
    "ADVANCED_TAB": "Avanzate",
    "AIRCRAFT_INFORMATION": "Informazioni sull'aeromobile",
    "ICAO_CODE": "Codice ICAO:",
    "AIRCRAFT_NAME": "Nome aeromobile:",
    "LIVE_DATA": "Dati in tempo reale",
    "LATITUDE": "Latitudine:",
    "LONGITUDE": "Longitudine:",
    "ALTITUDE_MSL": "Altitudine (MSL):",
    "ALTITUDE_AGL": "Altitudine (AGL):",
    "HEADING": "Prua:",
    "HEADING_TRUE": "Prua (vera):",
    "HEADING_MAG": "Prua (magnetica):",
    "GROUND_SPEED": "Velocità al suolo:",
    "INDICATED_SPEED": "Velocità indicata:",
    "POWER": "Potenza:",
    "SIMULATION_TIME": "Ora di simulazione:",
    "N_A": "N/D",
    
    # Finestre di dialogo e messaggi
    "SELECT_OUTPUT_FILE": "Seleziona file di output",
    "ERROR_NO_OUTPUT_FILE": "Errore: Nessun file di output specificato",
    "ERROR_SPECIFY_OUTPUT_FILE": "Specificare un percorso del file di output.",
    "MONITOR_CREATED": "Monitor creato per il simulatore {sim_type}",
    "ERROR_CREATING_MONITOR": "Errore durante la creazione del monitor: {error}",
    "FAILED_CREATE_MONITOR": "Impossibile creare il monitor: {error}",
    "CONNECTED_SUCCESS": "Connesso con successo al simulatore",
    "CONNECT_FAILED": "Impossibile connettersi al simulatore",
    "CONNECTION_ERROR": "Errore di connessione: {error}",
    "DISCONNECTED_SUCCESS": "Disconnesso dal simulatore",
    "DISCONNECT_ERROR": "Errore durante la disconnessione: {error}",
    "OUTPUT_CHANGED": "Impostazioni di output modificate, ricreazione del monitor...",
    "MONITORING_STARTED": "Monitoraggio avviato",
    "ERROR_STARTING_MONITORING": "Errore durante l'avvio del monitoraggio: {error}",
    "FAILED_START_MONITORING": "Impossibile avviare il monitoraggio: {error}",
    "MONITORING_STOPPED": "Monitoraggio fermato",
    "ERROR_STOPPING_MONITORING": "Errore durante l'arresto del monitoraggio: {error}",
    "ERROR_POLLING_DATA": "Errore durante il campionamento dei dati: {error}",
    "ERROR_UPDATING_DATA": "Errore durante l'aggiornamento dei dati: {error}",
    "NOT_CONNECTED": "Non connesso",
    "CONNECT_FIRST": "Connettersi prima al simulatore.",
    "CONNECTION_FAILED": "Connessione non riuscita",
    "XPLANE_NOT_RUNNING": "X-Plane non è in esecuzione o l'API REST non è accessibile su {host}:{port}",
    "XPLANE_API_TIMEOUT": "Timeout durante la connessione all'API X-Plane su {host}:{port}",
    "XPLANE_API_ERROR": "Errore API X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Errore di rete durante la connessione a X-Plane: {error}",
    "REQUESTS_NOT_INSTALLED": "Modulo 'requests' non installato",
    
    # Finestra About
    "ABOUT_TITLE": "Informazioni su Registratore Dati di Volo",
    "ABOUT_VERSION": "Versione 0.0.5",
    "ABOUT_DESCRIPTION": "Uno strumento per registrare i dati di volo dai simulatori in formato GeoJSON.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Simulatori supportati:</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (tramite API REST sulla porta 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (tramite SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (tramite SimConnect)",
    "ABOUT_LICENSE": "<b>Licenza:</b> MIT",
    "ABOUT_AUTHOR": "<b>Autore:</b> Team di Sviluppo AirRallies",
}

# Espagnol
_ES_TRANSLATIONS: Dict[str, str] = {
    # Ventana principal
    "FLIGHT_DATA_RECORDER_TITLE": "Grabadora de Datos de Vuelo",
    "FILE_MENU": "Archivo",
    "HELP_MENU": "Ayuda",
    "EXIT_ACTION": "Salir",
    "ABOUT_ACTION": "Acerca de",
    
    # Menu Idioma
    "LANGUAGE_MENU": "Idioma",
    "LANGUAGE_ENGLISH": "Inglés",
    "LANGUAGE_FRENCH": "Francés",
    "LANGUAGE_ITALIAN": "Italiano",
    "LANGUAGE_SPANISH": "Español",
    "LANGUAGE_PORTUGUESE": "Portugués",
    "LANGUAGE_GERMAN": "Alemán",
    
    # Pestañas
    "MAIN_TAB": "Principal",
    "ADVANCED_TAB": "Avanzado",
    
    # Pestaña Main - Configuración del Simulador
    "SIMULATOR_SETTINGS": "Configuración del Simulador",
    "SIMULATOR_TYPE": "Tipo de simulador:",
    "SIMULATOR_XPLANE_12": "X-Plane 12",
    "SIMULATOR_MSFS_P3D": "MSFS 2020/2024 / P3D",
    "HOST": "Host:",
    "HOST_PLACEHOLDER": "Introduzca la dirección IP",
    "PORT": "Puerto:",
    "POLL_INTERVAL": "Intervalo de sondeo (s):",
    
    # Pestaña Main - Configuración de Salida
    "OUTPUT_SETTINGS": "Configuración de Salida",
    "OUTPUT_FILE": "Archivo de salida:",
    "OUTPUT_FILE_PLACEHOLDER": "Seleccione la ruta del archivo de salida...",
    "BROWSE_BUTTON": "Examinar...",
    "INCLUDE_TRAJECTORY": "Incluir línea de trayectoria",
    "INCLUDE_TRAJECTORY_TOOLTIP": "Agrega una función LineString para la visualización de la trayectoria en QGIS",
    "AUTO_CONNECT": "Conectar automáticamente al inicio",
    "AUTO_CONNECT_TOOLTIP": "Se conecta automáticamente al simulador cuando comienza el monitoreo",
    
    # Pestaña Main - Controles
    "CONTROLS": "Controles",
    "CONNECT_BUTTON": "Conectar",
    "DISCONNECT_BUTTON": "Desconectar",
    "START_MONITORING": "Iniciar Monitoreo",
    "STOP_MONITORING": "Detener Monitoreo",
    
    # Pestaña Main - Estado
    "STATUS": "Estado",
    "CONNECTION": "Conexión:",
    "CONNECTION_CONNECTED": "Conectado",
    "CONNECTION_DISCONNECTED": "Desconectado",
    "FLIGHT_STATE": "Estado de vuelo:",
    "FLIGHT_STATE_WAITING": "En espera",
    "FLIGHT_STATE_IN_FLIGHT": "En vuelo",
    "FLIGHT_STATE_LANDED": "Aterrizado",
    "MONITORING": "Monitoreo:",
    "MONITORING_RUNNING": "En ejecución",
    "MONITORING_STOPPED": "Detenido",
    
    # Barra de estado
    "READY": "Listo",
    
    # Filtro de diálogo de archivos
    "FILE_FILTER_GEOJSON": "Archivos GeoJSON (*.json *.geojson);;Todos los archivos (*)",
    
    # Log inicial
    "LOG_STARTUP": "Aplicación iniciada. Lista para el monitoreo.",
    
    # Pestaña Advanced
    "ADVANCED_TAB": "Avanzado",
    "AIRCRAFT_INFORMATION": "Información de la Aeronave",
    "ICAO_CODE": "Código ICAO:",
    "AIRCRAFT_NAME": "Nombre de la aeronave:",
    "LIVE_DATA": "Datos en tiempo real",
    "LATITUDE": "Latitud:",
    "LONGITUDE": "Longitud:",
    "ALTITUDE_MSL": "Altitud (MSL):",
    "ALTITUDE_AGL": "Altitud (AGL):",
    "HEADING": "Rumbo:",
    "HEADING_TRUE": "Rumbo (verdadero):",
    "HEADING_MAG": "Rumbo (magnético):",
    "GROUND_SPEED": "Velocidad terrestre:",
    "INDICATED_SPEED": "Velocidad indicada:",
    "POWER": "Potencia:",
    "SIMULATION_TIME": "Hora de simulación:",
    "N_A": "N/D",
    
    # Diálogos y mensajes
    "SELECT_OUTPUT_FILE": "Seleccionar archivo de salida",
    "ERROR_NO_OUTPUT_FILE": "Error: No se especificó ningún archivo de salida",
    "ERROR_SPECIFY_OUTPUT_FILE": "Especifique una ruta de archivo de salida.",
    "MONITOR_CREATED": "Monitor creado para el simulador {sim_type}",
    "ERROR_CREATING_MONITOR": "Error al crear el monitor: {error}",
    "FAILED_CREATE_MONITOR": "No se pudo crear el monitor: {error}",
    "CONNECTED_SUCCESS": "Conexión exitosa al simulador",
    "CONNECT_FAILED": "No se pudo conectar al simulador",
    "CONNECTION_ERROR": "Error de conexión: {error}",
    "DISCONNECTED_SUCCESS": "Desconectado del simulador",
    "DISCONNECT_ERROR": "Error al desconectar: {error}",
    "OUTPUT_CHANGED": "Configuración de salida cambiada, recreando monitor...",
    "MONITORING_STARTED": "Monitoreo iniciado",
    "ERROR_STARTING_MONITORING": "Error al iniciar el monitoreo: {error}",
    "FAILED_START_MONITORING": "No se pudo iniciar el monitoreo: {error}",
    "MONITORING_STOPPED": "Monitoreo detenido",
    "ERROR_STOPPING_MONITORING": "Error al detener el monitoreo: {error}",
    "ERROR_POLLING_DATA": "Error al sondear datos: {error}",
    "ERROR_UPDATING_DATA": "Error al actualizar la visualización de datos: {error}",
    "NOT_CONNECTED": "No conectado",
    "CONNECT_FIRST": "Conéctese al simulador primero.",
    "CONNECTION_FAILED": "Conexión fallida",
    "XPLANE_NOT_RUNNING": "X-Plane no se está ejecutando o la API REST no es accesible en {host}:{port}",
    "XPLANE_API_TIMEOUT": "Tiempo de espera agotado al conectar a la API de X-Plane en {host}:{port}",
    "XPLANE_API_ERROR": "Error de la API de X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Error de red al conectar a X-Plane: {error}",
    "REQUESTS_NOT_INSTALLED": "Módulo 'requests' no instalado",
    
    # Cuadro About
    "ABOUT_TITLE": "Acerca de Grabadora de Datos de Vuelo",
    "ABOUT_VERSION": "Versión 0.0.5",
    "ABOUT_DESCRIPTION": "Una herramienta para grabar datos de vuelo de simuladores en formato GeoJSON.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Simuladores soportados:</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (vía API REST en el puerto 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (vía SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (vía SimConnect)",
    "ABOUT_LICENSE": "<b>Licencia:</b> MIT",
    "ABOUT_AUTHOR": "<b>Autor:</b> Equipo de Desarrollo de AirRallies",
}

# Portugais
_PT_TRANSLATIONS: Dict[str, str] = {
    # Janela principal
    "FLIGHT_DATA_RECORDER_TITLE": "Gravador de Dados de Voo",
    "FILE_MENU": "Arquivo",
    "HELP_MENU": "Ajuda",
    "EXIT_ACTION": "Sair",
    "ABOUT_ACTION": "Sobre",
    
    # Menu Idioma
    "LANGUAGE_MENU": "Idioma",
    "LANGUAGE_ENGLISH": "Inglês",
    "LANGUAGE_FRENCH": "Francês",
    "LANGUAGE_ITALIAN": "Italiano",
    "LANGUAGE_SPANISH": "Espanhol",
    "LANGUAGE_PORTUGUESE": "Português",
    "LANGUAGE_GERMAN": "Alemão",
    
    # Abas
    "MAIN_TAB": "Principal",
    "ADVANCED_TAB": "Avançado",
    
    # Aba Main - Configurações do Simulador
    "SIMULATOR_SETTINGS": "Configurações do Simulador",
    "SIMULATOR_TYPE": "Tipo de simulador:",
    "SIMULATOR_XPLANE_12": "X-Plane 12",
    "SIMULATOR_MSFS_P3D": "MSFS 2020/2024 / P3D",
    "HOST": "Host:",
    "HOST_PLACEHOLDER": "Digite o endereço IP",
    "PORT": "Porta:",
    "POLL_INTERVAL": "Intervalo de coleta (s):",
    
    # Aba Main - Configurações de Saída
    "OUTPUT_SETTINGS": "Configurações de Saída",
    "OUTPUT_FILE": "Arquivo de saída:",
    "OUTPUT_FILE_PLACEHOLDER": "Selecione o caminho do arquivo de saída...",
    "BROWSE_BUTTON": "Procurar...",
    "INCLUDE_TRAJECTORY": "Incluir linha de trajetória",
    "INCLUDE_TRAJECTORY_TOOLTIP": "Adiciona um recurso LineString para visualização da trajetória no QGIS",
    "AUTO_CONNECT": "Conectar automaticamente ao iniciar",
    "AUTO_CONNECT_TOOLTIP": "Conecta automaticamente ao simulador quando o monitoramento começar",
    
    # Aba Main - Controles
    "CONTROLS": "Controles",
    "CONNECT_BUTTON": "Conectar",
    "DISCONNECT_BUTTON": "Desconectar",
    "START_MONITORING": "Iniciar Monitoramento",
    "STOP_MONITORING": "Parar Monitoramento",
    
    # Aba Main - Status
    "STATUS": "Status",
    "CONNECTION": "Conexão:",
    "CONNECTION_CONNECTED": "Conectado",
    "CONNECTION_DISCONNECTED": "Desconectado",
    "FLIGHT_STATE": "Estado de voo:",
    "FLIGHT_STATE_WAITING": "Aguardando",
    "FLIGHT_STATE_IN_FLIGHT": "Em voo",
    "FLIGHT_STATE_LANDED": "Pousado",
    "MONITORING": "Monitoramento:",
    "MONITORING_RUNNING": "Em execução",
    "MONITORING_STOPPED": "Parado",
    
    # Barra de status
    "READY": "Pronto",
    
    # Filtro de diálogo de arquivos
    "FILE_FILTER_GEOJSON": "Arquivos GeoJSON (*.json *.geojson);;Todos os arquivos (*)",
    
    # Log inicial
    "LOG_STARTUP": "Aplicação iniciada. Pronta para monitoramento.",
    
    # Aba Advanced
    "ADVANCED_TAB": "Avançado",
    "AIRCRAFT_INFORMATION": "Informações da Aeronave",
    "ICAO_CODE": "Código ICAO:",
    "AIRCRAFT_NAME": "Nome da aeronave:",
    "LIVE_DATA": "Dados em tempo real",
    "LATITUDE": "Latitude:",
    "LONGITUDE": "Longitude:",
    "ALTITUDE_MSL": "Altitude (MSL):",
    "ALTITUDE_AGL": "Altitude (AGL):",
    "HEADING": "Proa:",
    "HEADING_TRUE": "Proa (verdadeira):",
    "HEADING_MAG": "Proa (magnética):",
    "GROUND_SPEED": "Velocidade no solo:",
    "INDICATED_SPEED": "Velocidade indicada:",
    "POWER": "Potência:",
    "SIMULATION_TIME": "Hora da simulação:",
    "N_A": "N/D",
    
    # Diálogos e mensagens
    "SELECT_OUTPUT_FILE": "Selecionar arquivo de saída",
    "ERROR_NO_OUTPUT_FILE": "Erro: Nenhum arquivo de saída especificado",
    "ERROR_SPECIFY_OUTPUT_FILE": "Especifique um caminho de arquivo de saída.",
    "MONITOR_CREATED": "Monitor criado para o simulador {sim_type}",
    "ERROR_CREATING_MONITOR": "Erro ao criar o monitor: {error}",
    "FAILED_CREATE_MONITOR": "Falha ao criar o monitor: {error}",
    "CONNECTED_SUCCESS": "Conectado ao simulador com sucesso",
    "CONNECT_FAILED": "Falha ao conectar ao simulador",
    "CONNECTION_ERROR": "Erro de conexão: {error}",
    "DISCONNECTED_SUCCESS": "Desconectado do simulador",
    "DISCONNECT_ERROR": "Erro ao desconectar: {error}",
    "OUTPUT_CHANGED": "Configurações de saída alteradas, recriando monitor...",
    "MONITORING_STARTED": "Monitoramento iniciado",
    "ERROR_STARTING_MONITORING": "Erro ao iniciar o monitoramento: {error}",
    "FAILED_START_MONITORING": "Falha ao iniciar o monitoramento: {error}",
    "MONITORING_STOPPED": "Monitoramento parado",
    "ERROR_STOPPING_MONITORING": "Erro ao parar o monitoramento: {error}",
    "ERROR_POLLING_DATA": "Erro ao coletar dados: {error}",
    "ERROR_UPDATING_DATA": "Erro ao atualizar a exibição de dados: {error}",
    "NOT_CONNECTED": "Não conectado",
    "CONNECT_FIRST": "Conecte-se ao simulador primeiro.",
    "CONNECTION_FAILED": "Falha na conexão",
    "XPLANE_NOT_RUNNING": "O X-Plane não está em execução ou a API REST não está acessível em {host}:{port}",
    "XPLANE_API_TIMEOUT": "Tempo limite excedido ao conectar à API do X-Plane em {host}:{port}",
    "XPLANE_API_ERROR": "Erro na API do X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Erro de rede ao conectar ao X-Plane: {error}",
    "REQUESTS_NOT_INSTALLED": "Módulo 'requests' não instalado",
    
    # Caixa About
    "ABOUT_TITLE": "Sobre o Gravador de Dados de Voo",
    "ABOUT_VERSION": "Versão 0.0.5",
    "ABOUT_DESCRIPTION": "Uma ferramenta para gravar dados de voo de simuladores no formato GeoJSON.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Simuladores suportados:</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (via API REST na porta 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (via SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (via SimConnect)",
    "ABOUT_LICENSE": "<b>Licença:</b> MIT",
    "ABOUT_AUTHOR": "<b>Autor:</b> Equipe de Desenvolvimento AirRallies",
}

# Allemand
_DE_TRANSLATIONS: Dict[str, str] = {
    # Hauptfenster
    "FLIGHT_DATA_RECORDER_TITLE": "Flugdatenrecorder",
    "FILE_MENU": "Datei",
    "HELP_MENU": "Hilfe",
    "EXIT_ACTION": "Beenden",
    "ABOUT_ACTION": "Über",
    
    # Sprachmenü
    "LANGUAGE_MENU": "Sprache",
    "LANGUAGE_ENGLISH": "Englisch",
    "LANGUAGE_FRENCH": "Französisch",
    "LANGUAGE_ITALIAN": "Italienisch",
    "LANGUAGE_SPANISH": "Spanisch",
    "LANGUAGE_PORTUGUESE": "Portugiesisch",
    "LANGUAGE_GERMAN": "Deutsch",
    
    # Tabs
    "MAIN_TAB": "Haupt",
    "ADVANCED_TAB": "Erweitert",
    
    # Tab Main - Simulator-Einstellungen
    "SIMULATOR_SETTINGS": "Simulator-Einstellungen",
    "SIMULATOR_TYPE": "Simulator-Typ:",
    "SIMULATOR_XPLANE_12": "X-Plane 12",
    "SIMULATOR_MSFS_P3D": "MSFS 2020/2024 / P3D",
    "HOST": "Host:",
    "HOST_PLACEHOLDER": "IP-Adresse eingeben",
    "PORT": "Port:",
    "POLL_INTERVAL": "Abfrageintervall (s):",
    
    # Tab Main - Ausgabeeinstellungen
    "OUTPUT_SETTINGS": "Ausgabeeinstellungen",
    "OUTPUT_FILE": "Ausgabedatei:",
    "OUTPUT_FILE_PLACEHOLDER": "Ausgabedateipfad auswählen...",
    "BROWSE_BUTTON": "Durchsuchen...",
    "INCLUDE_TRAJECTORY": "Flugbahn-Linie einbeziehen",
    "INCLUDE_TRAJECTORY_TOOLTIP": "Fügt ein LineString-Objekt für die Flugbahnvisualisierung in QGIS hinzu",
    "AUTO_CONNECT": "Automatisch verbinden beim Start",
    "AUTO_CONNECT_TOOLTIP": "Stellt automatisch eine Verbindung zum Simulator her, wenn die Überwachung beginnt",
    
    # Tab Main - Steuerung
    "CONTROLS": "Steuerung",
    "CONNECT_BUTTON": "Verbinden",
    "DISCONNECT_BUTTON": "Trennen",
    "START_MONITORING": "Überwachung starten",
    "STOP_MONITORING": "Überwachung stoppen",
    
    # Tab Main - Status
    "STATUS": "Status",
    "CONNECTION": "Verbindung:",
    "CONNECTION_CONNECTED": "Verbunden",
    "CONNECTION_DISCONNECTED": "Getrennt",
    "FLIGHT_STATE": "Flugzustand:",
    "FLIGHT_STATE_WAITING": "Wartend",
    "FLIGHT_STATE_IN_FLIGHT": "Im Flug",
    "FLIGHT_STATE_LANDED": "Gelandet",
    "MONITORING": "Überwachung:",
    "MONITORING_RUNNING": "Läuft",
    "MONITORING_STOPPED": "Gestoppt",
    
    # Statusleiste
    "READY": "Bereit",
    
    # Dateidialog-Filter
    "FILE_FILTER_GEOJSON": "GeoJSON-Dateien (*.json *.geojson);;Alle Dateien (*)",
    
    # Start-Log
    "LOG_STARTUP": "Anwendung gestartet. Bereit für die Überwachung.",
    
    # Tab Advanced
    "ADVANCED_TAB": "Erweitert",
    "AIRCRAFT_INFORMATION": "Flugzeuginformationen",
    "ICAO_CODE": "ICAO-Code:",
    "AIRCRAFT_NAME": "Flugzeugname:",
    "LIVE_DATA": "Echtzeitdaten",
    "LATITUDE": "Breitengrad:",
    "LONGITUDE": "Längengrad:",
    "ALTITUDE_MSL": "Höhe (MSL):",
    "ALTITUDE_AGL": "Höhe (AGL):",
    "HEADING": "Kurs:",
    "HEADING_TRUE": "Kurs (wahr):",
    "HEADING_MAG": "Kurs (magnetisch):",
    "GROUND_SPEED": "Bodengeschwindigkeit:",
    "INDICATED_SPEED": "Angezeigte Geschwindigkeit:",
    "POWER": "Leistung:",
    "SIMULATION_TIME": "Simulationszeit:",
    "N_A": "N/V",
    
    # Dialoge und Nachrichten
    "SELECT_OUTPUT_FILE": "Ausgabedatei auswählen",
    "ERROR_NO_OUTPUT_FILE": "Fehler: Keine Ausgabedatei angegeben",
    "ERROR_SPECIFY_OUTPUT_FILE": "Bitte geben Sie einen Ausgabedateipfad an.",
    "MONITOR_CREATED": "Monitor für {sim_type}-Simulator erstellt",
    "ERROR_CREATING_MONITOR": "Fehler beim Erstellen des Monitors: {error}",
    "FAILED_CREATE_MONITOR": "Erstellen des Monitors fehlgeschlagen: {error}",
    "CONNECTED_SUCCESS": "Erfolgreich mit Simulator verbunden",
    "CONNECT_FAILED": "Verbindung zum Simulator fehlgeschlagen",
    "CONNECTION_ERROR": "Verbindungsfehler: {error}",
    "DISCONNECTED_SUCCESS": "Vom Simulator getrennt",
    "DISCONNECT_ERROR": "Fehler beim Trennen: {error}",
    "OUTPUT_CHANGED": "Ausgabeeinstellungen geändert, erstelle Monitor neu...",
    "MONITORING_STARTED": "Überwachung gestartet",
    "ERROR_STARTING_MONITORING": "Fehler beim Starten der Überwachung: {error}",
    "FAILED_START_MONITORING": "Starten der Überwachung fehlgeschlagen: {error}",
    "MONITORING_STOPPED": "Überwachung gestoppt",
    "ERROR_STOPPING_MONITORING": "Fehler beim Stoppen der Überwachung: {error}",
    "ERROR_POLLING_DATA": "Fehler beim Abfragen der Daten: {error}",
    "ERROR_UPDATING_DATA": "Fehler beim Aktualisieren der Datenanzeige: {error}",
    "NOT_CONNECTED": "Nicht verbunden",
    "CONNECT_FIRST": "Bitte verbinden Sie sich zuerst mit dem Simulator.",
    "CONNECTION_FAILED": "Verbindung fehlgeschlagen",
    "XPLANE_NOT_RUNNING": "X-Plane läuft nicht oder die REST-API ist unter {host}:{port} nicht zugänglich",
    "XPLANE_API_TIMEOUT": "Zeitüberschreitung bei der Verbindung zur X-Plane-API unter {host}:{port}",
    "XPLANE_API_ERROR": "X-Plane-API-Fehler: {error}",
    "XPLANE_NETWORK_ERROR": "Netzwerkfehler bei der Verbindung zu X-Plane: {error}",
    "REQUESTS_NOT_INSTALLED": "Modul 'requests' nicht installiert",
    
    # Info-Fenster
    "ABOUT_TITLE": "Über Flugdatenrecorder",
    "ABOUT_VERSION": "Version 0.0.5",
    "ABOUT_DESCRIPTION": "Ein Tool zum Aufzeichnen von Flugdaten aus Flugsimulatoren im GeoJSON-Format.",
    "ABOUT_SUPPORTED_SIMULATORS": "<b>Unterstützte Simulatoren:</b>",
    "ABOUT_SIMULATOR_XPLANE": "X-Plane 12 (über REST-API auf Port 8086)",
    "ABOUT_SIMULATOR_MSFS": "Microsoft Flight Simulator 2020/2024 (über SimConnect)",
    "ABOUT_SIMULATOR_P3D": "Prepar3D (über SimConnect)",
    "ABOUT_LICENSE": "<b>Lizenz:</b> MIT",
    "ABOUT_AUTHOR": "<b>Autor:</b> AirRallies Entwicklungs-Team",
}

# Dictionnaire des traductions disponibles
_AVAILABLE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": _FR_TRANSLATIONS,
    "en": _EN_TRANSLATIONS,
    "it": _IT_TRANSLATIONS,
    "es": _ES_TRANSLATIONS,
    "pt": _PT_TRANSLATIONS,
    "de": _DE_TRANSLATIONS,
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
            
            # Copier les callbacks à appeler (pour éviter deadlock)
            callbacks_to_call = self._retranslate_callbacks.copy()
            lang_to_pass = lang
        
        # Appeler les callbacks EN DEHORS du lock pour éviter deadlock
        # (les callbacks peuvent appeler get_language() qui prend le lock)
        if old_lang != lang:
            for callback in callbacks_to_call:
                try:
                    callback(lang_to_pass)
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
                # Détecter la langue système - faire ça en dehors du lock serait mieux
                # mais on est déjà dans le lock, donc on continue
                lang = self._detect_system_language()
                if lang not in _AVAILABLE_TRANSLATIONS and lang not in self._custom_translations:
                    lang = "en"
                self._current_language = lang
            
            # Fusionner les traductions disponibles
            translations = _AVAILABLE_TRANSLATIONS.get(lang, {}).copy()
            translations.update(self._custom_translations.get(lang, {}))
            
            # Récupérer le message
            message_template = translations.get(message_id, message_id)
        
        # Formater avec les kwargs si nécessaire (en dehors du lock pour éviter blocage)
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
