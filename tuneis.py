import pygame
import math
from config import (
    LARGURA, ALTURA,
    COR_FUNDO, COR_GRAMA_CLARA, COR_TEE, COR_HOLE,
    COR_BOLA_SOMBRA,
    RAIO_BURACO, RAIO_TUNEL,
    ATRITO, ATRITO_AREIA, VEL_MIN,
)
from paredes import colidir_rect
from agua import checar_buraco


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


def checar_tuneis(j, tuneis):
    if not j.em_tunel:
        for t in tuneis:
            ax, ay = t.pos_a
            bx, by = t.pos_b
            if math.hypot(j.x - ax, j.y - ay) < RAIO_TUNEL:
                j.x, j.y = float(bx), float(by)
                j.em_tunel = True
                return
            if math.hypot(j.x - bx, j.y - by) < RAIO_TUNEL:
                j.x, j.y = float(ax), float(ay)
                j.em_tunel = True
                return
    else:
        for t in tuneis:
            if (math.hypot(j.x - t.pos_a[0], j.y - t.pos_a[1]) < RAIO_TUNEL or
                    math.hypot(j.x - t.pos_b[0], j.y - t.pos_b[1]) < RAIO_TUNEL):
                return
        j.em_tunel = False


def atualizar_bola(j, paredes, buraco_pos, zonas, tuneis):
    j.x += j.vx
    j.y += j.vy

    for p in paredes:
        colidir_rect(j, p.rect)

    checar_tuneis(j, tuneis)

    for z in zonas:
        if z.tipo == "agua" and z.contem(j.x, j.y):
            j.x, j.y = j.pos_inicio_tacada
            j.vx = j.vy = 0.0
            j.tacadas += 1
            j.em_tunel = False
            return

    if checar_buraco(j, buraco_pos):
        return

    em_areia = any(z.tipo == "areia" and z.contem(j.x, j.y) for z in zonas)
    atrito = ATRITO_AREIA if em_areia else ATRITO

    j.vx *= atrito
    j.vy *= atrito
    if abs(j.vx) < VEL_MIN:
        j.vx = 0.0
    if abs(j.vy) < VEL_MIN:
        j.vy = 0.0


def desenhar_campo(tela, tee, buraco_pos, paredes, zonas, tuneis):
    tela.fill(COR_FUNDO)

    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    for z in zonas:
        z.desenhar(tela)

    for t in tuneis:
        t.desenhar(tela)

    pygame.draw.circle(tela, COR_TEE, tee, 14, 1)

    bx, by = buraco_pos
    pygame.draw.circle(tela, (10, 30, 15), (bx + 1, by + 2), RAIO_BURACO + 2)
    pygame.draw.circle(tela, COR_HOLE, (bx, by), RAIO_BURACO)
    pygame.draw.line(tela, (60, 40, 30), (bx, by - 3), (bx, by - 38), 2)
    pygame.draw.polygon(tela, (220, 50, 50),
                        [(bx, by - 38), (bx + 16, by - 33), (bx, by - 26)])

    for p in paredes:
        p.desenhar(tela)
