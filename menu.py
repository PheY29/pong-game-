import pygame
import time
import sys

from animation import AnimateSprite


class Start(AnimateSprite):
    def __init__(self, screen, game, game_plus, game_state_manager):
        super().__init__("menus/validation")
        self.screen = screen
        self.game = game
        self.game_plus = game_plus
        self.screen_img = pygame.image.load("assets/menus/start.png")
        self.image = self.get_image(0, 0, 26, 26)
        self.image.set_colorkey([255, 255, 255])
        self.game_state_manager = game_state_manager
        self.normal_mode_rect = pygame.rect.Rect(485, 425, 500, 50)
        self.special_mode_rect = pygame.rect.Rect(570, 500, 500, 50)

        self.font = pygame.font.Font("assets/font_start.ttf", 40)
        self.font_1 = pygame.font.Font("assets/font_start.ttf", 30)
        self.WHITE = (255, 255, 255)
        self.BLUE = (41, 182, 246)
        self.versus_selected = "yes"
        self.versus_choice_made = False

        self.keys = {}

        self.mode_selected = "normal"
        self.mode_chosen = False
        self.enter_pressed = False
        self.prev_down_key_state = False

        self.normal_mode_animation_triggered = True
        self.special_mode_animation_triggered = False
        self.animation_end_time = 0
        self.delay_to_run_game = 1

    def run(self):
        self.screen.blit(self.screen_img, (0, 0))
        self.draw_start_menu()
        self.handle_input()

        if self.normal_mode_animation_triggered:
            self.screen.blit(self.image, (945, 437))
            self.animate("validate", stop=True)
        if self.special_mode_animation_triggered:
            self.screen.blit(self.image, (1026, 513))
            self.animate("validate", stop=True)

        if self.mode_chosen and self.enter_pressed:
            self.load_game()

    def load_game(self):
        if self.enter_pressed:
            if self.mode_selected == "normal" and time.time() >= self.animation_end_time:
                self.game_state_manager.set_state("game")
            elif self.mode_selected == "special" and time.time() >= self.animation_end_time:
                self.game_state_manager.set_state("game_plus")

    def handle_input(self):
        up_down_keys = self.keys.get(pygame.K_DOWN, False) or self.keys.get(pygame.K_UP, False)
        left_right_keys = self.keys.get(pygame.K_LEFT) or self.keys.get(pygame.K_RIGHT)
        current_down_key_state = (up_down_keys or left_right_keys or self.keys.get(pygame.K_ESCAPE)
                                  or self.keys.get(pygame.K_RETURN))

        if self.keys.get(pygame.K_ESCAPE) and not self.prev_down_key_state:
            if self.mode_chosen:
                self.mode_chosen = False
            else:
                pygame.quit()
                sys.exit()

        if up_down_keys and not self.prev_down_key_state and not self.mode_chosen:
            self.animation_index = 0
            if self.mode_selected == "normal":
                self.mode_selected = "special"
                self.normal_mode_animation_triggered = False
                self.special_mode_animation_triggered = True
            else:
                self.mode_selected = "normal"
                self.normal_mode_animation_triggered = True
                self.special_mode_animation_triggered = False

        if self.keys.get(pygame.K_RETURN) and not self.prev_down_key_state:
            if not self.mode_chosen:
                self.mode_chosen = True
            else:
                self.enter_pressed = True

        if self.mode_chosen:
            if left_right_keys and not self.prev_down_key_state:
                if self.mode_selected == "normal":
                    self.game.player_right_is_AI = not self.game.player_right_is_AI
                else:
                    self.game_plus.player_right_is_AI = not self.game_plus.player_right_is_AI

        self.prev_down_key_state = current_down_key_state

    def draw_start_menu(self):
        if self.mode_selected == "normal":
            self.screen.blit(self.font_1.render("Yes", True,
                                                self.BLUE if self.game.player_right_is_AI else self.WHITE), (908, 570))
            self.screen.blit(self.font_1.render("No", True,
                                                self.BLUE if not self.game.player_right_is_AI else self.WHITE), (1000, 570))
        else:
            self.screen.blit(self.font_1.render("Yes", True,
                                                self.BLUE if self.game_plus.player_right_is_AI else self.WHITE), (908, 570))
            self.screen.blit(self.font_1.render("No", True,
                                                self.BLUE if not self.game_plus.player_right_is_AI else self.WHITE), (1000, 570))

    def return_to_start(self):
        self.reset_keys()
        self.mode_selected = "normal"
        self.mode_chosen = False
        self.versus_selected = "yes"
        self.animation_index = 0

        self.game.player_right_is_AI = True
        self.game_plus.player_right_is_AI = True
        self.prev_down_key_state = False
        self.enter_pressed = False

        self.normal_mode_animation_triggered = True
        self.special_mode_animation_triggered = False
        self.animation_end_time = 0
        self.delay_to_run_game = 1

    def reset_keys(self):
        self.keys = {}


