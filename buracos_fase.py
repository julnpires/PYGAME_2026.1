import pygame
import math

from config import (
    LARGURA, ALTURA,
    COR_FUNDO, COR_GRAMA_CLARA, COR_TEXTO, COR_TEE, COR_HOLE,
    COR_BOLA_SOMBRA,
    RAIO_BOLA, RAIO_BURACO, RAIO_TUNEL,
    ATRITO, ATRITO_AREIA, VEL_MIN, POTENCIA_MAX_DRAG,
    COEF_RESTITUICAO, VEL_MAX_AFUNDA,
)

from paredes import Parede, Jogador
from agua import Agua
from areia import Areia
from esteiras import Esteira
from tuneis import Tunel

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
            if (
                math.hypot(j.x - t.pos_a[0], j.y - t.pos_a[1]) < RAIO_TUNEL
                or math.hypot(j.x - t.pos_b[0], j.y - t.pos_b[1]) < RAIO_TUNEL
            ):
                return
        j.em_tunel = False

def checar_buraco(j, buraco_pos):
    bx, by = buraco_pos
    dist = math.hypot(j.x - bx, j.y - by)
    if dist < RAIO_BURACO and math.hypot(j.vx, j.vy) < VEL_MAX_AFUNDA:
        j.no_buraco = True
        j.x = float(bx)
        j.y = float(by)
        j.vx = 0.0
        j.vy = 0.0
        return True
    return False

def atualizar_bola(j, fase):
    j.x += j.vx
    j.y += j.vy
    for e in fase.esteiras:
        e.aplicar(j)
    for p in fase.paredes:
        colidir_rect(j, p.rect)
    checar_tuneis(j, fase.tuneis)
    for a in fase.aguas:
        if a.contem(j.x, j.y):
            j.x, j.y = j.pos_inicio_tacada
            j.vx = 0.0
            j.vy = 0.0
            j.tacadas += 1
            j.em_tunel = False
            return
    if checar_buraco(j, fase.buraco_pos):
        return
    em_areia = any(a.contem(j.x, j.y) for a in fase.areias)
    atrito = ATRITO_AREIA if em_areia else ATRITO
    j.vx *= atrito
    j.vy *= atrito
    if abs(j.vx) < VEL_MIN:
        j.vx = 0.0
    if abs(j.vy) < VEL_MIN:
        j.vy = 0.0

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

def desenhar_campo(tela, fase):
    tela.fill(COR_FUNDO)
    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))
    for a in fase.areias:
        a.desenhar(tela)
    for g in fase.aguas:
        g.desenhar(tela)
    for e in fase.esteiras:
        e.desenhar(tela)
    for t in fase.tuneis:
        t.desenhar(tela)
    pygame.draw.circle(tela, COR_TEE, fase.tee, 14, 1)

    bx, by = fase.buraco_pos
    pygame.draw.circle(tela, (10, 30, 15), (bx + 1, by + 2), RAIO_BURACO + 2)
    pygame.draw.circle(tela, COR_HOLE, (bx, by), RAIO_BURACO)
    pygame.draw.line(tela, (60, 40, 30), (bx, by - 3), (bx, by - 38), 2)
    pygame.draw.polygon(tela, (220, 50, 50), [(bx, by - 38), (bx + 16, by - 33), (bx, by - 26)])
    for p in fase.paredes:
        p.desenhar(tela)

def desenhar_hud(tela, fonte_m, jogador, fase):
    painel = pygame.Surface((LARGURA, 50), pygame.SRCALPHA)
    painel.fill((0, 0, 0, 120))
    tela.blit(painel, (0, 0))
    info = fonte_m.render(f"Buraco {fase.numero}  •  Par {fase.par}", True, COR_TEXTO)
    tela.blit(info, (40, 12))
    vez = fonte_m.render(f"Vez: {jogador.nome}  (tacadas: {jogador.tacadas})", True, COR_TEXTO)
    tela.blit(vez, (LARGURA // 2 - vez.get_width() // 2, 12))

def desenhar_fim_hole(tela, fonte_g, fonte_m, jogador, fase):
    tela.fill(COR_FUNDO)
    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))
    titulo = fonte_g.render(f"Buraco {fase.numero} concluido", True, COR_TEXTO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))
    par = fonte_m.render(f"Par {fase.par}", True, (230, 230, 200))
    tela.blit(par, (LARGURA // 2 - par.get_width() // 2, 125))
    info = fonte_m.render(f"{jogador.nome} terminou em {jogador.tacadas} tacadas.", True, COR_TEXTO)
    tela.blit(info, (LARGURA // 2 - info.get_width() // 2, 160))
    instr = fonte_m.render("Pressione SPACE para continuar", True, COR_TEXTO)
    tela.blit(instr, (LARGURA // 2 - instr.get_width() // 2, 230))