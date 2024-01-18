import pygame


class AnimateSprite(pygame.sprite.Sprite):
    def __init__(self, dossier):
        super().__init__()
        self.image = pygame.image.load(f"assets/{dossier}.png")
        self.images = {
            "ball": self.get_images(0, 4, 16, 16, 16, 22),
            "validate": self.get_images(0, 4, 26, 26, 26),
            "mode_selection": self.get_images(0, 8, 48, 48, 48, 96)
        }
        self.animation_index = 0
        self.speed = 2
        self.clock = 0

    def animate(self, name, stop=False):
        self.image = self.images[name][self.animation_index]
        self.image.set_colorkey((255, 255, 255))
        self.clock += self.speed * 8

        if self.clock >= 100:
            self.animation_index += 1

            if self.animation_index >= len(self.images[name]):
                if stop:
                    self.animation_index = len(self.images[name]) - 1
                    self.image = self.images[name][self.animation_index]
                else:
                    self.animation_index = 0

            self.clock = 0

    def get_images(self, y, number, width, height, pixel, scaling=None):
        images = []

        for i in range(0, number):
            x = i * pixel
            image = self.get_image(x, y, width, height)
            if scaling is not None:
                image = pygame.transform.scale(image, (scaling, scaling))
            images.append(image)

        return images

    def get_image(self, x, y, width=32, height=32):
        image = pygame.Surface([width, height]).convert()
        image.set_colorkey([255, 255, 255])
        image.blit(self.image, (0, 0), (x, y, width, height))

        return image