class Pause:
    def __init__(self, screen, game, game_plus, start, game_state_manager):
        self.screen = screen
        self.game = game
        self.game_plus = game_plus
        self.start = start
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.game_state_manager = game_state_manager
        self.font = pygame.font.Font("assets/font.ttf", 20)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.restart_color = (200, 190, 0)
        self.exit_color = (255, 255, 255)
        self.reset_color = (255, 255, 255)
        self.button_selected = "restart"

        self.keys = {}
        self.prev_down_key_state = False
        self.enter_pressed = False

        self.reset_game_mode_rect = None
        self.exit_game_rect = None
        self.restart_game_rect = None

    def run(self):
        self.draw_pause()
        self.handle_input()

    def handle_input(self):
        left_key_pressed = self.keys.get(pygame.K_LEFT, False) or self.keys.get(pygame.K_q, False)
        right_key_pressed = self.keys.get(pygame.K_RIGHT, False) or self.keys.get(pygame.K_d, False)
        current_down_key_state = left_key_pressed or right_key_pressed

        if current_down_key_state and not self.prev_down_key_state:
            if self.game_state_manager.get_previous_state() == "game":
                if self.button_selected == "restart":
                    self.button_selected = "exit"
                    self.exit_color = (200, 190, 0)
                    self.restart_color = (255, 255, 255)
                else:
                    self.button_selected = "restart"
                    self.restart_color = (200, 190, 0)
                    self.exit_color = (255, 255, 255)
            else:
                if right_key_pressed:
                    if self.button_selected == "restart":
                        self.button_selected = "reset_mode"
                        self.restart_color = (255, 255, 255)
                        self.reset_color = (200, 190, 0)
                        self.exit_color = (255, 255, 255)
                    elif self.button_selected == "reset_mode":
                        self.button_selected = "exit"
                        self.restart_color = (255, 255, 255)
                        self.reset_color = (255, 255, 255)
                        self.exit_color = (200, 190, 0)
                    else:
                        self.button_selected = "restart"
                        self.restart_color = (200, 190, 0)
                        self.reset_color = (255, 255, 255)
                        self.exit_color = (255, 255, 255)
                else:
                    if left_key_pressed:
                        if self.button_selected == "restart":
                            self.button_selected = "exit"
                            self.restart_color = (255, 255, 255)
                            self.reset_color = (255, 255, 255)
                            self.exit_color = (200, 190, 0)
                        elif self.button_selected == "exit":
                            self.button_selected = "reset_mode"
                            self.restart_color = (255, 255, 255)
                            self.reset_color = (200, 190, 0)
                            self.exit_color = (255, 255, 255)
                        else:
                            self.button_selected = "restart"
                            self.restart_color = (200, 190, 0)
                            self.reset_color = (255, 255, 255)
                            self.exit_color = (255, 255, 255)

        self.prev_down_key_state = current_down_key_state

        if self.keys.get(pygame.K_RETURN):
            self.enter_pressed = True

        if self.enter_pressed:
            if self.button_selected == "restart":
                if self.game_state_manager.get_previous_state() == "game":
                    self.game.all_reset()
                    self.game_state_manager.set_state("game")
                else:
                    self.game_plus.all_reset()
                    self.game_state_manager.set_state("game_plus")

            if self.button_selected == "exit":
                self.start.return_to_start()

                if self.game_state_manager.get_previous_state() == "game":
                    self.game.pause = False
                    self.game.all_reset()
                else:
                    self.game_plus.pause = False
                    self.game_plus.reset_game_mode()
                    self.game_plus.all_reset()

                self.game_state_manager.set_state("start")

            if self.game_state_manager.get_previous_state() == "game_plus":
                if self.button_selected == "reset_mode":
                    self.game_plus.reset_game_mode()
                    self.game_plus.all_reset()
                    self.game_state_manager.set_state("game_plus")

        self.enter_pressed = False
        self.keys = {}

    def draw_pause(self):
        if self.game_state_manager.get_state() == "pause":
            pygame.draw.rect(self.surface, (128, 128, 128, 2), [0, 0, self.width, self.height])

            paused_menu = pygame.draw.rect(self.surface, "dark gray", [(self.width // 2 - 260), 65, 520, 50],
                                           0, 10)
            self.surface.blit(self.font.render("Paused : Escape to Resume", True, "black"),
                              ((self.width // 2 - paused_menu.width // 3), 80))

            if self.game_state_manager.get_previous_state() == "game":
                self.restart_game_rect = pygame.Rect((self.width // 2 - 260), 135, 200, 50)
                self.exit_game_rect = pygame.Rect((self.width // 2 + 60), 135, 200, 50)

                pygame.draw.rect(self.surface, self.restart_color, [(self.width // 2 - 260), 135, 200, 50], 0,
                                 10)
                pygame.draw.rect(self.surface, self.exit_color, [(self.width // 2 + 60), 135, 200, 50], 0,
                                 10)

                self.surface.blit(self.font.render("Restart", True, "black"),
                                  ((self.width // 2 - 210), 150))
                self.surface.blit(self.font.render("Exit", True, "black"),
                                  ((self.width // 2 + 135), 150))

            if self.game_state_manager.get_previous_state() == "game_plus":
                self.restart_game_rect = pygame.Rect((self.width // 2 - 260), 135, 120, 50)
                self.exit_game_rect = pygame.Rect((self.width // 2 + 150), 135, 110, 50)
                self.reset_game_mode_rect = pygame.Rect((self.width // 2 - 120), 135, 250, 50)

                pygame.draw.rect(self.surface, self.restart_color, [(self.width // 2 - 260), 135, 120, 50], 0,
                                 10)
                pygame.draw.rect(self.surface, self.exit_color, [(self.width // 2 + 150), 135, 110, 50], 0,
                                 10)
                pygame.draw.rect(self.surface, self.reset_color, [(self.width // 2 - 120), 135, 250, 50], 0,
                                 10)
                self.surface.blit(self.font.render("Restart", True, "black"),
                                  ((self.width // 2 - 250), 150))
                self.surface.blit(self.font.render("Exit", True, "black"),
                                  ((self.width // 2 + 180), 150))
                self.surface.blit(self.font.render("Change game mode", True, "black"),
                                  ((self.width // 2 - 115), 150))

            self.screen.blit(self.surface, (0, 0))


class WinningScreen:
    def __init__(self, screen, game, game_plus, start, game_state_manager):
        self.screen = screen
        self.game = game
        self.game_plus = game_plus
        self.start = start
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.game_state_manager = game_state_manager
        self.font = pygame.font.Font("assets/font.ttf", 20)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.new_game_color = (200, 190, 0)
        self.exit_color = (255, 255, 255)
        self.button_selected = "new_game"

        self.keys = {}
        self.prev_down_key_state = False
        self.enter_pressed = False

        self.new_game_rect = pygame.Rect((self.width // 2 - 200), (self.height // 2 + 50), 150, 30)
        self.exit_game_rect = pygame.Rect((self.width // 2 + 50), (self.height // 2 + 50), 150, 30)

    def run(self):
        self.draw_winning_menu()
        self.handle_input()

    def handle_input(self):
        current_down_key_state = (self.keys.get(pygame.K_LEFT, False) or self.keys.get(pygame.K_q, False)
                                  or self.keys.get(pygame.K_RIGHT, False) or self.keys.get(pygame.K_d, False))

        if current_down_key_state and not self.prev_down_key_state:
            if self.button_selected == "new_game":
                self.button_selected = "exit"
                self.new_game_color = (255, 255, 255)
                self.exit_color = (200, 190, 0)
            else:
                self.button_selected = "new_game"
                self.new_game_color = (200, 190, 0)
                self.exit_color = (255, 255, 255)
        self.prev_down_key_state = current_down_key_state

        if self.keys.get(pygame.K_RETURN):
            self.enter_pressed = True

        if self.enter_pressed:
            if self.button_selected == "new_game":
                if self.game_state_manager.get_previous_state() == "game":
                    self.game.all_reset()
                    self.game_state_manager.set_state("game")
                else:
                    self.game_plus.all_reset()
                    if self.game_plus.mode_selected == "mode_double_ball":
                        if self.game_plus.ball_one.x_velocity == self.game_plus.ball_two.x_velocity:
                            self.game_plus.ball_two.x_velocity *= -1
                    self.game_state_manager.set_state("game_plus")

            if self.button_selected == "exit":
                self.start.return_to_start()

                if self.game_state_manager.get_previous_state() == "game":
                    self.game.pause = False
                    self.game.all_reset()
                else:
                    self.game_plus.pause = False
                    self.game_plus.all_reset()

                self.game_state_manager.set_state("start")

        self.enter_pressed = False
        self.keys = {}

    def draw_winning_menu(self):
        if self.game_state_manager.get_state() == "winning_screen":
            pygame.draw.rect(self.surface, (128, 128, 128, 0), [0, 0, self.width, self.height])

            if self.game_state_manager.get_previous_state() == "game":
                winning_player = self.font.render(self.game.win_text, 1, "green")
            else:
                winning_player = self.font.render(self.game_plus.win_text, 1, "green")

            self.surface.blit(winning_player, (self.width // 2 - winning_player.get_width() // 2,
                                               (self.height // 2 - winning_player.get_height() // 2) + 30))
            pygame.draw.rect(self.surface, self.new_game_color, [(self.width // 2 - 200),
                                                                 (self.height // 2 + 50), 150, 30], 0, 10)
            pygame.draw.rect(self.surface, self.exit_color, [(self.width // 2 + 50),
                                                             (self.height // 2 + 50), 150, 30], 0, 10)

            self.surface.blit(self.font.render("New Game", True, "black"),
                              ((self.width // 2 - 185), (self.height // 2 + 52.5)))
            self.surface.blit(self.font.render("Exit", True, "black"),
                              ((self.width // 2 + 100), (self.height // 2 + 52.5)))

            self.screen.blit(self.surface, (0, 0))
