"""
Module de traduction pour sim_monitor.

Ce module fournit un système d'internationalisation (i18n) pour tous les
messages destinés à l'utilisateur dans le module sim_monitor.

Ce système utilise des dictionnaires Python simples pour les traductions,
ce qui le rend portable sans nécessiter l'installation de gettext.

Utilisation :
    from translations import gettext as _, set_language, get_language
    
    # Dans le code
    message = _("Connecté au simulateur")
    
    # Pour changer de langue
    set_language("en")  # Anglais
    set_language("fr")  # Français
    
    # Pour ajouter une nouvelle langue
    add_translations("es", {
        "Connecté au simulateur": "Conectado al simulador",
        # ... autres traductions
    })

Les traductions sont chargées depuis des dictionnaires Python.
"""

import os
import threading
import re
from typing import Optional, Dict

# ---------------------------------------------------------------------------
# Dictionnaires de traduction
# ---------------------------------------------------------------------------

# Français (langue par défaut)
_FR_TRANSLATIONS: Dict[str, str] = {
    # Messages from GeoJSONWriter
    "Le chemin du fichier ne peut pas être vide": "Le chemin du fichier ne peut pas être vide",
    "Latitude manquante": "Latitude manquante",
    "Longitude manquante": "Longitude manquante",
    "Latitude invalide: {value}": "Latitude invalide: {value}",
    "Latitude hors plage: {result} (doit être entre -90 et 90)": "Latitude hors plage: {result} (doit être entre -90 et 90)",
    "Longitude invalide: {value}": "Longitude invalide: {value}",
    "Longitude hors plage: {result} (doit être entre -180 et 180)": "Longitude hors plage: {result} (doit être entre -180 et 180)",
    
    # Messages from BaseSimulatorMonitor
    "Décollage détecté - Enregistrement démarré": "Décollage détecté - Enregistrement démarré",
    "Atterrissage détecté - Enregistrement arrêté": "Atterrissage détecté - Enregistrement arrêté",
    "Connecté au simulateur - En attente de décollage": "Connecté au simulateur - En attente de décollage",
    "Échec de la connexion initiale au simulateur": "Échec de la connexion initiale au simulateur",
    "Erreur lors de la récupération des données: {error}": "Erreur lors de la récupération des données: {error}",
    "Déconnecté": "Déconnecté",
    "Monitoring arrêté": "Monitoring arrêté",
    
    # Messages from MSFSMonitor
    "Module SimConnect non installé (Windows uniquement)": "Module SimConnect non installé (Windows uniquement)",
    "Échec de connexion SimConnect: {error}": "Échec de connexion SimConnect: {error}",
    
    # Messages from XPlaneMonitor
    "Module 'requests' non installé": "Module 'requests' non installé",
    "Échec de connexion X-Plane: {error}": "Échec de connexion X-Plane: {error}",
}

