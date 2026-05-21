import pygame
from config import COR_AGUA, COR_AGUA_CLARA

class Agua:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def contem(self, x, y):
        return self.rect.collidepoint(x, y)

    def desenhar(self, tela):
        pygame.draw.rect(tela, COR_AGUA, self.rect, border_radius=10)
        pygame.draw.rect(
            tela,
            COR_AGUA_CLARA,
            self.rect.inflate(-10, -10),
            border_radius=8
        )
        for i in range(3):
            y = self.rect.y + 20 + i * 25
            if y < self.rect.bottom - 10:
                pygame.draw.arc(
                    tela,
                    (255, 255, 255),
                    (self.rect.x + 15, y, 30, 10),
                    3.14,
                    6.28,
                    2
                )