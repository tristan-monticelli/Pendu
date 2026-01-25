"""
Ce module sert de "porte d'entrée" vers le fichier data/mots.txt.
Il est utilisé par :
- la scène de jeu : pour charger des mots selon la difficulté + récupérer les indices
- la scène "Ajouter un mot" : pour valider un mot saisi et l'ajouter au fichier

Format supporté (deux formats possibles)
1) Ancien format (compatibilité) :
   - 1 mot par ligne
   Exemple :
   pomme
   voiture

2) Nouveau format (avec difficulté + indices) :
   - DIFFICULTE;mot;indice1;indice2;indice3
   Exemple :
   FACILE;chien;animal;aboie;compagnon
   MOYEN;ordinateur;machine;clavier;ecran
   DIFFICILE;cryptographie;secret;code;mathematiques

Règles côté "mot" (validate_word)
- pas d'espaces
- pas de ';' (car c'est notre séparateur)
- minuscule (normalisation)
- uniquement des lettres (pas de chiffres / symboles)

Fonctions principales
- load_words(path) -> list[str]
  Charge tous les mots, toutes difficultés confondues (utile pour vérifier les doublons).

- load_words_by_difficulty(path, difficulty) -> (words, hints_dict)
  Charge uniquement une difficulté, et prépare un dictionnaire d'indices par mot.

- validate_word(raw_word) -> (ok, normalized_word, message)
  Validation simple d'un mot saisi dans l'UI.

- add_word(path, raw_word) -> (ok, message)
  Ajoute un mot validé au fichier, en évitant les doublons.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def load_words(path: str) -> List[str]:
    """
    Charger tous les mots disponibles (tous niveaux mélangés).

    Cette fonction sert surtout à :
    - alimenter des listes simples de mots
    - vérifier les doublons quand on veut ajouter un mot

    Comportements importants
    - Si le fichier est absent : on renvoie [] (pas d'erreur bloquante).
    - On ignore les lignes vides et les commentaires (lignes qui commencent par '#').
    - On accepte deux formats :
      * "mot" (ancien format)
      * "DIFFICULTE;mot;..." (nouveau format) -> on récupère uniquement la colonne "mot"

    Args:
        path: chemin vers le fichier mots.txt

    Returns:
        Liste de mots en minuscules.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    words: List[str] = []
    for line in lines:
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue

        # Nouveau format : DIFF;mot;... -> on récupère la partie "mot"
        if ";" in raw:
            parts = raw.split(";")
            if len(parts) >= 2:
                w = parts[1].strip().lower()
            else:
                # Ligne mal formée : on ignore
                continue
        else:
            # Ancien format : mot seul
            w = raw.lower()

        if not w:
            continue
        words.append(w)

    return words


def load_words_by_difficulty(path: str, difficulty: str) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Charger uniquement les mots d'une difficulté donnée + leurs indices.

    On ne lit ici que le NOUVEAU FORMAT, parce que l'ancien ne contient pas la difficulté.
    Concrètement :
    - les lignes sans ';' sont ignorées
    - on filtre sur la difficulté demandée
    - on prépare :
      * words : liste des mots pour la difficulté
      * hints : dict {mot: [indice1, indice2, indice3]} (liste pouvant être plus courte)

    Args:
        path: chemin vers le fichier mots.txt
        difficulty: "FACILE", "MOYEN" ou "DIFFICILE" (insensible aux espaces et à la casse)

    Returns:
        (words, hints)
        - words: list[str]
        - hints: dict[str, list[str]] où la liste contient 1 à 3 indices si présents
    """
    # On normalise la difficulté pour comparer correctement avec le fichier.
    difficulty = (difficulty or "").strip().upper()

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return [], {}

    words: List[str] = []
    hints: Dict[str, List[str]] = {}

    for line in lines:
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue

        # Ici, on ne traite que le nouveau format (avec ';')
        if ";" not in raw:
            continue

        parts = raw.split(";")
        diff = parts[0].strip().upper()

        # On garde uniquement la difficulté demandée
        if diff != difficulty:
            continue

        # On veut au minimum : DIFF;mot
        if len(parts) < 2:
            continue

        word = parts[1].strip().lower()
        if not word:
            continue

        words.append(word)

        # Indices : positions 2, 3, 4 si elles existent.
        # On ne force pas à 3 indices : si le fichier en a moins, on prend ce qu'il y a.
        word_hints = []
        for i in range(2, min(5, len(parts))):
            hint = parts[i].strip()
            if hint:
                # On stocke l'indice tel quel.
                # (Si on veut transformer des '_' en espaces, ce serait à faire ailleurs.)
                word_hints.append(hint)

        # On ne met le mot dans hints que si on a au moins un indice non vide
        if word_hints:
            hints[word] = word_hints

    return words, hints


def validate_word(raw_word: str) -> Tuple[bool, str, str]:
    """
    Valider un mot saisi par un joueur (ex: depuis AddWordScene).

    Objectif
    - Renforcer un minimum la qualité du fichier mots.txt
    - Éviter les entrées impossibles à jouer (espaces, symboles, etc.)

    Args:
        raw_word: texte brut (peut être None, peut contenir des espaces)

    Returns:
        (ok, normalized, message)
        - ok: bool (True si valide)
        - normalized: mot en minuscules, sans espaces en début/fin
        - message: texte "humain" pour l'UI (toast)
    """
    if raw_word is None:
        return False, "", "Mot vide"

    # Normalisation simple : on convertit en str, on enlève les espaces autour, on met en minuscule
    word = str(raw_word).strip().lower()

    if not word:
        return False, "", "Le mot ne peut pas être vide"

    # On interdit les espaces à l'intérieur du mot (pendu = un seul mot)
    if " " in word:
        return False, "", "Le mot ne doit pas contenir d'espaces"

    # On interdit ';' car c'est notre séparateur dans le fichier
    if ";" in word:
        return False, "", "Caractère interdit : ;"

    # On veut uniquement des lettres (pas de chiffres, pas de tirets, pas d'accents gérés ici)
    if not word.isalpha():
        return False, "", "Le mot doit contenir uniquement des lettres"

    return True, word, "Mot valide"


def add_word(path: str, raw_word: str) -> Tuple[bool, str]:
    """
    Ajouter un mot dans le fichier mots.txt (si valide et non-duplicaté).

    Choix du projet
    - Pour rester simple, on ajoute en difficulté MOYEN.
    - On n'ajoute pas d'indices depuis l'UI (donc la ligne ajoutée ne contient que DIFF;mot).

    Étapes
    1) validate_word : vérifie la saisie + normalise le mot
    2) load_words : charge tous les mots existants pour éviter les doublons
    3) append dans le fichier (en gérant proprement la présence/absence de newline en fin de fichier)

    Args:
        path: chemin vers mots.txt
        raw_word: mot saisi dans l'interface

    Returns:
        (ok, message)
        - ok: True si ajout effectué
        - message: message pour l'utilisateur (toast)
    """
    ok, word, msg = validate_word(raw_word)
    if not ok:
        return False, msg

    # On vérifie les doublons sur tous les mots, toutes difficultés confondues
    existing = load_words(path)
    if word in existing:
        return False, "Mot déjà présent"

    # Écriture : ici on ajoute en MOYEN et sans indices
    line_to_write = f"MOYEN;{word}"

    # Append propre : si le fichier ne finit pas par \n, on en ajoute un avant d'écrire la nouvelle ligne.
    try:
        try:
            # On ouvre en binaire juste pour lire le dernier octet sans se soucier de l'encodage.
            with open(path, "rb") as fb:
                fb.seek(0, 2)  # fin de fichier
                size = fb.tell()
                needs_newline = False
                if size > 0:
                    fb.seek(-1, 2)  # dernier caractère
                    last = fb.read(1)
                    needs_newline = last != b"\n"
        except FileNotFoundError:
            # Si le fichier n'existe pas, on le créera en mode "a"
            needs_newline = False

        with open(path, "a", encoding="utf-8") as f:
            if needs_newline:
                f.write("\n")
            f.write(line_to_write + "\n")

    except OSError:
        # Erreur générique d'accès disque (permissions, chemin invalide, etc.)
        return False, "Erreur lors de l'écriture du fichier mots.txt"

    return True, "Mot ajouté (niveau MOYEN)"