# Anglais
_EN_TRANSLATIONS: Dict[str, str] = {
    # Messages from GeoJSONWriter
    "Le chemin du fichier ne peut pas être vide": "File path cannot be empty",
    "Latitude manquante": "Missing latitude",
    "Longitude manquante": "Missing longitude",
    "Latitude invalide: {value}": "Invalid latitude: {value}",
    "Latitude hors plage: {result} (doit être entre -90 et 90)": "Latitude out of range: {result} (must be between -90 and 90)",
    "Longitude invalide: {value}": "Invalid longitude: {value}",
    "Longitude hors plage: {result} (doit être entre -180 et 180)": "Longitude out of range: {result} (must be between -180 and 180)",
    
    # Messages from BaseSimulatorMonitor
    "Décollage détecté - Enregistrement démarré": "Takeoff detected - Recording started",
    "Atterrissage détecté - Enregistrement arrêté": "Landing detected - Recording stopped",
    "Connecté au simulateur - En attente de décollage": "Connected to simulator - Waiting for takeoff",
    "Échec de la connexion initiale au simulateur": "Initial connection to simulator failed",
    "Erreur lors de la récupération des données: {error}": "Error retrieving data: {error}",
    "Déconnecté": "Disconnected",
    "Monitoring arrêté": "Monitoring stopped",
    
    # Messages from MSFSMonitor
    "Module SimConnect non installé (Windows uniquement)": "SimConnect module not installed (Windows only)",
    "Échec de connexion SimConnect: {error}": "SimConnect connection failed: {error}",
    
    # Messages from XPlaneMonitor
    "Module 'requests' non installé": "'requests' module not installed",
    "Échec de connexion X-Plane: {error}": "X-Plane connection failed: {error}",
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
    """
    Gère le chargement et la sélection des traductions.
    
    Thread-safe pour une utilisation dans des environnements multi-threads.
    """
    
    _instance: Optional['TranslationManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern pour le gestionnaire de traductions."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._current_language: Optional[str] = None
                cls._instance._custom_translations: Dict[str, Dict[str, str]] = {}
            return cls._instance
    
    def set_language(self, lang: Optional[str] = None) -> None:
        """
        Définit la langue active pour les traductions.
        
        Args:
            lang: Code de langue (ex: "fr", "en", None pour la langue système)
        """
        with self._lock:
            if lang is None:
                # Détecter la langue système
                import locale
                try:
                    lang = locale.getdefaultlocale()[0]
                except Exception:
                    lang = None
                
                if lang is None:
                    lang = "en"  # Default to English
                else:
                    lang = lang[:2]  # Prendre seulement le code langue (ex: "fr_FR" -> "fr")
            
            # Vérifier si la langue existe
            if lang not in _AVAILABLE_TRANSLATIONS and lang not in self._custom_translations:
                # Si la langue n'est pas disponible, utiliser l'anglais par défaut
                lang = "en"
            
            self._current_language = lang
    
    def get_current_language(self) -> Optional[str]:
        """Retourne la langue actuellement active."""
        return self._current_language
    
    def add_translations(self, lang: str, translations: Dict[str, str]) -> None:
        """
        Ajoute des traductions personnalisées pour une langue.
        
        Args:
            lang: Code de langue (ex: "es", "de")
            translations: Dictionnaire de traductions {original: traduit}
        """
        with self._lock:
            self._custom_translations[lang] = translations
    
    def gettext(self, message: str, **kwargs) -> str:
        """
        Traduit un message dans la langue active.
        
        Args:
            message: Message à traduire (peut contenir des placeholders comme {error})
            **kwargs: Arguments pour formater le message
            
        Returns:
            Message traduit et formaté
        """
        with self._lock:
            lang = self._current_language
            
            # Si aucune langue n'est définie, utiliser la langue système
            if lang is None:
                self.set_language()
                lang = self._current_language
            
            # Trouver la traduction
            translations = _AVAILABLE_TRANSLATIONS.get(lang, {}).copy()
            translations.update(self._custom_translations.get(lang, {}))
            
            translated = translations.get(message, message)
            
            # Formater le message avec les arguments fournis
            if kwargs:
                try:
                    return translated.format(**kwargs)
                except (KeyError, ValueError):
                    # Si le formatage échoue, retourner la traduction sans formatage
                    return translated
            
            return translated


# ---------------------------------------------------------------------------
# Instance singleton et fonctions utilitaires
# ---------------------------------------------------------------------------

# Créer l'instance singleton
_translation_manager = TranslationManager()

# Définir la langue par défaut (français)
_translation_manager.set_language("fr")


def set_language(lang: Optional[str] = None) -> None:
    """
    Définit la langue active.
    
    Args:
        lang: Code de langue (ex: "fr", "en", None pour la langue système)
    """
    _translation_manager.set_language(lang)


def get_language() -> Optional[str]:
    """Retourne la langue actuellement active."""
    return _translation_manager.get_current_language()


def gettext(message: str, **kwargs) -> str:
    """
    Traduit un message dans la langue active.
    
    Cette fonction doit être importée sous le nom '_' dans les modules.
    
    Args:
        message: Message à traduire
        **kwargs: Arguments pour formater le message (ex: error="Erreur")
        
    Returns:
        Message traduit et formaté
    """
    return _translation_manager.gettext(message, **kwargs)


def add_translations(lang: str, translations: Dict[str, str]) -> None:
    """
    Ajoute des traductions personnalisées pour une langue.
    
    Args:
        lang: Code de langue (ex: "es", "de")
        translations: Dictionnaire de traductions {original: traduit}
    """
    _translation_manager.add_translations(lang, translations)


# Alias pour une utilisation standard
_ = gettext
