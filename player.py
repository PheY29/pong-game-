import pygame


class Paddle:
    def __init__(self, x, y, width, height, image_path, is_ai=False):
        self.paddle_img = pygame.image.load(image_path).convert_alpha()
        self.paddle_mask = pygame.mask.from_surface(self.paddle_img)
        # self.mask = self.paddle_mask.to_surface()  # afficher le masks a l'ecran
        self.rect = self.paddle_img.get_rect()
        self.original_x = x
        self.original_y = y
        self.rect.x = x
        self.rect.y = y
        self.width = width
        self.height = height
        self.color = (255, 255, 255)
        self.velocity = 6
        self.is_ai = is_ai

    def draw(self, screen):
        screen.blit(self.paddle_img, (self.rect.x, self.rect.y))
        # screen.blit(self.mask, (50, 50))  # afficher le masks a l'ecran

    def move(self, up=True):
        if up:
            self.rect.y -= self.velocity
        else:
            self.rect.y += self.velocity

    def reset(self):
        self.rect.x = self.original_x
        self.rect.y = self.original_y
