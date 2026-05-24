import pygame
import sys
import math
from paredes_moveis import ParedeMovel
from config import (
    LARGURA, ALTURA, FPS,
    COR_FUNDO, COR_TEXTO, COR_CAIXA,
    COR_BOTAO, COR_BOTAO_HOVER,
    COR_BOLA, POTENCIA_MAX_DRAG, POTENCIA_FATOR,
    COR_TUNEL_1, COR_TUNEL_2, COR_TUNEL_3,
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
            # água bloqueia o caminho direto pelo centro inferior
            aguas=[Agua(600, 480, 130, 120)],
            # saída dentro do ⊓ — obriga a sair do corredor e cruzar o campo
            tuneis=[Tunel((250, 620), (310, 330), COR_TUNEL_1)],
            # força aumentada: bola tende a ultrapassar o buraco
            esteiras=[Esteira(775, 310, 50, 250, 0, -1, 0.52)],
            # parede oscila na saída do canal, exige timing
            paredes_moveis=[ParedeMovel(755, 295, 175, 25, 755, 440, velocidade=1.0)],
        ),

        Fase(
            numero=3, par=4, tee=(130, 350), buraco_pos=(870, 350),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(450, 80, 30, 130), Parede(450, 490, 30, 140),
            ],
            aguas=[Agua(380, 230, 240, 240)],
            tuneis=[Tunel((280, 350), (720, 350), COR_TUNEL_2)],
            paredes_moveis=[ParedeMovel(370, 110, 30, 100, 370, 480, velocidade=1.2)],
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
            areias=[Areia(700, 60, 80, 130)],
            aguas=[Agua(110, 540, 110, 110)],
            tuneis=[Tunel((340, 200), (820, 480), COR_TUNEL_3)],
            esteiras=[Esteira(280, 340, 90, 40, 1, 0, 0.25)],
        ),

        Fase(
            numero=5, par=4, tee=(130, 350), buraco_pos=(870, 600),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(485, 30, 30, 640), Parede(515, 380, 470, 30),
            ],
            tuneis=[
                Tunel((250, 200), (700, 180), COR_TUNEL_1),
                Tunel((900, 250), (700, 540), COR_TUNEL_2),
            ],
            esteiras=[Esteira(560, 200, 280, 50, -1, 0, 0.25)],
        ),

        Fase(
            numero=6, par=5, tee=(130, 350), buraco_pos=(900, 350),
            paredes=[
                Parede(0, 0, 1000, 30), Parede(0, 670, 1000, 30),
                Parede(0, 0, 30, 700), Parede(970, 0, 30, 700),
                Parede(60, 230, 700, 30), Parede(60, 440, 700, 30),
            ],
            esteiras=[
                Esteira(150, 90, 600, 130, 1, 0, 0.28),
                Esteira(150, 480, 600, 130, -1, 0, 0.22),
            ],
            paredes_moveis=[
                ParedeMovel(250, 290, 30, 130, 450, 290, velocidade=1.4, fase_inicial=0.0),
                ParedeMovel(550, 290, 30, 130, 700, 290, velocidade=1.6, fase_inicial=1.5),
            ],
        ),
    ]


