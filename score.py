"""
score.py

Ce module gère la lecture et l'écriture des scores en JSON.
Le tri se fait par temps (croissant) pour les gagnants, et les perdants sont à la fin.
"""
import json
import os
from constants import SCORE_FILE

def save_score(player_name, time_taken, won):
    """
    Enregistre le score d'un joueur.
    time_taken: float (secondes)
    won: bool (True si gagné, False sinon)
    """
    scores = []
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content:
                    scores = json.loads(content)
        except Exception as e:
            print(f"Erreur lecture scores pour sauvegarde : {e}")

    # Ajouter le nouveau score
    # Si gagné, on stocke le temps. Si perdu, on stocke aussi le temps (qui sera le temps max) 
    # mais le tri s'occupera de les mettre à la fin.
    scores.append({
        "name": player_name,
        "time": round(time_taken, 2), 
        "won": won,
        "display_time": f"{time_taken:.2f}s" if won else "Mot non trouvé"
    })

    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du score : {e}")

def get_top_scores():
    """
    Récupère les scores triés.
    """
    scores_data = []
    if not os.path.exists(SCORE_FILE):
        return []

    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if content:
                scores_data = json.loads(content)
    except Exception as e:
        print(f"Erreur lors de la lecture des scores : {e}")
        return []

    # Trier: Les gagnants (won=True) par temps croissant, puis les perdants
    # On utilise une clé de tri complexe
    def sort_key(item):
        if item.get("won", False):
            return (0, item.get("time", 0)) # Priority 0, then time
        else:
            return (1, 0) # Priority 1 (bottom)

    scores_data.sort(key=sort_key)
    
    # Convertir pour affichage
    display_list = []
    for entry in scores_data:
        name = entry.get("name", "Unknown")
        display = entry.get("display_time", "N/A")
        display_list.append((name, display))
        
    return display_list
