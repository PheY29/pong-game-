import pygame
import time
import random

from ball import Ball
from player import Paddle
from animation import AnimateSprite


class Game:
    def __init__(self, screen, game_state_manager):
        super().__init__()
        self.screen = screen
        self.img_terrain = pygame.image.load("assets/terrain.png")
        self.game_state_manager = game_state_manager

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (41, 182, 246)
        self.font = pygame.font.Font("assets/font.ttf", 20)

        self.paddle_width, self.paddle_height = 10, 100
        self.player_right_is_AI = True
        self.left_paddle = Paddle(0, (self.height // 2 - self.paddle_height // 2), self.paddle_width,
                                  self.paddle_height, "assets/paddle/paddle.png")
        self.right_paddle = Paddle((self.width - self.paddle_width), (self.height // 2 - self.paddle_height // 2),
                                   self.paddle_width, self.paddle_height, "assets/paddle/paddle.png",
                                   self.player_right_is_AI)

        self.balls_group = pygame.sprite.Group()  # Groupe de sprites pour les balles
        self.ball_one = None
        self.number_rolled = False

        self.point = 1
        self.winning_score = 5  # TODO changer score
        self.won = None
        self.win_text = ""
        self.left_score = 0
        self.right_score = 0
        self.keys = {}
        self.pause = False
        self.seconds, self.minutes, self.hours = 0, 0, 0
        self.acceleration_triggered = False
        self.random_offset = None

    def run(self):
        if not self.pause:
            self.golden_ball_luck()
            self.update_score()
            self.update_screen()
            self.handle_input()
            self.timer(self.screen)

            for ball in self.balls_group:
                ball.move()

            self.accelerate()
            self.handle_collision()
            self.check_victory()

    def update_screen(self):
        self.screen.fill(self.BLACK)
        self.screen.blit(self.img_terrain, (0, 0))

        left_score_text = self.font.render(f"{self.left_score}", 1, self.WHITE)
        right_score_text = self.font.render(f"{self.right_score}", 1, self.WHITE)
        self.screen.blit(left_score_text, (self.width // 4 - left_score_text.get_width() // 2, 20))
        self.screen.blit(right_score_text, ((self.width * (3 / 4)) - right_score_text.get_width() // 2, 20))

        for paddle in [self.left_paddle, self.right_paddle]:
            paddle.draw(self.screen)

        for ball in self.balls_group:
            ball.draw(self.screen)

    def handle_collision(self):
        for ball in self.balls_group:
            left_offset = (self.left_paddle.rect.x - ball.rect.x, self.left_paddle.rect.y - ball.rect.y)
            right_offset = (self.right_paddle.rect.x - ball.rect.x, self.right_paddle.rect.y - ball.rect.y)

            if (ball.rect.y + ball.radius * 3) >= self.height or ball.rect.y <= 0:
                ball.y_velocity *= -1

            if ball.ball_mask.overlap(self.left_paddle.paddle_mask, left_offset):
                if ball.rect.x > self.left_paddle.rect.x:
                    ball.rect.left = self.left_paddle.rect.right
                else:
                    ball.rect.right = self.left_paddle.rect.left

                ball.x_velocity *= -1
                middle_y = self.left_paddle.rect.y + self.left_paddle.rect.height / 2
                difference_y = middle_y - ball.rect.y
                reduction_factor = (self.left_paddle.rect.height / 2) / ball.x_velocity
                y_vel = difference_y / reduction_factor
                ball.y_velocity = -1 * y_vel

            if ball.ball_mask.overlap(self.right_paddle.paddle_mask, right_offset):
                if ball.rect.x > self.right_paddle.rect.x:
                    ball.rect.left = self.right_paddle.rect.right
                else:
                    ball.rect.right = self.right_paddle.rect.left

                ball.x_velocity *= -1
                middle_y = self.right_paddle.rect.y + self.right_paddle.rect.height / 2
                difference_y = middle_y - ball.rect.y
                reduction_factor = (self.right_paddle.rect.height / 2) / ball.x_velocity
                y_vel = difference_y / reduction_factor
                ball.y_velocity = y_vel

    def handle_input(self):
        if self.keys.get(pygame.K_z) and (self.left_paddle.rect.top >= 0):
            self.left_paddle.move(up=True)
        if self.keys.get(pygame.K_s) and (self.left_paddle.rect.bottom <= self.height):
            self.left_paddle.move(up=False)

        if self.player_right_is_AI:
            self.ai()
        else:
            if self.keys.get(pygame.K_UP) and (self.right_paddle.rect.top >= 0):
                self.right_paddle.move(up=True)
            if self.keys.get(pygame.K_DOWN) and (self.right_paddle.rect.bottom <= self.height):
                self.right_paddle.move(up=False)

    def ai(self):
        for ball in self.balls_group:
            if ball.x_velocity > 0:
                if self.random_offset is None:
                    self.random_offset = random.randint(-35, 35)

                target = self.right_paddle.rect.centery + self.random_offset
                if (target > ball.rect.centery) and (self.right_paddle.rect.top >= 0):
                    self.right_paddle.move(up=True)
                if (target < ball.rect.centery) and (self.right_paddle.rect.bottom < self.height):
                    self.right_paddle.move(up=False)
            else:
                self.random_offset = None

    def update_score(self):
        for ball in self.balls_group:
            if (ball.rect.x + ball.radius * 3) < 0 or ball.rect.x > self.width:
                if ball.rect.x < 0:
                    self.right_score += self.point
                else:
                    self.left_score += self.point

                if self.left_score < self.winning_score and self.right_score < self.winning_score:
                    self.countdown(3)
                    ball.reset()

    def check_victory(self):
        if (self.left_score >= self.winning_score or
                any(ball.is_golden and ball.rect.x > self.width for ball in self.balls_group)):
            self.won = True
            self.win_text = "Left Player WON!"

        elif (self.right_score >= self.winning_score or
              any(ball.is_golden and (ball.rect.x + ball.radius * 3) < 0 for ball in self.balls_group)):
            self.won = True
            self.win_text = "Right Player WON!"

        if self.won:
            self.game_state_manager.set_state("winning_screen")

    def countdown(self, seconds):
        while seconds > 0:
            self.update_screen()
            text = self.font.render(str(seconds), 1, self.BLUE)
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2,
                                    (self.height // 2 - text.get_height() // 2) + 30))
            pygame.display.update()
            time.sleep(1)
            seconds -= 1

    def timer(self, screen):
        self.seconds += 1 / 60
        if self.seconds >= 60:
            self.seconds = 0
            self.minutes += 1
            # if self.minutes >= 60:
            #     self.minutes = 0
            #     self.hours += 1
        time_text = self.font.render(f"{self.minutes:02d}:{int(self.seconds):02d}", 1, self.WHITE)
        screen.blit(time_text, (self.width // 2 - 35, 5))

    def accelerate(self):
        if int(self.seconds) != int((self.seconds - 1 / 60)):
            self.acceleration_triggered = False

        if self.seconds >= 1:
            for ball in self.balls_group:
                if int(self.seconds % 10) == 0 and not self.acceleration_triggered:
                    if ball.x_velocity > 0:
                        ball.x_velocity += ball.speed_factor
                    else:
                        ball.x_velocity -= ball.speed_factor

                self.acceleration_triggered = True

    def all_reset(self):
        self.balls_group.empty()
        self.pause = False
        self.won = None
        self.random_offset = None
        self.win_text = ""
        self.left_score = 0
        self.right_score = 0
        self.number_rolled = False
        self.seconds, self.minutes, self.hours = 0, 0, 0
        self.left_paddle.reset()
        self.right_paddle.reset()
        for ball in self.balls_group:
            ball.reset()

    def golden_ball_luck(self):
        if not self.number_rolled:
            roll_1 = random.randint(1, 100)
            if 1 <= roll_1 <= 5:
                self.ball_one = Ball(self.width // 2 - 11, self.height // 2, self.balls_group,
                                     "ball/golden_ball", True)
            else:
                self.ball_one = Ball(self.width // 2 - 11, self.height // 2, self.balls_group, "ball/ball")
            self.number_rolled = True


class GamePlus(AnimateSprite, Game):
    def __init__(self, screen, game_state_manager):
        AnimateSprite.__init__(self, "mode_selection")
        Game.__init__(self, screen, game_state_manager)
        self.screen = screen
        self.game_state_manager = game_state_manager

        self.image = self.get_image(0, 0, 48, 48)
        self.image = pygame.transform.scale(self.image, (96, 96))
        self.image.set_colorkey([255, 255, 255])
        self.animation_start_time = 0
        self.animation_end_time = 2.5

        self.pause = False
        self.keys = {}

        self.player_right_is_AI = True
        self.mode_selected = ""
        self.mode_activated = False
        self.mode_checked = False
        self.ball_two = None

        self.obstacles = []

    def run(self):
        if not self.pause:
            if not self.mode_activated:
                self.randomize_mode()

            self.golden_ball_luck()
            self.update_score()
            self.update_screen()

            if self.animation_start_time < self.animation_end_time:
                self.animate_mode_selection()
            else:
                self.mode_management()

                self.handle_input()
                self.timer(self.screen)

                for ball in self.balls_group:
                    ball.move()

                self.accelerate()
                self.handle_collision()
                self.check_victory()

    def update_score(self):
        for ball in self.balls_group:
            if (ball.rect.x + ball.radius * 2) < 0 or ball.rect.x > self.width:
                if ball.rect.x < 0:
                    self.right_score += self.point
                else:
                    self.left_score += self.point

                if self.left_score < self.winning_score and self.right_score < self.winning_score:
                    self.countdown(3)

                    if self.mode_selected == "mode_double_ball":
                        for balls in self.balls_group:
                            balls.reset()
                            if self.ball_one.x_velocity == self.ball_two.x_velocity:
                                self.ball_two.x_velocity *= -1
                    else:
                        ball.reset()

    def handle_collision(self):
        super().handle_collision()

        if self.mode_selected == "mode_obstacle":  # TODO : important !! perfect gestion de collision
            for ball in self.balls_group:
                for obstacle in self.obstacles:
                    collision_tolerance = 10
                    if ball.rect.colliderect(obstacle):
                        if abs(obstacle.top - ball.rect.bottom) < collision_tolerance and ball.y_velocity > 0:
                            ball.y_velocity *= -1
                        if abs(obstacle.bottom - ball.rect.top) < collision_tolerance and ball.y_velocity < 0:
                            ball.y_velocity *= -1
                        if abs(obstacle.right - ball.rect.left) < collision_tolerance and ball.x_velocity < 0:
                            ball.x_velocity *= -1
                        if abs(obstacle.left - ball.rect.right) < collision_tolerance and ball.x_velocity > 0:
                            ball.x_velocity *= -1

    def ai(self):
        if self.mode_selected == "mode_double_ball":
            distance_to_ball_one = self.ball_one.rect.x - self.right_paddle.rect.x
            distance_to_ball_two = self.ball_two.rect.x - self.right_paddle.rect.x

            if distance_to_ball_one > distance_to_ball_two:
                if self.ball_one.x_velocity > 0:
                    if self.random_offset is None:
                        self.random_offset = random.randint(-35, 35)

                    target = self.right_paddle.rect.centery + self.random_offset
                    if target > self.ball_one.rect.centery and self.right_paddle.rect.top >= 0:
                        self.right_paddle.move(up=True)
                    if target < self.ball_one.rect.centery and self.right_paddle.rect.bottom < self.height:
                        self.right_paddle.move(up=False)
                else:
                    self.random_offset = None

            else:
                if self.ball_two.x_velocity > 0 and distance_to_ball_one < distance_to_ball_two:
                    if self.random_offset is None:
                        self.random_offset = random.randint(-35, 35)

                    target = self.right_paddle.rect.centery + self.random_offset
                    if target > self.ball_two.rect.centery and self.right_paddle.rect.top >= 0:
                        self.right_paddle.move(up=True)
                    if target < self.ball_two.rect.centery and self.right_paddle.rect.bottom < self.height:
                        self.right_paddle.move(up=False)
                else:
                    self.random_offset = None

        elif self.mode_selected == "mode_double_paddle":
            for ball in self.balls_group:
                if ball.x_velocity > 0:
                    if self.random_offset is None:
                        self.random_offset = random.randint(-100, 100)

                    target = self.right_paddle.rect.centery + self.random_offset
                    if (target > ball.rect.centery) and (self.right_paddle.rect.top >= 0):
                        self.right_paddle.move(up=True)
                    if (target < ball.rect.centery) and (self.right_paddle.rect.bottom < self.height):
                        self.right_paddle.move(up=False)
                else:
                    self.random_offset = None

        else:
            super().ai()

    def mode_management(self):
        if self.mode_selected == "mode_obstacle":
            for obstacle in self.obstacles:
                pygame.draw.rect(self.screen, "red", obstacle)

        if not self.mode_checked:
            if self.mode_selected != "mode_double_paddle":
                self.paddle_width, self.paddle_height = 10, 100
                self.left_paddle = Paddle(0, (self.height // 2 - self.paddle_height // 2), self.paddle_width,
                                          self.paddle_height, "assets/paddle/paddle.png")
                self.right_paddle = Paddle((self.width - self.paddle_width),
                                           (self.height // 2 - self.paddle_height // 2),
                                           self.paddle_width, self.paddle_height, "assets/paddle/paddle.png",
                                           self.player_right_is_AI)

            if self.mode_selected != "mode_double_points":
                self.point = 1

            if self.mode_selected != "mode_super_speed":
                self.left_paddle.velocity = self.right_paddle.velocity = 6
                for ball in self.balls_group:
                    ball.speed_factor = 1

        self.mode_checked = True

    def randomize_mode(self):
        modes = ["mode_double_ball", "mode_super_speed", "mode_double_points", "mode_obstacle", "mode_double_paddle"]
        self.mode_selected = random.choice(modes)
        getattr(self, self.mode_selected)()

    def animate_mode_selection(self):
        self.screen.blit(self.image, (self.width // 2 - 48, self.height - 175))
        self.animate("mode_selection", stop=True)
        self.animation_start_time += 1/60

        if self.animation_start_time >= 1:
            text = self.font.render(self.mode_selected.replace("_", " "), True, (255, 175, 55))

            text_width = text.get_width()
            self.screen.blit(text, ((self.width // 2 - text_width // 2), (self.height - 95)))

    def mode_double_ball(self):
        self.mode_activated = True

    def mode_super_speed(self):
        self.left_paddle.velocity = self.right_paddle.velocity = 8
        for ball in self.balls_group:
            ball.speed_factor = 2
        self.mode_activated = True

    def mode_double_points(self):
        self.point = 2
        self.mode_activated = True

    def mode_obstacle(self):
        self.obstacles = []
        number_of_obstacle = 3
        for _ in range(number_of_obstacle):
            collision = True
            while collision:
                x_position = random.randint(275, 450) if random.choice([True, False]) \
                    else random.randint(650, 825)
                y_position = random.randint(175, 350) if random.choice([True, False]) \
                    else random.randint(400, 525)

                new_obstacle = pygame.Rect(x_position, y_position, 50, 50)
                collision = any(obstacle.colliderect(new_obstacle) for obstacle in self.obstacles)

            self.obstacles.append(new_obstacle)
        self.mode_activated = True

    def mode_double_paddle(self):
        self.paddle_width, self.paddle_height = 10, 240
        self.left_paddle = Paddle(0, (self.height // 2 - self.paddle_height // 2), self.paddle_width,
                                  self.paddle_height, "assets/paddle/double_paddle.png")

        self.right_paddle = Paddle((self.width - self.paddle_width),
                                   (self.height // 2 - self.paddle_height // 2),
                                   self.paddle_width, self.paddle_height, "assets/paddle/double_paddle.png",
                                   self.player_right_is_AI)
        self.mode_activated = True

    def reset_game_mode(self):
        self.balls_group.empty()
        self.mode_selected = ""
        self.mode_activated = False
        self.mode_checked = False
        self.animation_start_time = 0
        self.animation_index = 0

    def golden_ball_luck(self):
        if not self.number_rolled:
            roll_1 = random.randint(1, 100)
            if 1 <= roll_1 <= 5:
                self.ball_one = Ball(self.width // 2 - 11, self.height // 2, self.balls_group,
                                     "ball/golden_ball", True)
            else:
                self.ball_one = Ball(self.width // 2 - 11, self.height // 2, self.balls_group, "ball/ball")

            if self.mode_selected == "mode_double_ball":
                roll_2 = random.randint(1, 100)
                if 1 <= roll_2 <= 5:
                    self.ball_two = Ball(self.width // 2 - 11, self.height // 2, self.balls_group,
                                         "ball/golden_ball", True)
                else:
                    self.ball_two = Ball(self.width // 2 - 11, self.height // 2, self.balls_group, "ball/ball")

                if self.ball_one.x_velocity == self.ball_two.x_velocity:
                    self.ball_two.x_velocity *= -1

        self.number_rolled = True
