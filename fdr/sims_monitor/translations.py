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

# Italien
_IT_TRANSLATIONS: Dict[str, str] = {
    # GeoJSONWriter errors
    "FILE_PATH_EMPTY": "Il percorso del file non può essere vuoto",
    "LATITUDE_MISSING": "Latitudine mancante",
    "LATITUDE_INVALID": "Latitudine non valida: {value}",
    "LATITUDE_OUT_OF_RANGE": "Latitudine fuori intervallo: {result} (deve essere compresa tra -90 e 90)",
    "LONGITUDE_MISSING": "Longitudine mancante",
    "LONGITUDE_INVALID": "Longitudine non valida: {value}",
    "LONGITUDE_OUT_OF_RANGE": "Longitudine fuori intervallo: {result} (deve essere compresa tra -180 e 180)",
    
    # BaseSimulatorMonitor messages
    "TAKEOFF_DETECTED": "Decollo rilevato - Registrazione avviata",
    "LANDING_DETECTED": "Atterraggio rilevato - Registrazione fermata",
    "CONNECTED_WAITING_TAKEOFF": "Connesso al simulatore - In attesa di decollo",
    "INITIAL_CONNECTION_FAILED": "Connessione iniziale al simulatore non riuscita",
    "DATA_RETRIEVAL_ERROR": "Errore durante il recupero dei dati: {error}",
    "DISCONNECTED": "Disconnesso",
    "MONITORING_STOPPED": "Monitoraggio fermato",
    
    # MSFSMonitor errors
    "SIMCONNECT_NOT_INSTALLED": "Modulo SimConnect non installato (solo Windows)",
    "SIMCONNECT_CONNECTION_FAILED": "Connessione SimConnect fallita: {error}",
    
    # XPlaneMonitor errors
    "REQUESTS_NOT_INSTALLED": "Modulo 'requests' non installato",
    "XPLANE_CONNECTION_FAILED": "Connessione a X-Plane fallita: {error}",
    "XPLANE_NOT_RUNNING": "X-Plane non è in esecuzione o l'API REST non è accessibile su {host}:{port}",
    "XPLANE_API_TIMEOUT": "Timeout durante la connessione all'API X-Plane su {host}:{port}",
    "XPLANE_API_ERROR": "Errore API X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Errore di rete durante la connessione a X-Plane: {error}",
    "XPLANE_WRONG_ENDPOINT": "Impossibile connettersi all'API X-Plane su {host}:{port}. Verificare che il plugin X-Plane Connect sia installato o che l'API nativa sia abilitata nelle impostazioni di X-Plane.",
    "XPLANE_CHECK_HTTP_SERVER": "Verificare che 'Enable HTTP Server' sia attivato in Impostazioni > Rete di X-Plane (porta predefinita: 8080).",
    "XPLANE_INCOMING_TRAFFIC_DISABLED": "Il traffico in entrata è disabilitato nelle impostazioni di rete di X-Plane. Abilitare 'Allow Incoming Traffic' in Impostazioni > Rete.",
    "XPLANE_INVALID_API_RESPONSE_FORMAT": "Formato di risposta API X-Plane non valido.",
    "XPLANE_DATAREF_TIMEOUT": "Timeout durante la lettura della dataref {key} (ID: {id}).",
    "XPLANE_HTTP_ERROR": "Errore HTTP {status} durante la connessione a X-Plane.",
    
    # _XPlaneAPI errors
    "DATAREF_NOT_FOUND": "Dataref non trovata: {path}",
    "XPLANE_INVALID_API_RESPONSE": "Risposta API X-Plane non valida: {error}",
    
    # create_monitor errors
    "UNKNOWN_SIMULATOR_TYPE": "Tipo di simulatore sconosciuto: '{simulator_type}'. Usare '{msfs}' o '{xplane}'",
}

