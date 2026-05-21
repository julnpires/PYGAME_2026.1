import pygame
import math
from config import COR_BOLA_SOMBRA, RAIO_TUNEL


class Tunel:
    """Par de portais. Bola entra em um e sai no outro."""
    def __init__(self, pos_a, pos_b, cor):
        self.pos_a = pos_a
        self.pos_b = pos_b
        self.cor = cor

    def desenhar(self, tela):
        t = pygame.time.get_ticks() * 0.003
        for px, py in (self.pos_a, self.pos_b):
            pygame.draw.circle(tela, COR_BOLA_SOMBRA, (px + 2, py + 3), RAIO_TUNEL + 3)
            pygame.draw.circle(tela, self.cor, (px, py), RAIO_TUNEL + 3)
            pygame.draw.circle(tela, (20, 18, 30), (px, py), RAIO_TUNEL)

            for i in range(3):
                ang = t + i * (2 * math.pi / 3)
                dx = math.cos(ang) * (RAIO_TUNEL - 5)
                dy = math.sin(ang) * (RAIO_TUNEL - 5)
                pygame.draw.circle(tela, self.cor, (int(px + dx), int(py + dy)), 3)

            for i in range(3):
                ang = -t * 1.5 + i * (2 * math.pi / 3)
                dx = math.cos(ang) * (RAIO_TUNEL - 11)
                dy = math.sin(ang) * (RAIO_TUNEL - 11)
                cor_dim = tuple(c // 2 for c in self.cor)
                pygame.draw.circle(tela, cor_dim, (int(px + dx), int(py + dy)), 2)