"""Gestion du temps de jeu - A IMPLEMENTER"""

import pygame

#--------------------------------------TimeTracker--------------------------------------#

class TimeTracker:
    """Tracker de temps pour une partie"""

    def __init__(self):
        self.start_ticks = 0
        self.running = False
        self.paused = False

    def start(self):
        """Demarre le timer"""
        pass  # TODO: Implementer

    def stop(self) -> float:
        """Arrete et retourne le temps ecoule en secondes"""
        pass  # TODO: Implementer
        return 0.0

    def pause(self):
        """Met le timer en pause"""
        pass  # TODO: Implementer

    def resume(self):
        """Reprend le timer apres une pause"""
        pass  # TODO: Implementer

    def get_elapsed(self) -> float:
        """Retourne le temps ecoule en secondes"""
        pass  # TODO: Implementer
        return 0.0

    def get_formatted(self) -> str:
        """Retourne le temps formate mm:ss"""
        pass  # TODO: Implementer
        return "00:00"