# Espagnol
_ES_TRANSLATIONS: Dict[str, str] = {
    # GeoJSONWriter errors
    "FILE_PATH_EMPTY": "La ruta del archivo no puede estar vacía",
    "LATITUDE_MISSING": "Latitud faltante",
    "LATITUDE_INVALID": "Latitud no válida: {value}",
    "LATITUDE_OUT_OF_RANGE": "Latitud fuera de rango: {result} (debe estar entre -90 y 90)",
    "LONGITUDE_MISSING": "Longitud faltante",
    "LONGITUDE_INVALID": "Longitud no válida: {value}",
    "LONGITUDE_OUT_OF_RANGE": "Longitud fuera de rango: {result} (debe estar entre -180 y 180)",
    
    # BaseSimulatorMonitor messages
    "TAKEOFF_DETECTED": "Despegue detectado - Grabación iniciada",
    "LANDING_DETECTED": "Aterrizaje detectado - Grabación detenida",
    "CONNECTED_WAITING_TAKEOFF": "Conectado al simulador - Esperando despegue",
    "INITIAL_CONNECTION_FAILED": "Conexión inicial al simulador fallida",
    "DATA_RETRIEVAL_ERROR": "Error al recuperar datos: {error}",
    "DISCONNECTED": "Desconectado",
    "MONITORING_STOPPED": "Monitoreo detenido",
    
    # MSFSMonitor errors
    "SIMCONNECT_NOT_INSTALLED": "Módulo SimConnect no instalado (solo Windows)",
    "SIMCONNECT_CONNECTION_FAILED": "Conexión SimConnect fallida: {error}",
    
    # XPlaneMonitor errors
    "REQUESTS_NOT_INSTALLED": "Módulo 'requests' no instalado",
    "XPLANE_CONNECTION_FAILED": "Conexión a X-Plane fallida: {error}",
    "XPLANE_NOT_RUNNING": "X-Plane no se está ejecutando o la API REST no es accesible en {host}:{port}",
    "XPLANE_API_TIMEOUT": "Tiempo de espera agotado al conectar a la API de X-Plane en {host}:{port}",
    "XPLANE_API_ERROR": "Error de la API de X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Error de red al conectar a X-Plane: {error}",
    "XPLANE_WRONG_ENDPOINT": "No se puede conectar a la API de X-Plane en {host}:{port}. Verifique que el plugin X-Plane Connect esté instalado o que la API nativa esté habilitada en Configuración > Red de X-Plane.",
    "XPLANE_CHECK_HTTP_SERVER": "Verifique que 'Enable HTTP Server' esté activado en Configuración > Red de X-Plane (puerto predeterminado: 8080).",
    "XPLANE_INCOMING_TRAFFIC_DISABLED": "El tráfico entrante está deshabilitado en la configuración de red de X-Plane. Active 'Allow Incoming Traffic' en Configuración > Red.",
    "XPLANE_INVALID_API_RESPONSE_FORMAT": "Formato de respuesta de la API de X-Plane no válido.",
    "XPLANE_DATAREF_TIMEOUT": "Tiempo de espera agotado al leer la dataref {key} (ID: {id}).",
    "XPLANE_HTTP_ERROR": "Error HTTP {status} al conectar a X-Plane.",
    
    # _XPlaneAPI errors
    "DATAREF_NOT_FOUND": "Dataref no encontrada: {path}",
    "XPLANE_INVALID_API_RESPONSE": "Respuesta de la API de X-Plane no válida: {error}",
    
    # create_monitor errors
    "UNKNOWN_SIMULATOR_TYPE": "Tipo de simulador desconocido: '{simulator_type}'. Use '{msfs}' o '{xplane}'",
}

# Portugais
_PT_TRANSLATIONS: Dict[str, str] = {
    # GeoJSONWriter errors
    "FILE_PATH_EMPTY": "O caminho do arquivo não pode estar vazio",
    "LATITUDE_MISSING": "Latitude ausente",
    "LATITUDE_INVALID": "Latitude inválida: {value}",
    "LATITUDE_OUT_OF_RANGE": "Latitude fora do intervalo: {result} (deve estar entre -90 e 90)",
    "LONGITUDE_MISSING": "Longitude ausente",
    "LONGITUDE_INVALID": "Longitude inválida: {value}",
    "LONGITUDE_OUT_OF_RANGE": "Longitude fora do intervalo: {result} (deve estar entre -180 e 180)",
    
    # BaseSimulatorMonitor messages
    "TAKEOFF_DETECTED": "Decolagem detectada - Gravação iniciada",
    "LANDING_DETECTED": "Pouso detectado - Gravação parada",
    "CONNECTED_WAITING_TAKEOFF": "Conectado ao simulador - Aguardando decolagem",
    "INITIAL_CONNECTION_FAILED": "Falha na conexão inicial com o simulador",
    "DATA_RETRIEVAL_ERROR": "Erro ao recuperar dados: {error}",
    "DISCONNECTED": "Desconectado",
    "MONITORING_STOPPED": "Monitoramento parado",
    
    # MSFSMonitor errors
    "SIMCONNECT_NOT_INSTALLED": "Módulo SimConnect não instalado (somente Windows)",
    "SIMCONNECT_CONNECTION_FAILED": "Falha na conexão SimConnect: {error}",
    
    # XPlaneMonitor errors
    "REQUESTS_NOT_INSTALLED": "Módulo 'requests' não instalado",
    "XPLANE_CONNECTION_FAILED": "Falha na conexão com X-Plane: {error}",
    "XPLANE_NOT_RUNNING": "O X-Plane não está em execução ou a API REST não está acessível em {host}:{port}",
    "XPLANE_API_TIMEOUT": "Tempo limite excedido ao conectar à API do X-Plane em {host}:{port}",
    "XPLANE_API_ERROR": "Erro na API do X-Plane: {error}",
    "XPLANE_NETWORK_ERROR": "Erro de rede ao conectar ao X-Plane: {error}",
    "XPLANE_WRONG_ENDPOINT": "Impossível conectar à API do X-Plane em {host}:{port}. Verifique se o plugin X-Plane Connect está instalado ou se a API nativa está habilitada em Configurações > Rede do X-Plane.",
    "XPLANE_CHECK_HTTP_SERVER": "Verifique se 'Enable HTTP Server' está ativado em Configurações > Rede do X-Plane (porta padrão: 8080).",
    "XPLANE_INCOMING_TRAFFIC_DISABLED": "O tráfego de entrada está desabilitado nas configurações de rede do X-Plane. Ative 'Allow Incoming Traffic' em Configurações > Rede.",
    "XPLANE_INVALID_API_RESPONSE_FORMAT": "Formato de resposta da API do X-Plane inválido.",
    "XPLANE_DATAREF_TIMEOUT": "Tempo limite excedido ao ler a dataref {key} (ID: {id}).",
    "XPLANE_HTTP_ERROR": "Erro HTTP {status} ao conectar ao X-Plane.",
    
    # _XPlaneAPI errors
    "DATAREF_NOT_FOUND": "Dataref não encontrada: {path}",
    "XPLANE_INVALID_API_RESPONSE": "Resposta da API do X-Plane inválida: {error}",
    
    # create_monitor errors
    "UNKNOWN_SIMULATOR_TYPE": "Tipo de simulador desconhecido: '{simulator_type}'. Use '{msfs}' ou '{xplane}'",
}

