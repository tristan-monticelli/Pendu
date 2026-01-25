"""
Rôle du fichier
- Démarrer Pygame (fenêtre, horloge, audio).
- Charger les ressources globales (polices, images, sons).
- Construire l’état partagé entre toutes les scènes (runtime_state + shared).
- Créer le SceneManager et lancer la boucle principale.

Ce fichier n’a pas pour objectif de contenir la logique du pendu.
La logique du jeu et l’UI détaillée doivent rester dans les scènes / modules dédiés.
"""

from __future__ import annotations

import pygame
import sys

from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    FONT_PATH,
    FONT_SIZES,
    LEADERBOARD_PATH,
    SHOW_FPS,
    MUSIC_PATH,
    MUSIC_VOLUME,
    SOUND_PATHS,
    SOUND_VOLUME,
)

from scene_manager import SceneManager
from core.leaderboard_io import load_leaderboard, get_last_player_summary
from ui.simpson_components import ToastManager


def init_pygame() -> tuple[pygame.Surface, pygame.time.Clock, dict]:
    """
    Initialise Pygame et prépare ce qui est nécessaire dès le démarrage.

    Ce qui est fait ici
    - pygame.init() : initialisation globale Pygame.
    - pygame.mixer.init() : audio (sons + musique).
    - création de la fenêtre (mode fenêtré sur la résolution définie dans settings).
    - création de l’horloge (pour le FPS et le dt).
    - chargement des polices (police Simpson avec fallback).
    - lancement de la musique de fond (si possible).

    Retour
    - screen : surface principale d’affichage.
    - clock : horloge Pygame.
    - fonts : dictionnaire de polices prêtes à être utilisées (tiny/body/title, etc.).
    """
    pygame.init()
    pygame.mixer.init()  # Audio global

    # Fenêtre fixe (le plein écran est géré ailleurs si besoin)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pendu - Simpson Edition")

    clock = pygame.time.Clock()

    fonts = load_fonts()
    init_background_music()

    return screen, clock, fonts


def init_background_music() -> None:
    """
    Initialise la musique de fond et la lance en boucle.

    Remarques
    - Ce bloc est "tolérant" : si la musique ne charge pas, le jeu continue.
    - Le quit/init du mixer sert à repartir d’un état propre avec des paramètres stables

    Effets de bord
    - Démarre pygame.mixer.music en boucle (si ok).
    """
    try:
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)  # boucle infinie

        # Infos juste pour le dev pour vérifier que l’audio est bien actif
        print(f"Musique chargée: {MUSIC_PATH}")
        print(f"Volume: {MUSIC_VOLUME * 100}%")
        print(f"Mixer init: {pygame.mixer.get_init()}")

    except Exception as e:
        print(f"Impossible de charger la musique: {e}")
        print("Le jeu continue sans musique...")


def load_fonts() -> dict:
    """
    Charge les polices utilisées dans le projet.

    Stratégie
    - On charge la police Simpson (FONT_PATH) pour chaque taille définie dans FONT_SIZES.
    - Si la police n’est pas trouvée / ne se charge pas :
      on bascule sur la police par défaut de Pygame (None) pour garder un jeu fonctionnel.

    Retour
    - fonts : dict {nom_taille: pygame.font.Font}
      Exemple : fonts["body"], fonts["title"], ...
    """
    fonts = {}

    try:
        for size_name, size_value in FONT_SIZES.items():
            fonts[size_name] = pygame.font.Font(FONT_PATH, size_value)
    except Exception as e:
        print(f"Erreur chargement police Simpson: {e}")
        print("Utilisation de la police par défaut...")

        for size_name, size_value in FONT_SIZES.items():
            fonts[size_name] = pygame.font.Font(None, size_value)

    return fonts


