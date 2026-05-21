import pygame
import math
from config import (
    COR_BOLA_SOMBRA,
    COR_PAREDE,
    COR_PAREDE_DARK,
    RAIO_BOLA,
    VEL_MIN,
)


class Parede:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def desenhar(self, tela):
        sombra = self.rect.move(3, 4)
        pygame.draw.rect(tela, COR_BOLA_SOMBRA, sombra, border_radius=4)
        pygame.draw.rect(tela, COR_PAREDE, self.rect, border_radius=4)
        pygame.draw.rect(tela, COR_PAREDE_DARK, self.rect, 2, border_radius=4)


class Jogador:
    def __init__(self, nome, cor):
        self.nome = nome
        self.cor = cor
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.tacadas = 0
        self.pos_inicio_tacada = (0.0, 0.0)
        self.no_buraco = False
        self.em_tunel = False

    def reset(self, tee):
        self.x = float(tee[0])
        self.y = float(tee[1])
        self.vx = 0.0
        self.vy = 0.0
        self.tacadas = 0
        self.pos_inicio_tacada = (self.x, self.y)
        self.no_buraco = False
        self.em_tunel = False

    def parou(self):
        return abs(self.vx) < VEL_MIN and abs(self.vy) < VEL_MIN

    def desenhar(self, tela, ativo=False):
        ix, iy = int(self.x), int(self.y)

        pygame.draw.circle(tela, COR_BOLA_SOMBRA, (ix + 2, iy + 3), RAIO_BOLA)

        if ativo:
            pulse = (math.sin(pygame.time.get_ticks() * 0.008) + 1) * 0.5
            r = RAIO_BOLA + 4 + int(pulse * 4)
            surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.cor, 80), (r + 1, r + 1), r)
            tela.blit(surf, (ix - r - 1, iy - r - 1))

        pygame.draw.circle(tela, self.cor, (ix, iy), RAIO_BOLA)
        pygame.draw.circle(tela, (255, 255, 255), (ix - 2, iy - 2), 2)