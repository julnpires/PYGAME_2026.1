import pygame
import sys
import os
import math

#imports das outras partes do jogo, para melhor organização
from paredes_moveis import ParedeMovel
from config import (
    LARGURA, ALTURA, FPS,
    COR_FUNDO, COR_GRAMA_CLARA, COR_TEXTO, COR_CAIXA,
    COR_BOTAO, COR_BOTAO_HOVER,
    POTENCIA_MAX_DRAG, POTENCIA_FATOR,
    COR_TUNEL_1, COR_TUNEL_2, COR_TUNEL_3,
    CORES_JOGADORES,
)
from paredes import Parede, Jogador
from areia import Areia
from agua import Agua
from esteiras import Esteira
from tuneis import Tunel
from buracos_fase import (
    atualizar_bola,
    desenhar_campo,
    desenhar_mira,
    desenhar_hud,
    desenhar_fim_hole,
)
from ranking.ranking import adicionar_ao_ranking, carregar_ranking

#classe das Fases
class Fase:
    def __init__(self, numero, par, tee, buraco_pos,
                 paredes=None, areias=None, aguas=None,
                 tuneis=None, esteiras=None, paredes_moveis=None):
        self.numero = numero
        self.par = par
        self.tee = tee
        self.buraco_pos = buraco_pos
        self.paredes = paredes or []
        self.areias = areias or []
        self.aguas = aguas or []
        self.tuneis = tuneis or []
        self.esteiras = esteiras or []
        self.paredes_moveis = paredes_moveis or []

def criar_fases():
    return [
        Fase(
            numero=1, par=3, tee=(130, 350), buraco_pos=(870, 350),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(485, 200, 30, 300),
            ],
        ),

        Fase(
            numero=2, par=4, tee=(130, 600), buraco_pos=(870, 250),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(180, 150, 30, 320), Parede(180, 150, 540, 30),
                Parede(720, 150, 30, 280),
            ],
            areias=[Areia(380, 500, 220, 110)],
            aguas=[Agua(600, 480, 130, 120)],
            tuneis=[Tunel((190, 560), (780, 500), COR_TUNEL_1)],
            esteiras=[Esteira(800, 340, 50, 250, 0, -1, 0.35)],
            paredes_moveis=[ParedeMovel(775, 300, 175, 25, 745, 455, velocidade=1.3)],
        ),

        Fase(
            numero=3, par=4, tee=(130, 350), buraco_pos=(870, 350),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(450, 80, 30, 130), Parede(450, 490, 30, 140),
            ],
            aguas=[Agua(380, 230, 240, 240)],
            tuneis=[Tunel((260, 220), (760, 470), COR_TUNEL_2)],
            paredes_moveis=[ParedeMovel(800, 110, 30, 100, 800, 480, velocidade=1.2)],
        ),

        Fase(
            numero=4, par=4, tee=(130, 130), buraco_pos=(870, 600),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(220, 80, 30, 240), Parede(220, 290, 280, 30),
                Parede(620, 380, 30, 260), Parede(380, 380, 270, 30),
                Parede(750, 200, 30, 200),
            ],
            areias=[Areia(520, 220, 80, 130)],
            aguas=[Agua(300, 430, 110, 110)],
            tuneis=[Tunel((300, 170), (800, 500), COR_TUNEL_3)],
            esteiras=[Esteira(280, 340, 90, 40, 1, 0, 0.18)],
        ),

        Fase(
            numero=5, par=4, tee=(130, 350), buraco_pos=(870, 600),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(485, 30, 30, 640), Parede(515, 380, 470, 30),
            ],
            tuneis=[
                Tunel((170, 250), (590, 240), COR_TUNEL_1),
                Tunel((820, 320), (640, 560), COR_TUNEL_2),
            ],
            esteiras=[Esteira(500, 210, 360, 60, -1, 0, 0.48)],
        ),

        Fase(
            numero=6, par=5, tee=(130, 350), buraco_pos=(900, 350),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(60, 230, 700, 30), Parede(60, 440, 700, 30),
                Parede(60, 150, 560, 30),
                Parede(700, 150, 90, 30),
            ],
            esteiras=[
                Esteira(150, 90, 420, 90, 1, 0, 0.18),
                Esteira(180, 480, 420, 130, -1, 0, 0.28),
            ],
            paredes_moveis=[
                ParedeMovel(250, 290, 30, 130, 450, 290, velocidade=1.8, fase_inicial=0.0),
                ParedeMovel(550, 290, 30, 130, 700, 290, velocidade=2.0, fase_inicial=1.5),
            ],
        ),
    ]

