import pygame
import random
import math

from animation import AnimateSprite


class Ball(AnimateSprite):
    def __init__(self, x, y, ball_group, name_path, is_golden=False):
        super().__init__(name_path)
        self.image = self.get_image(0, 0, 16, 16)  # image d'apparition
        self.image = pygame.transform.scale(self.image, (22, 22))
        self.ball_mask = pygame.mask.from_surface(self.image)
        self.image.set_colorkey([255, 255, 255])
        self.rect = self.image.get_rect()
        self.is_golden = is_golden

        self.original_x = x
        self.original_y = y
        self.rect.x = x
        self.rect.y = y
        self.radius = 7.5
        self.original_x_velocity = 5
        self.x_velocity = 5 * random.choice([-1, 1])
        self.y_velocity = random.randint(-3, 3)
        self.speed_factor = 1
        self.color = (255, 255, 255)

        ball_group.add(self)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def move(self):
        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity
        self.animate("ball")

    def reset(self):
        self.rect.x = self.original_x
        self.rect.y = self.original_y
        self.y_velocity = random.randint(-3, 3)
        self.x_velocity = 5 if self.x_velocity > 0 else -5
        self.x_velocity *= -1
