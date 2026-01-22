"""
BUT DU FICHIER
- Gérer les scènes du jeu (menu, game, add_word, leaderboard, game_over).
- Une seule scène est active à la fois.
- Quand on change de scène, on crée la nouvelle et on lui donne un "payload".

POURQUOI ON FAIT ÇA ?
- Pour éviter d'avoir tout le code dans un seul fichier énorme.
- Chaque scène gère son affichage et ses events.
- Le manager sert juste à "router" : events -> scène, update -> scène, draw -> scène.

CONTRAT D'UNE SCÈNE
Chaque scène doit avoir (au minimum) ces méthodes :
- on_enter() : (optionnel) appelée au moment où on arrive sur la scène
- handle_event(event) : appelée pour chaque event pygame
- update(dt) : appelée chaque frame (dt = secondes)
- draw(screen) : dessin de la scène

IMPORTANT
- Ce fichier ne fait pas la logique du jeu (pendu), il gère juste la navigation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

# Import des scènes 
from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene
from scenes.add_word_scene import AddWordScene
from scenes.leaderboard_scene import LeaderboardScene
from scenes.game_over_scene import GameOverScene


class SceneManager:
    """
    SceneManager = "chef d'orchestre" des scènes.

    Attributs :
    - shared : ressources partagées (fonts, images, sons...)
    - runtime_state : état global (pseudo actif, cache leaderboard, toasts, etc.)
    - scenes : dictionnaire nom -> classe de scène
    - current_scene : instance de la scène active
    """

    def __init__(self, shared: Dict[str, Any], runtime_state: Dict[str, Any]) -> None:
        """
        Initialise le manager et démarre sur le menu.

        Étapes :
        1) enregistrer shared et runtime_state
        2) créer le dictionnaire de scènes disponibles
        3) current_scene = None
        4) aller sur la scène "menu"
        """
        self.shared = shared
        self.runtime_state = runtime_state

        # Dictionnaire "nom de scène" -> classe
        # (facile à utiliser avec go_to("menu"), go_to("game"), etc.)
        self.scenes: Dict[str, Type[Any]] = {
            "menu": MenuScene,
            "game": GameScene,
            "add_word": AddWordScene,
            "leaderboard": LeaderboardScene,
            "game_over": GameOverScene,
        }

        self.current_scene: Optional[Any] = None

        # On démarre directement sur le menu
        self.go_to("menu")


    def go_to(self, scene_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Change la scène active.

        Paramètres :
        - scene_name : nom de la scène ("menu", "game", ...)
        - payload : dict de données à transmettre à la scène 

        Étapes :
        1) vérifier que scene_name existe dans self.scenes
        2) créer une instance de la scène correspondante
        3) stocker dans self.current_scene
        4) si la scène a une méthode on_enter(), l'appeler
        """
        if payload is None:
            payload = {}

        if scene_name not in self.scenes:
            raise ValueError(f"Scène inconnue : {scene_name}")

        SceneClass = self.scenes[scene_name]

        # On crée la scène : on lui donne manager + shared + runtime_state + payload
        self.current_scene = SceneClass(
            manager=self,
            shared=self.shared,
            runtime_state=self.runtime_state,
            payload=payload,
        )

        # Certaines scènes ont besoin d'initialiser leurs widgets à l'entrée
        if hasattr(self.current_scene, "on_enter"):
            self.current_scene.on_enter()


    def dispatch_event(self, event: Any) -> None:
        """
        Envoie un event à la scène active.

        Exemple :
        - clic souris
        - touche clavier
        """
        if self.current_scene is None:
            return
        self.current_scene.handle_event(event)


    def update_scene(self, dt: float) -> None:
        """
        Met à jour la scène active.

        dt = temps en secondes depuis la frame précédente.
        """
        if self.current_scene is None:
            return
        self.current_scene.update(dt)


    def draw_scene(self, screen: Any) -> None:
        """
        Dessine la scène active.
        """
        if self.current_scene is None:
            return
        self.current_scene.draw(screen)