# Allemand
_DE_TRANSLATIONS: Dict[str, str] = {
    # GeoJSONWriter errors
    "FILE_PATH_EMPTY": "Der Dateipfad darf nicht leer sein",
    "LATITUDE_MISSING": "Breitengrad fehlt",
    "LATITUDE_INVALID": "Ungültiger Breitengrad: {value}",
    "LATITUDE_OUT_OF_RANGE": "Breitengrad außer Bereich: {result} (muss zwischen -90 und 90 liegen)",
    "LONGITUDE_MISSING": "Längengrad fehlt",
    "LONGITUDE_INVALID": "Ungültiger Längengrad: {value}",
    "LONGITUDE_OUT_OF_RANGE": "Längengrad außer Bereich: {result} (muss zwischen -180 und 180 liegen)",
    
    # BaseSimulatorMonitor messages
    "TAKEOFF_DETECTED": "Start erkannt - Aufzeichnung gestartet",
    "LANDING_DETECTED": "Landung erkannt - Aufzeichnung gestoppt",
    "CONNECTED_WAITING_TAKEOFF": "Mit Simulator verbunden - Warte auf Start",
    "INITIAL_CONNECTION_FAILED": "Erste Verbindung zum Simulator fehlgeschlagen",
    "DATA_RETRIEVAL_ERROR": "Fehler beim Abrufen der Daten: {error}",
    "DISCONNECTED": "Getrennt",
    "MONITORING_STOPPED": "Überwachung gestoppt",
    
    # MSFSMonitor errors
    "SIMCONNECT_NOT_INSTALLED": "SimConnect-Modul nicht installiert (nur Windows)",
    "SIMCONNECT_CONNECTION_FAILED": "SimConnect-Verbindung fehlgeschlagen: {error}",
    
    # XPlaneMonitor errors
    "REQUESTS_NOT_INSTALLED": "Modul 'requests' nicht installiert",
    "XPLANE_CONNECTION_FAILED": "Verbindung zu X-Plane fehlgeschlagen: {error}",
    "XPLANE_NOT_RUNNING": "X-Plane läuft nicht oder die REST-API ist unter {host}:{port} nicht zugänglich",
    "XPLANE_API_TIMEOUT": "Zeitüberschreitung bei der Verbindung zur X-Plane-API unter {host}:{port}",
    "XPLANE_API_ERROR": "X-Plane-API-Fehler: {error}",
    "XPLANE_NETWORK_ERROR": "Netzwerkfehler bei der Verbindung zu X-Plane: {error}",
    "XPLANE_WRONG_ENDPOINT": "Kann nicht zur X-Plane-API unter {host}:{port} verbinden. Überprüfen Sie, ob das X-Plane Connect-Plugin installiert ist oder die native HTTP-Server-API in den X-Plane-Einstellungen > Netzwerk aktiviert ist.",
    "XPLANE_CHECK_HTTP_SERVER": "Überprüfen Sie, ob 'Enable HTTP Server' in X-Plane Einstellungen > Netzwerk aktiviert ist (Standardport: 8080).",
    "XPLANE_INCOMING_TRAFFIC_DISABLED": "Eingehender Datenverkehr ist in den X-Plane-Netzwerkeinstellungen deaktiviert. Aktivieren Sie 'Allow Incoming Traffic' in Einstellungen > Netzwerk.",
    "XPLANE_INVALID_API_RESPONSE_FORMAT": "Ungültiges X-Plane-API-Antwortformat.",
    "XPLANE_DATAREF_TIMEOUT": "Zeitüberschreitung beim Lesen der Dataref {key} (ID: {id}).",
    "XPLANE_HTTP_ERROR": "HTTP-Fehler {status} bei der Verbindung zu X-Plane.",
    
    # _XPlaneAPI errors
    "DATAREF_NOT_FOUND": "Dataref nicht gefunden: {path}",
    "XPLANE_INVALID_API_RESPONSE": "Ungültige X-Plane-API-Antwort: {error}",
    
    # create_monitor errors
    "UNKNOWN_SIMULATOR_TYPE": "Unbekannter Simulator-Typ: '{simulator_type}'. Verwenden Sie '{msfs}' oder '{xplane}'",
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
