"""Gestionnaire de scenes du jeu"""

import pygame

class SceneManager:
    """Gere les transitions entre les scenes du jeu"""

    def __init__(self, screen):
        self.screen = screen
        self.scenes = {}
        self.current_scene = None
        self.shared_data = {
            "player_names": ["", "", ""],
            "num_players": 1,
            "current_player_index": 0,
            "difficulty": "normal",
            "scores": [0, 0, 0],
            "last_player_pseudo": "",
            "last_word": "",
            "last_time": 0,
            "last_won": False,
        }
        self._register_scenes()

    def _register_scenes(self):
        """Enregistre toutes les scenes disponibles"""
        from scenes.menu_scene import MenuScene
        from scenes.game_scene import GameScene
        from scenes.game_over_scene import GameOverScene
        from scenes.leaderboard_scene import LeaderboardScene
        from scenes.add_word_scene import AddWordScene

        self.scenes["menu"] = MenuScene(self)
        self.scenes["game"] = GameScene(self)
        self.scenes["game_over"] = GameOverScene(self)
        self.scenes["leaderboard"] = LeaderboardScene(self)
        self.scenes["add_word"] = AddWordScene(self)

    def go_to(self, scene_name: str):
        """Change de scene"""
        if scene_name in self.scenes:
            if self.current_scene:
                self.current_scene.exit()
            self.current_scene = self.scenes[scene_name]
            self.current_scene.enter()

    def handle_events(self, events):
        """Transmet les evenements a la scene courante"""
        if self.current_scene:
            self.current_scene.handle_events(events)

    def update(self):
        """Met a jour la scene courante"""
        if self.current_scene:
            self.current_scene.update()

    def draw(self):
        """Dessine la scene courante"""
        if self.current_scene:
            self.current_scene.draw(self.screen)


class Scene:
    """Classe de base pour toutes les scenes"""

    def __init__(self, manager: SceneManager):
        self.manager = manager

    def enter(self):
        """Appele quand on entre dans la scene"""
        pass

    def exit(self):
        """Appele quand on quitte la scene"""
        pass

    def handle_events(self, events):
        """Gere les evenements pygame"""
        pass

    def update(self):
        """Met a jour la logique de la scene"""
        pass

    def draw(self, screen):
        """Dessine la scene"""
        pass
