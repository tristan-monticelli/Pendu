"""
Objectif
- Mesurer le temps écoulé pendant une partie, sans dépendre directement de Pygame.
- On passe une fonction "get_ticks_func" en paramètre (injection de dépendance).
  Exemple typique : pygame.time.get_ticks (renvoie des millisecondes).

Pourquoi ce design
- Le module reste simple à tester : on peut fournir une fonction "fake" en test.
- On évite d'avoir du code Pygame partout : la scène de jeu appelle juste ces helpers.

Convention
- Les ticks sont en millisecondes (ms).
- Les durées renvoyées par ce module sont en secondes (int), arrondies à l'entier inférieur.
"""

from __future__ import annotations

from typing import Callable


def start_session_timer(get_ticks_func: Callable[[], int]) -> int:
    """
    Démarre un timer de session.

    Paramètre
    - get_ticks_func : fonction qui renvoie le temps courant en millisecondes (ms)

    Retour
    - start_ticks : valeur de référence (ms) à stocker et réutiliser ensuite
      (dans la scène, on la garde par exemple dans une variable start_ticks)
    """
    # Conversion en int pour être sûr d'avoir un type stable (certaines fonctions peuvent renvoyer un float)
    return int(get_ticks_func())


def get_elapsed_seconds(start_ticks: int, get_ticks_func: Callable[[], int]) -> int:
    """
    Calcule le temps écoulé depuis start_ticks.

    Principe
    - On récupère les ticks actuels, on fait la différence, puis on convertit en secondes.

    Sécurité
    - Si la différence est négative (cas très rare mais possible si mauvaise valeur start_ticks),
      on force à 0 pour éviter des durées incohérentes.

    Paramètres
    - start_ticks : ticks de départ (ms)
    - get_ticks_func : fonction qui renvoie le temps courant (ms)

    Retour
    - Durée en secondes (int), partie entière (ex: 3.9s -> 3)
    """
    now_ticks = int(get_ticks_func())
    elapsed_ms = now_ticks - int(start_ticks)

    # Sécurité : on refuse une durée négative
    if elapsed_ms < 0:
        elapsed_ms = 0

    # Conversion ms -> secondes (division entière)
    return int(elapsed_ms // 1000)


def stop_session_timer(start_ticks: int, get_ticks_func: Callable[[], int]) -> int:
    """
    Stoppe une session et renvoie la durée finale.

    Ici on ne "stoppe" pas réellement un timer (pas d'état global) :
    - on recalcule juste la durée au moment où on appelle la fonction.

    Paramètres
    - start_ticks : ticks de départ (ms)
    - get_ticks_func : fonction qui renvoie le temps courant (ms)

    Retour
    - Durée totale de la session en secondes (int)
    """
    return get_elapsed_seconds(start_ticks, get_ticks_func)
