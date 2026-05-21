from config import *
import pygame
from math import hypot
import math

class Esteira:
    def __init__(self, x, y, w, h, dx, dy, forca=0.3):
        self.rect = pygame.Rect(x, y, w, h)
        dist = math.hypot(dx, dy)
        self.dx = dx / dist if dist > 0 else 0.0
        self.dy = dy / dist if dist > 0 else 0.0
        self.forca = forca

    def aplicar(self, j):
        if self.rect.collidepoint(j.x, j.y):
            j.vx += self.dx * self.forca
            j.vy += self.dy * self.forca
            return True
        return False

    def desenhar(self, tela):
        old_clip = tela.get_clip()
        tela.set_clip(self.rect)
        pygame.draw.rect(tela, COR_ESTEIRA, self.rect, border_radius=8)
        spacing = 30
        offset = (pygame.time.get_ticks() * 0.06) % spacing
        ax_x = self.dx
        ax_y = self.dy
        px_x = -self.dy
        px_y = self.dx
        long_max = max(self.rect.w, self.rect.h) + spacing
        for i in range(-long_max // spacing - 1, long_max // spacing + 2):
            for j_par in range(-long_max // spacing - 1, long_max // spacing + 2):
                cx = self.rect.centerx + (i * spacing + offset) * ax_x + (j_par * spacing) * px_x
                cy = self.rect.centery + (i * spacing + offset) * ax_y + (j_par * spacing) * px_y
                if not self.rect.collidepoint(cx, cy):
                    continue

                head_x = cx + ax_x * 7
                head_y = cy + ax_y * 7
                tail_x = cx - ax_x * 7
                tail_y = cy - ax_y * 7
                pygame.draw.line(tela, COR_ESTEIRA_SETA, (tail_x, tail_y), (head_x, head_y), 2)
                pygame.draw.line(
                    tela,
                    COR_ESTEIRA_SETA,
                    (head_x, head_y),
                    (head_x - ax_x * 4 + px_x * 3, head_y - ax_y * 4 + px_y * 3),
                    2
                )
                pygame.draw.line(
                    tela,
                    COR_ESTEIRA_SETA,
                    (head_x, head_y),
                    (head_x - ax_x * 4 - px_x * 3, head_y - ax_y * 4 - px_y * 3),
                    2
                )
        tela.set_clip(old_clip)
        pygame.draw.rect(tela, COR_ESTEIRA_DARK, self.rect, 2, border_radius=8)