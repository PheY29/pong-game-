import sys
import pygame

from game import Game, GamePlus
from game_state import GameStateManager
from menu import Start, Pause, WinningScreen

pygame.init()

# FPS
clock = pygame.time.Clock()
FPS = 60

# GESTION FENÊTRE
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
pygame.display.set_caption("Pong")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# GESTION DES MENUS
game_state_manager = GameStateManager("start")  # 1er page afficher
game = Game(screen, game_state_manager)
game_plus = GamePlus(screen, game_state_manager)
start = Start(screen, game, game_plus, game_state_manager)
pause = Pause(screen, game, game_plus, start, game_state_manager)
winning_screen = WinningScreen(screen, game, game_plus, start, game_state_manager)

states = {
    "start": start,
    "game": game,
    "game_plus": game_plus,
    "pause": pause,
    "winning_screen": winning_screen
}

# BOUCLE DU JEU
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state_manager.get_state() == "start":
            if event.type == pygame.KEYDOWN:
                start.keys[event.key] = True
            if event.type == pygame.KEYUP:
                start.keys[event.key] = False

        if not game_state_manager.get_state() == "start":
            if not (game.pause or game_plus.pause):
                if event.type == pygame.KEYDOWN:
                    game.keys[event.key] = True
                    game_plus.keys[event.key] = True
                    winning_screen.keys[event.key] = True

                    if game_state_manager.get_state() == "game":
                        if event.key == pygame.K_ESCAPE:
                            game.pause = True
                            game_state_manager.set_state("pause")

                    elif game_state_manager.get_state() == "game_plus":
                        if event.key == pygame.K_ESCAPE:
                            game_plus.pause = True
                            game_state_manager.set_state("pause")

                if event.type == pygame.KEYUP:
                    game.keys[event.key] = False
                    game_plus.keys[event.key] = False
                    winning_screen.keys[event.key] = False

            elif pause and not game_state_manager.get_state() == "winning_screen":
                if event.type == pygame.KEYDOWN:
                    pause.keys[event.key] = True

                    if event.key == pygame.K_ESCAPE:
                        if game_state_manager.get_previous_state() == "game":
                            game.pause = not game.pause
                            game_state_manager.set_state(game_state_manager.get_previous_state())
                        else:
                            game_plus.pause = not game_plus.pause
                            game_state_manager.set_state(game_state_manager.get_previous_state())

                if event.type == pygame.KEYUP:
                    pause.keys[event.key] = False

    states[game_state_manager.get_state()].run()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
