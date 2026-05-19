import pygame
import math
import random
from config import (
    LARGURA, ALTURA,
    COR_FUNDO, COR_GRAMA_CLARA, COR_TEXTO, COR_TEE, COR_HOLE,
    COR_AREIA, COR_AREIA_DARK, COR_AGUA, COR_AGUA_CLARA,
    RAIO_BURACO,
    ATRITO, ATRITO_AREIA, VEL_MIN, VEL_MAX_AFUNDA,
)
from paredes import colidir_rect


class Zona:
    """Areia ou água."""
    def __init__(self, x, y, w, h, tipo):
        self.rect = pygame.Rect(x, y, w, h)
        self.tipo = tipo

    def desenhar(self, tela):
        if self.tipo == "areia":
            pygame.draw.rect(tela, COR_AREIA, self.rect, border_radius=10)
            random.seed(self.rect.x * 7 + self.rect.y)
            for _ in range(self.rect.w * self.rect.h // 200):
                px = random.randint(self.rect.left + 4, self.rect.right - 4)
                py = random.randint(self.rect.top + 4, self.rect.bottom - 4)
                pygame.draw.circle(tela, COR_AREIA_DARK, (px, py), 1)

        elif self.tipo == "agua":
            pygame.draw.rect(tela, COR_AGUA, self.rect, border_radius=10)
            pygame.draw.rect(tela, COR_AGUA_CLARA, self.rect.inflate(-10, -10), border_radius=8)
            for i in range(3):
                y = self.rect.y + 20 + i * 25
                if y < self.rect.bottom - 10:
                    pygame.draw.arc(tela, (255, 255, 255),
                                    (self.rect.x + 15, y, 30, 10), 3.14, 6.28, 2)

    def contem(self, x, y):
        return self.rect.collidepoint(x, y)


def checar_buraco(j, buraco_pos):
    bx, by = buraco_pos
    dist = math.hypot(j.x - bx, j.y - by)
    if dist < RAIO_BURACO and math.hypot(j.vx, j.vy) < VEL_MAX_AFUNDA:
        j.no_buraco = True
        j.x, j.y = float(bx), float(by)
        j.vx = j.vy = 0.0
        return True
    return False


def atualizar_bola(j, paredes, buraco_pos, zonas):
    j.x += j.vx
    j.y += j.vy

    for p in paredes:
        colidir_rect(j, p.rect)

    for z in zonas:
        if z.tipo == "agua" and z.contem(j.x, j.y):
            j.x, j.y = j.pos_inicio_tacada
            j.vx = j.vy = 0.0
            j.tacadas += 1
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


def desenhar_campo(tela, tee, buraco_pos, paredes, zonas):
    tela.fill(COR_FUNDO)

    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    for z in zonas:
        z.desenhar(tela)

    pygame.draw.circle(tela, COR_TEE, tee, 14, 1)

    bx, by = buraco_pos
    pygame.draw.circle(tela, (10, 30, 15), (bx + 1, by + 2), RAIO_BURACO + 2)
    pygame.draw.circle(tela, COR_HOLE, (bx, by), RAIO_BURACO)
    pygame.draw.line(tela, (60, 40, 30), (bx, by - 3), (bx, by - 38), 2)
    pygame.draw.polygon(tela, (220, 50, 50),
                        [(bx, by - 38), (bx + 16, by - 33), (bx, by - 26)])

    for p in paredes:
        p.desenhar(tela)


def desenhar_fim_hole(tela, fonte_g, fonte_m, jogador):
    tela.fill(COR_FUNDO)

    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    titulo = fonte_g.render("Buraco concluido", True, COR_TEXTO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

    info = fonte_m.render(
        f"{jogador.nome} terminou em {jogador.tacadas} tacadas.",
        True, COR_TEXTO,
    )
    tela.blit(info, (LARGURA // 2 - info.get_width() // 2, 160))

    instr = fonte_m.render("Pressione SPACE para jogar de novo", True, COR_TEXTO)
    tela.blit(instr, (LARGURA // 2 - instr.get_width() // 2, 230))