def load_assets() -> dict:
    """
    Charge les assets graphiques et applique le scaling de référence.

    Principe
    - Les chemins (ASSETS_PATHS) et les tailles cibles (ASSET_SIZES) viennent de settings.
    - Chaque image est chargée (convert_alpha pour garder la transparence),
      puis redimensionnée pour être cohérente à l’écran.

    Tolérance aux erreurs
    - Pour certains packs (ex: têtes Trump, coeurs), on crée des "placeholders"
      si le chargement échoue, pour éviter un crash complet.
    """
    from settings import ASSETS_PATHS, ASSET_SIZES

    assets = {}

    # --- Trump : têtes (expressions) ---
    try:
        assets["trump_happy"] = pygame.image.load(ASSETS_PATHS["trump_happy"]).convert_alpha()
        assets["trump_angry"] = pygame.image.load(ASSETS_PATHS["trump_angry"]).convert_alpha()
        assets["trump_sad"] = pygame.image.load(ASSETS_PATHS["trump_sad"]).convert_alpha()
        assets["trump_dead"] = pygame.image.load(ASSETS_PATHS["trump_dead"]).convert_alpha()

        for mood in ["happy", "angry", "sad", "dead"]:
            assets[f"trump_{mood}"] = pygame.transform.scale(
                assets[f"trump_{mood}"],
                ASSET_SIZES["trump_head"]
            )
    except Exception as e:
        print(f"Erreur chargement Trump heads: {e}")
        for mood in ["happy", "angry", "sad", "dead"]:
            assets[f"trump_{mood}"] = pygame.Surface(ASSET_SIZES["trump_head"])
            assets[f"trump_{mood}"].fill((255, 217, 15))  # jaune "Simpson"

    # --- Trump : corps + membres ---
    try:
        assets["trump_body"] = pygame.image.load(ASSETS_PATHS["trump_body"]).convert_alpha()
        assets["trump_arm_left"] = pygame.image.load(ASSETS_PATHS["trump_arm_left"]).convert_alpha()
        assets["trump_arm_right"] = pygame.image.load(ASSETS_PATHS["trump_arm_right"]).convert_alpha()
        assets["trump_leg_left"] = pygame.image.load(ASSETS_PATHS["trump_leg_left"]).convert_alpha()
        assets["trump_leg_right"] = pygame.image.load(ASSETS_PATHS["trump_leg_right"]).convert_alpha()

        assets["trump_body"] = pygame.transform.scale(assets["trump_body"], ASSET_SIZES["trump_body"])
        assets["trump_arm_left"] = pygame.transform.scale(assets["trump_arm_left"], ASSET_SIZES["trump_arm"])
        assets["trump_arm_right"] = pygame.transform.scale(assets["trump_arm_right"], ASSET_SIZES["trump_arm"])
        assets["trump_leg_left"] = pygame.transform.scale(assets["trump_leg_left"], ASSET_SIZES["trump_leg"])
        assets["trump_leg_right"] = pygame.transform.scale(assets["trump_leg_right"], ASSET_SIZES["trump_leg"])
    except Exception as e:
        print(f"Erreur chargement Trump body: {e}")

    # --- Pendu : potence ---
    try:
        assets["pendu_wood"] = pygame.image.load(ASSETS_PATHS["pendu_wood"]).convert_alpha()
        assets["pendu_metal"] = pygame.image.load(ASSETS_PATHS["pendu_metal"]).convert_alpha()

        assets["pendu_wood"] = pygame.transform.scale(assets["pendu_wood"], ASSET_SIZES["pendu"])
        assets["pendu_metal"] = pygame.transform.scale(assets["pendu_metal"], ASSET_SIZES["pendu"])
    except Exception as e:
        print(f"Erreur chargement pendu: {e}")

    # --- Vies : coeurs ---
    try:
        assets["heart_full"] = pygame.image.load(ASSETS_PATHS["heart_full"]).convert_alpha()
        assets["heart_empty"] = pygame.image.load(ASSETS_PATHS["heart_empty"]).convert_alpha()

        assets["heart_full"] = pygame.transform.scale(assets["heart_full"], ASSET_SIZES["heart"])
        assets["heart_empty"] = pygame.transform.scale(assets["heart_empty"], ASSET_SIZES["heart"])
    except Exception as e:
        print(f"Erreur chargement coeurs: {e}")
        assets["heart_full"] = pygame.Surface(ASSET_SIZES["heart"])
        assets["heart_full"].fill((255, 0, 0))
        assets["heart_empty"] = pygame.Surface(ASSET_SIZES["heart"])
        assets["heart_empty"].fill((128, 128, 128))

    # --- Indices : icônes ---
    try:
        assets["hint_available"] = pygame.image.load(ASSETS_PATHS["hint_available"]).convert_alpha()
        assets["hint_used"] = pygame.image.load(ASSETS_PATHS["hint_used"]).convert_alpha()

        assets["hint_available"] = pygame.transform.scale(assets["hint_available"], ASSET_SIZES["hint"])
        assets["hint_used"] = pygame.transform.scale(assets["hint_used"], ASSET_SIZES["hint"])
    except Exception as e:
        print(f"Erreur chargement indices: {e}")

    return assets


