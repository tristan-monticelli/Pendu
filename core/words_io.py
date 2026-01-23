"""Lecture/ecriture du fichier de mots - A IMPLEMENTER"""

from typing import List, Tuple
from settings import PATHS

#--------------------------------------Chargement--------------------------------------#

def load_words() -> List[str]:
    """
    Charge la liste de mots depuis mots.txt
    A IMPLEMENTER: Lire le fichier, retourner liste de mots en majuscules
    """
    pass  # TODO: Implementer
    return ["TEST"]

def _create_default_words_file(filepath: str):
    """Cree le fichier de mots avec des mots par defaut"""
    pass  # TODO: Implementer

#--------------------------------------Ajout--------------------------------------#

def add_word(word: str) -> Tuple[bool, str]:
    """
    Ajoute un mot au fichier
    A IMPLEMENTER: Valider, verifier doublon, ajouter au fichier
    Retourne: (succes, message)
    """
    pass  # TODO: Implementer
    return False, "Non implemente"

#--------------------------------------Validation--------------------------------------#

def validate_word(word: str) -> Tuple[bool, str]:
    """
    Valide un mot avant ajout
    A IMPLEMENTER: Verifier longueur (2-30), pas d'espaces, lettres uniquement
    Retourne: (valide, message_erreur)
    """
    pass  # TODO: Implementer
    return True, ""
