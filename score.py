"""
score.py

Ce module gère la lecture et l'écriture des scores en TXT.
Format: nom|temps|gagné (True/False)
Le tri se fait par temps (croissant) pour les gagnants, et les perdants sont à la fin.
"""
import os
from constants import SCORE_FILE

def save_score(player_name, time_taken, won):
    """
    Enregistre le score d'un joueur dans le fichier TXT.
    time_taken: float (secondes)
    won: bool (True si gagné, False sinon)
    Format: nom|temps|gagné
    """
    try:
        # Ajouter le nouveau score à la fin du fichier
        with open(SCORE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{player_name}|{time_taken:.2f}|{won}\n")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du score : {e}")

def get_top_scores():
    """
    Récupère les scores triés depuis le fichier TXT.
    """
    scores_data = []
    if not os.path.exists(SCORE_FILE):
        return []

    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:  # Ignorer les lignes vides
                continue
                
            parts = line.split("|")
            if len(parts) == 3:
                name = parts[0]
                try:
                    time = float(parts[1])
                except ValueError:
                    time = 999999  # Valeur par défaut si conversion échoue
                
                won = parts[2].strip() == "True"
                
                scores_data.append({
                    "name": name,
                    "time": time,
                    "won": won
                })
    except Exception as e:
        print(f"Erreur lors de la lecture des scores : {e}")
        return []

    # Trier: Les gagnants (won=True) par temps croissant, puis les perdants
    def sort_key(item):
        if item.get("won", False):
            return (0, item.get("time", 0))  # Priority 0, then time
        else:
            return (1, 0)  # Priority 1 (bottom)

    scores_data.sort(key=sort_key)
    
    # Convertir pour affichage
    display_list = []
    for entry in scores_data:
        name = entry.get("name", "Unknown")
        time = entry.get("time", 0)
        won = entry.get("won", False)
        display = f"{time:.2f}s" if won else "Mot non trouvé"
        display_list.append((name, display))
        
    return display_list