def desenhar_menu(tela, fonte_g, fonte_m, nome, ativo_input, mouse_pos):
    tela.fill(COR_FUNDO)
    titulo = fonte_g.render("MINI GOLF", True, COR_TEXTO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

    box = pygame.Rect(LARGURA // 2 - 200, 220, 400, 50)
    pygame.draw.rect(tela, COR_CAIXA, box, border_radius=8)
    pygame.draw.rect(tela, COR_TEXTO, box, 2, border_radius=8)
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 and ativo_input else ""
    txt = fonte_m.render(nome + cursor, True, COR_TEXTO)
    tela.blit(txt, (box.x + 10, box.y + 12))
    label = fonte_m.render("Digite seu nome:", True, COR_TEXTO)
    tela.blit(label, (box.x, box.y - 30))

    botao_iniciar = pygame.Rect(LARGURA // 2 - 150, 320, 300, 50)
    botao_regras  = pygame.Rect(LARGURA // 2 - 150, 390, 300, 50)
    botao_ranking = pygame.Rect(LARGURA // 2 - 150, 460, 300, 50)

    for botao, texto in [
        (botao_iniciar, "Iniciar"),
        (botao_regras,  "Como Jogar"),
        (botao_ranking, "Ranking"),
    ]:
        cor = COR_BOTAO_HOVER if botao.collidepoint(mouse_pos) else COR_BOTAO
        pygame.draw.rect(tela, cor, botao, border_radius=8)
        pygame.draw.rect(tela, COR_TEXTO, botao, 2, border_radius=8)
        t = fonte_m.render(texto, True, COR_TEXTO)
        tela.blit(t, (botao.centerx - t.get_width() // 2, botao.centery - t.get_height() // 2))

    return box, botao_iniciar, botao_regras, botao_ranking


def desenhar_ranking_tela(tela, fonte_g, fonte_m, fonte_mono):
    data = carregar_ranking()
    tela.fill((15, 35, 20))

    titulo = fonte_g.render("RANKING", True, COR_TEXTO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 30))

    cab = fonte_mono.render(
        f"{'#':<4}{'Nome':<16}{'Tacadas':<10}{'Fases':<8}{'Media':<8}Data",
        True, (160, 200, 160),
    )
    tela.blit(cab, (60, 105))
    pygame.draw.line(tela, (70, 120, 80), (60, 128), (LARGURA - 60, 128), 1)

    cores_pos = {0: (220, 200, 60), 1: (190, 190, 190), 2: (210, 140, 70)}
    for i, e in enumerate(data.get("all_time", [])[:15]):
        cor = cores_pos.get(i, COR_TEXTO)
        linha = fonte_mono.render(
            f"{i + 1:<4}{e['nome'][:14]:<16}{e['total_tacadas']:<10}{e['fases']:<8}{e['media']:<8}{e['data']}",
            True, cor,
        )
        tela.blit(linha, (60, 140 + i * 30))

    esc = fonte_m.render("ESC — voltar ao menu", True, (130, 170, 130))
    tela.blit(esc, (LARGURA // 2 - esc.get_width() // 2, ALTURA - 45))


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Mini Golf")
    clock = pygame.time.Clock()

    fonte_g    = pygame.font.SysFont("Arial", 48, bold=True)
    fonte_m    = pygame.font.SysFont("Arial", 24)
    fonte_mono = pygame.font.SysFont("Courier New", 18)

    estado      = "MENU"
    nome        = ""
    input_ativo = True
    fases       = criar_fases()
    fase_idx    = 0
    fase        = fases[fase_idx]
    jogador     = None
    aiming      = False

    botao_iniciar = botao_regras = botao_ranking = None

    rodando = True
    while rodando:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(FPS) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False

            # ── MENU ──────────────────────────────────────────────
            if estado == "MENU":
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    box_atual = pygame.Rect(LARGURA // 2 - 200, 220, 400, 50)
                    input_ativo = box_atual.collidepoint(ev.pos)

                    if botao_iniciar and botao_iniciar.collidepoint(ev.pos) and nome.strip():
                        fases = criar_fases()
                        fase_idx = 0
                        fase = fases[fase_idx]
                        jogador = Jogador(nome.strip(), COR_BOLA)
                        jogador.reset(fase.tee)
                        estado = "JOGANDO"

                    elif botao_regras and botao_regras.collidepoint(ev.pos):
                        estado = "REGRAS"

                    elif botao_ranking and botao_ranking.collidepoint(ev.pos):
                        estado = "RANKING"

                if ev.type == pygame.KEYDOWN and input_ativo:
                    if ev.key == pygame.K_BACKSPACE:
                        nome = nome[:-1]
                    elif ev.key == pygame.K_RETURN and nome.strip():
                        fases = criar_fases()
                        fase_idx = 0
                        fase = fases[fase_idx]
                        jogador = Jogador(nome.strip(), COR_BOLA)
                        jogador.reset(fase.tee)
                        estado = "JOGANDO"
                    elif ev.unicode.isprintable() and len(nome) < 12:
                        nome += ev.unicode

            # ── JOGANDO ───────────────────────────────────────────
            elif estado == "JOGANDO":
                if jogador and jogador.parou() and not jogador.no_buraco:
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if math.hypot(ev.pos[0] - jogador.x, ev.pos[1] - jogador.y) < 50:
                            aiming = True
                    elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and aiming:
                        mx, my = ev.pos
                        dx = jogador.x - mx
                        dy = jogador.y - my
                        dist = math.hypot(dx, dy)
                        if dist > 8:
                            dist_cap = min(dist, POTENCIA_MAX_DRAG)
                            dx_n, dy_n = dx / dist, dy / dist
                            jogador.pos_inicio_tacada = (jogador.x, jogador.y)
                            jogador.vx = dx_n * dist_cap * POTENCIA_FATOR
                            jogador.vy = dy_n * dist_cap * POTENCIA_FATOR
                            jogador.tacadas += 1
                        aiming = False

            # ── FIM DO BURACO ─────────────────────────────────────
            elif estado == "FIM_HOLE":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    fase_idx += 1
                    if fase_idx >= len(fases):
                        adicionar_ao_ranking([jogador], len(fases))
                        estado = "RANKING"
                    else:
                        jogador.tacadas_total += jogador.tacadas
                        fase = fases[fase_idx]
                        jogador.reset(fase.tee)
                        estado = "JOGANDO"

            # ── RANKING / REGRAS ──────────────────────────────────
            elif estado in ("RANKING", "REGRAS"):
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    estado = "MENU"

        # ── FÍSICA + PAREDES MÓVEIS ───────────────────────────────
        if estado == "JOGANDO" and jogador and fase:
            for pm in fase.paredes_moveis:
                pm.update(dt)
            if not jogador.parou() and not jogador.no_buraco:
                atualizar_bola(jogador, fase)
                if jogador.no_buraco:
                    estado = "FIM_HOLE"

        # ── DESENHO ───────────────────────────────────────────────
        if estado == "MENU":
            _, botao_iniciar, botao_regras, botao_ranking = desenhar_menu(
                tela, fonte_g, fonte_m, nome, input_ativo, mouse_pos
            )

        elif estado == "JOGANDO" and fase:
            desenhar_campo(tela, fase)
            if jogador:
                jogador.desenhar(tela, ativo=jogador.parou() and not jogador.no_buraco)
                if aiming and jogador.parou() and not jogador.no_buraco:
                    desenhar_mira(tela, jogador, mouse_pos)
            desenhar_hud(tela, fonte_m, jogador, fase)

        elif estado == "FIM_HOLE" and fase:
            desenhar_fim_hole(tela, fonte_g, fonte_m, jogador, fase)

        elif estado == "RANKING":
            desenhar_ranking_tela(tela, fonte_g, fonte_m, fonte_mono)

        elif estado == "REGRAS":
            tela.fill((20, 20, 20))
            txt = fonte_m.render("Tela de regras (placeholder)", True, COR_TEXTO)
            tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 300))
            esc = fonte_m.render("ESC — voltar ao menu", True, (150, 150, 150))
            tela.blit(esc, (LARGURA // 2 - esc.get_width() // 2, ALTURA - 45))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
