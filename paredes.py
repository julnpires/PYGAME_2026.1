import pygame
import math
from config import (
    LARGURA, ALTURA, COR_FUNDO, COR_GRAMA_CLARA,
    COR_BOLA_SOMBRA, COR_HOLE, COR_TEE,
    COR_PAREDE, COR_PAREDE_DARK,
    RAIO_BOLA, RAIO_BURACO,
    ATRITO, VEL_MIN, POTENCIA_MAX_DRAG, COEF_RESTITUICAO,
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

    def reset(self, tee):
        self.x = float(tee[0])
        self.y = float(tee[1])
        self.vx = 0.0
        self.vy = 0.0
        self.tacadas = 0
        self.pos_inicio_tacada = (self.x, self.y)
        self.no_buraco = False

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


def desenhar_campo(tela, tee, hole, paredes):
    tela.fill(COR_FUNDO)

    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    pygame.draw.circle(tela, COR_TEE, tee, 14, 1)

    bx, by = hole
    pygame.draw.circle(tela, COR_HOLE, (bx, by), RAIO_BURACO)
    pygame.draw.line(tela, (60, 40, 30), (bx, by - 3), (bx, by - 38), 2)
    pygame.draw.polygon(tela, (220, 50, 50),
                        [(bx, by - 38), (bx + 16, by - 33), (bx, by - 26)])

    for p in paredes:
        p.desenhar(tela)


def desenhar_mira(tela, jogador, mouse_pos):
    mx, my = mouse_pos
    dx = jogador.x - mx
    dy = jogador.y - my
    dist = math.hypot(dx, dy)
    if dist < 5:
        return

    dist_cap = min(dist, POTENCIA_MAX_DRAG)
    dx_n, dy_n = dx / dist, dy / dist
    end_x = jogador.x + dx_n * dist_cap
    end_y = jogador.y + dy_n * dist_cap
    pct = dist_cap / POTENCIA_MAX_DRAG
    cor = (255, int(220 * (1 - pct)) + 35, int(80 * (1 - pct)))

    segmentos = 12
    for i in range(0, segmentos, 2):
        t1 = i / segmentos
        t2 = (i + 1) / segmentos
        sx = jogador.x + (end_x - jogador.x) * t1
        sy = jogador.y + (end_y - jogador.y) * t1
        ex = jogador.x + (end_x - jogador.x) * t2
        ey = jogador.y + (end_y - jogador.y) * t2
        pygame.draw.line(tela, cor, (sx, sy), (ex, ey), 4)

    ang = math.atan2(dy_n, dx_n)
    for off in (2.6, -2.6):
        tx = end_x + math.cos(ang + off) * 14
        ty = end_y + math.sin(ang + off) * 14
        pygame.draw.line(tela, cor, (end_x, end_y), (tx, ty), 4)

    bar_w = 80
    bar_x = mx - bar_w // 2
    bar_y = my + 25
    pygame.draw.rect(tela, (40, 40, 40), (bar_x, bar_y, bar_w, 8), border_radius=4)
    pygame.draw.rect(tela, cor, (bar_x, bar_y, int(bar_w * pct), 8), border_radius=4)


def colidir_rect(j, rect):
    cx = max(rect.left, min(j.x, rect.right))
    cy = max(rect.top, min(j.y, rect.bottom))
    dx = j.x - cx
    dy = j.y - cy
    dist_sq = dx * dx + dy * dy

    if dist_sq < RAIO_BOLA * RAIO_BOLA:
        if dist_sq < 0.0001:
            esq = j.x - rect.left
            dir_ = rect.right - j.x
            cima = j.y - rect.top
            baixo = rect.bottom - j.y
            menor = min(esq, dir_, cima, baixo)

            if menor == esq:
                j.x = rect.left - RAIO_BOLA - 0.5
                j.vx = -abs(j.vx) * COEF_RESTITUICAO
            elif menor == dir_:
                j.x = rect.right + RAIO_BOLA + 0.5
                j.vx = abs(j.vx) * COEF_RESTITUICAO
            elif menor == cima:
                j.y = rect.top - RAIO_BOLA - 0.5
                j.vy = -abs(j.vy) * COEF_RESTITUICAO
            else:
                j.y = rect.bottom + RAIO_BOLA + 0.5
                j.vy = abs(j.vy) * COEF_RESTITUICAO
            return True

        dist = math.sqrt(dist_sq)
        nx, ny = dx / dist, dy / dist
        sobra = RAIO_BOLA - dist
        j.x += nx * sobra
        j.y += ny * sobra

        dot = j.vx * nx + j.vy * ny
        if dot < 0:
            j.vx -= 2 * dot * nx
            j.vy -= 2 * dot * ny
            j.vx *= COEF_RESTITUICAO
            j.vy *= COEF_RESTITUICAO
        return True

    return False


def atualizar_bola(j, paredes):
    j.x += j.vx
    j.y += j.vy

    for p in paredes:
        colidir_rect(j, p.rect)

    j.vx *= ATRITO
    j.vy *= ATRITO

    if abs(j.vx) < VEL_MIN:
        j.vx = 0.0
    if abs(j.vy) < VEL_MIN:
        j.vy = 0.0