def load_sounds() -> dict:
    """
    Charge les effets sonores (Sound) listés dans settings.

    Retour
    - sounds : dict {nom: pygame.mixer.Sound | None}
      Si un son ne charge pas, on stocke None pour éviter un crash.
    """
    sounds = {}

    for sound_name, sound_path in SOUND_PATHS.items():
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(SOUND_VOLUME)
            sounds[sound_name] = sound
            print(f"Son chargé: {sound_name}")
        except Exception as e:
            print(f"Impossible de charger {sound_name}: {e}")
            sounds[sound_name] = None

    return sounds


def create_runtime_state() -> dict:
    """
    Construit l'état global partagé entre toutes les scènes.

    Idée
    - runtime_state sert à garder des infos qui doivent survivre aux transitions :
      pseudo actif, difficulté choisie, cache du leaderboard, toasts, etc.
    - Les scènes peuvent lire/écrire dedans pour se synchroniser.

    Retour
    - dict prêt à être donné au SceneManager et utilisé dans la boucle.
    """
    leaderboard = load_leaderboard(LEADERBOARD_PATH)
    last_summary = get_last_player_summary(leaderboard)

    runtime_state = {
        "active_pseudo": None,

        # Données classement (on évite de relire le fichier en permanence)
        "leaderboard_cache": leaderboard,
        "last_player_summary": last_summary,

        # UI : messages temporaires affichés par-dessus les scènes
        "toast_manager": ToastManager(),

        "selected_difficulty": "MOYEN",

        # Flag de sortie (piloté par la boucle + potentiellement par les scènes)
        "should_quit": False,
    }

    return runtime_state


def run_app_loop(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    manager: SceneManager,
    runtime_state: dict,
    fonts: dict,
) -> None:
    """
    Boucle principale du jeu.

    Responsabilités
    - Calculer dt (temps entre frames).
    - Récupérer les événements Pygame et les transmettre à la scène active.
    - Appeler update/draw de la scène via le SceneManager.
    - Mettre à jour et dessiner les toasts (au-dessus de tout).
    - Option debug : afficher le FPS.

    Sortie
    - La boucle s'arrête quand runtime_state["should_quit"] passe à True.
    """
    while not runtime_state["should_quit"]:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            # Fermeture fenêtre
            if event.type == pygame.QUIT:
                runtime_state["should_quit"] = True

            # Raccourci : ESC quitte le jeu depuis le menu (ailleurs, les scènes peuvent gérer ESC)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if hasattr(manager.current_scene, "__class__"):
                    if manager.current_scene.__class__.__name__ == "MenuScene":
                        runtime_state["should_quit"] = True

            manager.dispatch_event(event)

        manager.update_scene(dt)

        toast_manager = runtime_state["toast_manager"]
        toast_manager.update(dt)

        manager.draw_scene(screen)
        toast_manager.draw(screen, fonts["body"])

        if SHOW_FPS:
            fps_text = f"FPS: {int(clock.get_fps())}"
            fps_font = fonts["tiny"]
            fps_surface = fps_font.render(fps_text, True, (255, 255, 255))
            screen.blit(fps_surface, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def main() -> None:
    """
    Point d’entrée principal : prépare tout puis lance le jeu.

    Étapes
    1) init Pygame + polices + musique
    2) charger les images et les sons
    3) créer runtime_state (état global)
    4) préparer shared (ressources partagées)
    5) créer le SceneManager et lancer la boucle principale
    """
    screen, clock, fonts = init_pygame()

    assets = load_assets()
    sounds = load_sounds()

    runtime_state = create_runtime_state()

    shared = {
        "fonts": fonts,
        "assets": assets,
        "sounds": sounds,
    }

    manager = SceneManager(shared, runtime_state)

    # Par sécurité : on force le démarrage sur le menu (même si __init__ du manager le fait déjà)
    manager.go_to("menu")

    run_app_loop(screen, clock, manager, runtime_state, fonts)


if __name__ == "__main__":
    main()
