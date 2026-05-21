import pygame
import random
from config import COR_AREIA, COR_AREIA_DARK

class Areia:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def contem(self, x, y):
        return self.rect.collidepoint(x, y)

    def desenhar(self, tela):
        pygame.draw.rect(tela, COR_AREIA, self.rect, border_radius=10)

        random.seed(self.rect.x * 7 + self.rect.y)
        for _ in range(self.rect.w * self.rect.h // 200):
            px = random.randint(self.rect.left + 4, self.rect.right - 4)
            py = random.randint(self.rect.top + 4, self.rect.bottom - 4)
            pygame.draw.circle(tela, COR_AREIA_DARK, (px, py), 1)