import pygame
import math
from paredes_moveis import ParedeMovel

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
    for pm in fase.paredes_moveis:
        colidir_rect(j, pm.rect)

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
    for pm in fase.paredes_moveis:
        pm.desenhar(tela)

def desenhar_hud(tela, fonte_m, fonte_s, jogadores, jogador_idx, fase):
    painel = pygame.Surface((LARGURA, 55), pygame.SRCALPHA)
    painel.fill((0, 0, 0, 130))
    tela.blit(painel, (0, 0))

    info = fonte_m.render(f"Buraco {fase.numero}  •  Par {fase.par}", True, COR_TEXTO)
    tela.blit(info, (20, 15))

    j = jogadores[jogador_idx]
    vez = fonte_m.render(f"▶  {j.nome}", True, j.cor)
    tela.blit(vez, (LARGURA // 2 - vez.get_width() // 2, 15))

    x = LARGURA - 15
    for jj in reversed(jogadores):
        t = fonte_s.render(f"{jj.nome[:8]}: {jj.tacadas}", True, jj.cor)
        x -= t.get_width() + 18
        tela.blit(t, (x, 19))


def _label_par(tacadas, par):
    d = tacadas - par
    return {-3: "Albatross", -2: "Eagle", -1: "Birdie", 0: "Par", 1: "Bogey", 2: "Double Bogey"}.get(d, f"+{d}" if d > 0 else str(d))


def desenhar_fim_hole(tela, fonte_g, fonte_m, fonte_s, jogadores, fase, ultimo=False):
    tela.fill(COR_FUNDO)
    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    titulo = fonte_g.render(f"Buraco {fase.numero} concluído", True, COR_TEXTO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 70))
    par_txt = fonte_m.render(f"Par  {fase.par}", True, (230, 230, 200))
    tela.blit(par_txt, (LARGURA // 2 - par_txt.get_width() // 2, 125))

    painel_y = 175
    painel_h = 60 + len(jogadores) * 48
    painel = pygame.Rect(LARGURA // 2 - 260, painel_y, 520, painel_h)
    pygame.draw.rect(tela, (20, 50, 25), painel, border_radius=10)
    pygame.draw.rect(tela, (60, 100, 65), painel, 2, border_radius=10)

    cab = fonte_s.render("Jogador", True, (160, 200, 160))
    tela.blit(cab, (painel.x + 20, painel_y + 12))
    cab2 = fonte_s.render("Tacadas", True, (160, 200, 160))
    tela.blit(cab2, (painel.x + 310, painel_y + 12))
    cab3 = fonte_s.render("Resultado", True, (160, 200, 160))
    tela.blit(cab3, (painel.x + 400, painel_y + 12))
    pygame.draw.line(tela, (60, 100, 65), (painel.x + 10, painel_y + 34), (painel.right - 10, painel_y + 34), 1)

    for i, j in enumerate(jogadores):
        ry = painel_y + 44 + i * 48
        pygame.draw.circle(tela, j.cor, (painel.x + 20, ry + 14), 8)
        nome_t = fonte_m.render(j.nome[:14], True, j.cor)
        tela.blit(nome_t, (painel.x + 36, ry))
        tac_t = fonte_m.render(str(j.tacadas), True, COR_TEXTO)
        tela.blit(tac_t, (painel.x + 320, ry))
        label = _label_par(j.tacadas, fase.par)
        diff = j.tacadas - fase.par
        cor_label = (80, 200, 120) if diff < 0 else (230, 230, 230) if diff == 0 else (230, 120, 80)
        lab_t = fonte_s.render(label, True, cor_label)
        tela.blit(lab_t, (painel.x + 408, ry + 4))

    msg = "SPACE — ver ranking" if ultimo else "SPACE — próximo buraco"
    instr = fonte_m.render(msg, True, COR_TEXTO)
    tela.blit(instr, (LARGURA // 2 - instr.get_width() // 2, painel.bottom + 30))