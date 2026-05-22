import pygame
import math
import sys
from config import (
    LARGURA, ALTURA, FPS,
    COR_FUNDO, COR_TEXTO, COR_CAIXA,
    COR_BOTAO, COR_BOTAO_HOVER,
    COR_BOLA, POTENCIA_MAX_DRAG,
    POTENCIA_FATOR,
    COR_TUNEL_1,
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

class Fase:
    def __init__(
        self,
        numero,
        par,
        tee,
        buraco_pos,
        paredes=None,
        areias=None,
        aguas=None,
        tuneis=None,
        esteiras=None,
    ):
        self.numero = numero
        self.par = par
        self.tee = tee
        self.buraco_pos = buraco_pos
        self.paredes = paredes or []
        self.areias = areias or []
        self.aguas = aguas or []
        self.tuneis = tuneis or []
        self.esteiras = esteiras or []
    
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
    botao_regras = pygame.Rect(LARGURA // 2 - 150, 390, 300, 50)
    for botao, texto in [
        (botao_iniciar, "Iniciar"),
        (botao_regras, "Como Jogar")
    ]:
        cor = COR_BOTAO_HOVER if botao.collidepoint(mouse_pos) else COR_BOTAO
        pygame.draw.rect(tela, cor, botao, border_radius=8)
        pygame.draw.rect(tela, COR_TEXTO, botao, 2, border_radius=8)
        t = fonte_m.render(texto, True, COR_TEXTO)
        tela.blit(
            t,
            (
                botao.centerx - t.get_width() // 2,
                botao.centery - t.get_height() // 2
            )
        )
    return box, botao_iniciar, botao_regras

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Mini Golf Multiplayer")
    clock = pygame.time.Clock()
    fonte_g = pygame.font.SysFont("Arial", 48, bold=True)
    fonte_m = pygame.font.SysFont("Arial", 24)
    estado = "MENU"
    nome = ""
    input_ativo = True
    fase = Fase(
        numero=1,
        par=4,
        tee=(130, 350),
        buraco_pos=(870, 350),
        paredes=[
            Parede(480, 200, 30, 300),
        ],
        areias=[
            Areia(380, 500, 220, 110),
        ],
        aguas=[
            Agua(110, 120, 140, 90),
        ],
        tuneis=[
            Tunel((300, 350), (700, 350), COR_TUNEL_1),
        ],
        esteiras=[
            Esteira(280, 340, 90, 40, 1, 0, 0.25),
        ],
    )
    jogador = None
    aiming = False
    botao_iniciar = None
    botao_regras = None
    rodando = True
    while rodando:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(FPS) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            if estado == "MENU":
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if botao_iniciar and botao_iniciar.collidepoint(ev.pos) and nome.strip():
                        jogador = Jogador(nome.strip(), COR_BOLA)
                        jogador.reset(fase.tee)
                        estado = "JOGANDO"
                    elif botao_regras and botao_regras.collidepoint(ev.pos):
                        estado = "REGRAS"
                    box_atual = pygame.Rect(
                        LARGURA // 2 - 200,
                        220,
                        400,
                        50
                    )
                    input_ativo = box_atual.collidepoint(ev.pos)
                if ev.type == pygame.KEYDOWN and input_ativo:
                    if ev.key == pygame.K_BACKSPACE:
                        nome = nome[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if nome.strip():
                            jogador = Jogador(nome.strip(), COR_BOLA)
                            jogador.reset(fase.tee)
                            estado = "JOGANDO"
                    elif ev.unicode.isprintable() and len(nome) < 12:
                        nome += ev.unicode
            elif estado == "JOGANDO":
                if jogador and jogador.parou() and not jogador.no_buraco:
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if math.hypot(
                            ev.pos[0] - jogador.x,
                            ev.pos[1] - jogador.y
                        ) < 50:
                            aiming = True
                    elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and aiming:
                        mx, my = ev.pos
                        dx = jogador.x - mx
                        dy = jogador.y - my
                        dist = math.hypot(dx, dy)
                        if dist > 8:
                            dist_cap = min(dist, POTENCIA_MAX_DRAG)
                            dx_n = dx / dist
                            dy_n = dy / dist
                            jogador.pos_inicio_tacada = (
                                jogador.x,
                                jogador.y
                            )
                            jogador.vx = dx_n * dist_cap * POTENCIA_FATOR
                            jogador.vy = dy_n * dist_cap * POTENCIA_FATOR
                            jogador.tacadas += 1
                        aiming = False
            elif estado == "FIM_HOLE":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    nome_atual = jogador.nome
                    jogador = Jogador(nome_atual, COR_BOLA)
                    jogador.reset(fase.tee)
                    estado = "JOGANDO"
            elif estado == "REGRAS":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    estado = "MENU"
        if estado == "JOGANDO" and jogador:
            for pm in fase.paredes_moveis:
                pm.update(dt) #pm update
            if not jogador.parou() and not jogador.no_buraco:
                atualizar_bola(jogador, fase)
                if jogador.no_buraco:
                    estado = "FIM_HOLE"
        if estado == "MENU":
            botao_iniciar, botao_regras = None, None
            _, botao_iniciar, botao_regras = desenhar_menu(
                tela,
                fonte_g,
                fonte_m,
                nome,
                input_ativo,
                mouse_pos
            )
        elif estado == "JOGANDO":
            desenhar_campo(tela, fase)
            if jogador:
                jogador.desenhar(
                    tela,
                    ativo=jogador.parou() and not jogador.no_buraco
                )
                if aiming and jogador.parou() and not jogador.no_buraco:
                    desenhar_mira(tela, jogador, mouse_pos)
                desenhar_hud(
                    tela,
                    fonte_m,
                    jogador,
                    fase
                )
        elif estado == "FIM_HOLE":
            desenhar_fim_hole(
                tela,
                fonte_g,
                fonte_m,
                jogador,
                fase
            )
        elif estado == "REGRAS":
            tela.fill((20, 20, 20))
            txt = fonte_m.render(
                "Tela de regras (placeholder)",
                True,
                COR_TEXTO
            )
            tela.blit(txt, (300, 300))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()