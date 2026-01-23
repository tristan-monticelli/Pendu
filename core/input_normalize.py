"""Normalisation des entrees clavier - A IMPLEMENTER"""

import pygame

#--------------------------------------Normalisation--------------------------------------#

def normalize_letter_input(event) -> str:
    """
    Normalise une touche clavier en lettre majuscule
    A IMPLEMENTER: Verifier si c'est A-Z, retourner en majuscule
    Retourne: lettre majuscule ou "" si pas une lettre
    """
    pass  # TODO: Implementer
    return ""

def is_valid_letter_event(event) -> bool:
    """
    Verifie si l'evenement est une lettre valide (A-Z)
    A IMPLEMENTER: Verifier event.type et event.key
    """
    pass  # TODO: Implementer
    return False

#--------------------------------------Caracteres speciaux--------------------------------------#

def is_backspace(event) -> bool:
    """Verifie si c'est la touche retour arriere"""
    pass  # TODO: Implementer
    return False

def is_enter(event) -> bool:
    """Verifie si c'est la touche entree"""
    pass  # TODO: Implementer
    return False

def is_escape(event) -> bool:
    """Verifie si c'est la touche echap"""
    pass  # TODO: Implementer
    return False