#jogadores
def proximo_jogador(jogadores, atual):
    n = len(jogadores)
    for i in range(1, n + 1):
        idx = (atual + i) % n
        if not jogadores[idx].no_buraco:
            return idx
    return atual

#menu
def desenhar_menu(surf, fonte_g, fonte_m, fonte_s,
                  cadastrados, nome_input, ativo_input, mouse_pos):
    surf.fill(COR_FUNDO)
    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(surf, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    titulo = fonte_g.render("MINI GOLF", True, COR_TEXTO)
    surf.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 30))

    # ── painel de jogadores (2×2) ──────────────────────────────────────────
    panel = pygame.Rect(LARGURA // 2 - 270, 110, 540, 195)
    pygame.draw.rect(surf, COR_CAIXA, panel, border_radius=10)
    pygame.draw.rect(surf, (80, 120, 85), panel, 2, border_radius=10)
    lbl = fonte_s.render("Jogadores  (máx. 4)", True, (160, 200, 160))
    surf.blit(lbl, (panel.x + 12, panel.y + 8))

    slot_w, slot_h = 245, 72
    slots_pos = [
        (panel.x + 10,  panel.y + 35),
        (panel.x + 285, panel.y + 35),
        (panel.x + 10,  panel.y + 115),
        (panel.x + 285, panel.y + 115),
    ]
    for i, (sx, sy) in enumerate(slots_pos):
        slot = pygame.Rect(sx, sy, slot_w, slot_h)
        if i < len(cadastrados):
            nome_c, cor_c = cadastrados[i]
            bg = tuple(max(0, c // 5) for c in cor_c)
            pygame.draw.rect(surf, bg, slot, border_radius=8)
            pygame.draw.rect(surf, cor_c, slot, 2, border_radius=8)
            pygame.draw.circle(surf, cor_c, (sx + 18, sy + slot_h // 2), 9)
            t = fonte_m.render(nome_c, True, cor_c)
            surf.blit(t, (sx + 34, sy + slot_h // 2 - t.get_height() // 2))
        else:
            pygame.draw.rect(surf, (28, 52, 32), slot, border_radius=8)
            pygame.draw.rect(surf, (55, 80, 60), slot, 1, border_radius=8)
            v = fonte_s.render("— vazio —", True, (70, 100, 75))
            surf.blit(v, (sx + slot_w // 2 - v.get_width() // 2,
                          sy + slot_h // 2 - v.get_height() // 2))

    box = pygame.Rect(LARGURA // 2 - 200, 330, 400, 45)
    pygame.draw.rect(surf, COR_CAIXA, box, border_radius=8)
    borda = COR_TEXTO if ativo_input else (80, 110, 85)
    pygame.draw.rect(surf, borda, box, 2, border_radius=8)
    nome_lbl = fonte_s.render("Nome do jogador:", True, (180, 210, 180))
    surf.blit(nome_lbl, (box.x, box.y - 22))
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 and ativo_input else ""
    surf.blit(fonte_m.render(nome_input + cursor, True, COR_TEXTO), (box.x + 10, box.y + 10))

    b_add  = pygame.Rect(LARGURA // 2 - 215, 392, 200, 42)
    b_rem  = pygame.Rect(LARGURA // 2 + 15,  392, 200, 42)
    b_ini  = pygame.Rect(LARGURA // 2 - 150, 450, 300, 50)
    b_how  = pygame.Rect(LARGURA // 2 - 150, 515, 300, 45)
    b_rank = pygame.Rect(LARGURA // 2 - 150, 575, 300, 45)

    pode_add = len(cadastrados) < 4 and bool(nome_input.strip())
    pode_rem = len(cadastrados) > 0
    pode_ini = len(cadastrados) > 0

    def btn(rect, texto, ativo=True):
        hover = rect.collidepoint(mouse_pos) and ativo
        cor_bg = COR_BOTAO_HOVER if hover else (COR_BOTAO if ativo else (22, 45, 27))
        cor_bd = COR_TEXTO if ativo else (55, 80, 60)
        pygame.draw.rect(surf, cor_bg, rect, border_radius=8)
        pygame.draw.rect(surf, cor_bd, rect, 2, border_radius=8)
        t = fonte_m.render(texto, True, cor_bd)
        surf.blit(t, (rect.centerx - t.get_width() // 2,
                      rect.centery - t.get_height() // 2))

    btn(b_add,  "Adicionar",   pode_add)
    btn(b_rem,  "Remover",     pode_rem)
    btn(b_ini,  "Iniciar",     pode_ini)
    btn(b_how,  "Como Jogar")
    btn(b_rank, "Ranking")

    return box, b_add, b_rem, b_ini, b_how, b_rank

#ranking na tela
def desenhar_ranking_tela(surf, fonte_g, fonte_m, fonte_mono):
    data = carregar_ranking()
    surf.fill((15, 35, 20))

    titulo = fonte_g.render("RANKING", True, COR_TEXTO)
    surf.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 30))

    cab = fonte_mono.render(
        f"{'#':<4}{'Nome':<16}{'Tacadas':<10}{'Fases':<8}{'Media':<8}Data",
        True, (160, 200, 160),
    )
    surf.blit(cab, (60, 105))
    pygame.draw.line(surf, (70, 120, 80), (60, 128), (LARGURA - 60, 128), 1)

    cores_pos = {0: (220, 200, 60), 1: (190, 190, 190), 2: (210, 140, 70)}
    for i, e in enumerate(data.get("all_time", [])[:15]):
        cor = cores_pos.get(i, COR_TEXTO)
        linha = fonte_mono.render(
            f"{i + 1:<4}{e['nome'][:14]:<16}{e['total_tacadas']:<10}"
            f"{e['fases']:<8}{e['media']:<8}{e['data']}",
            True, cor,
        )
        surf.blit(linha, (60, 140 + i * 30))

    esc = fonte_m.render("ESC — voltar ao menu", True, (130, 170, 130))
    surf.blit(esc, (LARGURA // 2 - esc.get_width() // 2, ALTURA - 45))

#função principal, onde o jogo vai rodar
def main():
    pygame.init()
    pygame.mixer.init()
    # Tela cheia com resolução do monitor
    info = pygame.display.Info()
    TELA_W, TELA_H = info.current_w, info.current_h
    tela = pygame.display.set_mode((TELA_W, TELA_H), pygame.FULLSCREEN)
    pygame.display.set_caption("Mini Golf")
    ratio = LARGURA / ALTURA
    if TELA_W / TELA_H >= ratio:
        h_sc = TELA_H
        w_sc = int(TELA_H * ratio)
    else:
        w_sc = TELA_W
        h_sc = int(TELA_W / ratio)
    off_x = (TELA_W - w_sc) // 2
    off_y = (TELA_H - h_sc) // 2

    surf = pygame.Surface((LARGURA, ALTURA))

    def mouse_jogo():
        rx, ry = pygame.mouse.get_pos()
        return (
            (rx - off_x) * LARGURA / w_sc,
            (ry - off_y) * ALTURA / h_sc,
        )

    def ev_jogo(pos):
        return (
            (pos[0] - off_x) * LARGURA / w_sc,
            (pos[1] - off_y) * ALTURA / h_sc,
        )

    clock = pygame.time.Clock()
    fonte_g    = pygame.font.SysFont("Arial", 48, bold=True)
    fonte_m    = pygame.font.SysFont("Arial", 24)
    fonte_s    = pygame.font.SysFont("Arial", 18)
    fonte_mono = pygame.font.SysFont("Courier New", 18)
    som_tacada = pygame.mixer.Sound("assets/sounds/single-knock.wav")
    som_buraco = pygame.mixer.Sound("assets/sounds/the-ball-hit-the-hole.wav")

    estado     = "MENU"
    cadastrados = []          # [(nome, cor), ...]
    nome_input  = ""
    input_ativo = True

    fases       = criar_fases()
    fase_idx    = 0
    fase        = fases[fase_idx]
    jogadores   = []
    jogador_idx = 0
    aiming      = False

    box = b_add = b_rem = b_ini = b_how = b_rank = None

    rodando = True
    while rodando:
        mouse_pos = mouse_jogo()
        dt = clock.tick(FPS) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                rodando = False
            if estado == "MENU":
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    gpos = ev_jogo(ev.pos)
                    input_ativo = box.collidepoint(gpos) if box else False

                    if b_add and b_add.collidepoint(gpos) and nome_input.strip() and len(cadastrados) < 4:
                        cor = CORES_JOGADORES[len(cadastrados)]
                        cadastrados.append((nome_input.strip(), cor))
                        nome_input = ""

                    elif b_rem and b_rem.collidepoint(gpos) and cadastrados:
                        cadastrados.pop()

                    elif b_ini and b_ini.collidepoint(gpos) and cadastrados:
                        fases = criar_fases()
                        fase_idx = 0
                        fase = fases[fase_idx]
                        jogadores = [Jogador(n, c) for n, c in cadastrados]
                        for j in jogadores:
                            j.reset(fase.tee)
                        jogador_idx = 0
                        aiming = False
                        estado = "JOGANDO"

                    elif b_how and b_how.collidepoint(gpos):
                        estado = "REGRAS"

                    elif b_rank and b_rank.collidepoint(gpos):
                        estado = "RANKING"

                if ev.type == pygame.KEYDOWN and input_ativo:
                    if ev.key == pygame.K_BACKSPACE:
                        nome_input = nome_input[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if nome_input.strip() and len(cadastrados) < 4:
                            cor = CORES_JOGADORES[len(cadastrados)]
                            cadastrados.append((nome_input.strip(), cor))
                            nome_input = ""
                    elif ev.unicode.isprintable() and len(nome_input) < 14:
                        nome_input += ev.unicode

            elif estado == "JOGANDO" and jogadores:
                jatual = jogadores[jogador_idx]
                if jatual.parou() and not jatual.no_buraco:
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        gpos = ev_jogo(ev.pos)
                        if math.hypot(gpos[0] - jatual.x, gpos[1] - jatual.y) < 50:
                            aiming = True
                    elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and aiming:
                        gpos = ev_jogo(ev.pos)
                        dx = jatual.x - gpos[0]
                        dy = jatual.y - gpos[1]
                        dist = math.hypot(dx, dy)
                        if dist > 8:
                            dist_cap = min(dist, POTENCIA_MAX_DRAG)
                            dx_n, dy_n = dx / dist, dy / dist
                            jatual.pos_inicio_tacada = (jatual.x, jatual.y)
                            jatual.vx = dx_n * dist_cap * POTENCIA_FATOR
                            jatual.vy = dy_n * dist_cap * POTENCIA_FATOR
                            jatual.tacadas += 1
                            som_tacada.play()
                        aiming = False

            elif estado == "FIM_HOLE":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    aiming = False
                    for j in jogadores:
                        j.tacadas_total += j.tacadas
                    fase_idx += 1
                    if fase_idx >= len(fases):
                        adicionar_ao_ranking(jogadores, len(fases))
                        estado = "RANKING"
                    else:
                        fase = fases[fase_idx]
                        for j in jogadores:
                            j.reset(fase.tee)
                        jogador_idx = 0
                        estado = "JOGANDO"

        if estado == "JOGANDO" and jogadores and fase:
            jatual = jogadores[jogador_idx]
            for pm in fase.paredes_moveis:
                pm.update(dt)

            if not jatual.parou() and not jatual.no_buraco:
                atualizar_bola(jatual, fase)
                if jatual.no_buraco:
                    som_buraco.play()
                    if all(j.no_buraco for j in jogadores):
                        estado = "FIM_HOLE"
                    else:
                        jogador_idx = proximo_jogador(jogadores, jogador_idx)
                        aiming = False

        if estado == "MENU":
            box, b_add, b_rem, b_ini, b_how, b_rank = desenhar_menu(
                surf, fonte_g, fonte_m, fonte_s,
                cadastrados, nome_input, input_ativo, mouse_pos,
            )

        elif estado == "JOGANDO" and jogadores and fase:
            jatual = jogadores[jogador_idx]
            desenhar_campo(surf, fase)
            for i, j in enumerate(jogadores):
                if not j.no_buraco:
                    j.desenhar(surf, ativo=(i == jogador_idx and j.parou()))
            if aiming and jatual.parou():
                desenhar_mira(surf, jatual, mouse_pos)
            desenhar_hud(surf, fonte_m, fonte_s, jogadores, jogador_idx, fase)

        elif estado == "FIM_HOLE" and fase and jogadores:
            ultimo = (fase_idx + 1 >= len(fases))
            desenhar_fim_hole(surf, fonte_g, fonte_m, fonte_s, jogadores, fase, ultimo)

        elif estado == "RANKING":
            desenhar_ranking_tela(surf, fonte_g, fonte_m, fonte_mono)

        elif estado == "REGRAS":
            surf.fill((20, 20, 20))
            txt = fonte_m.render("Tela de regras (placeholder)", True, COR_TEXTO)
            surf.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 300))
            esc = fonte_s.render("ESC — voltar ao menu", True, (150, 150, 150))
            surf.blit(esc, (LARGURA // 2 - esc.get_width() // 2, ALTURA - 45))

        tela.fill((0, 0, 0))
        scaled = pygame.transform.scale(surf, (w_sc, h_sc))
        tela.blit(scaled, (off_x, off_y))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
