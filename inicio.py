import pygame
import sys
import math
from config import (
    LARGURA, ALTURA, FPS,
    COR_FUNDO, COR_TEXTO, COR_CAIXA, COR_BOTAO, COR_BOTAO_HOVER,
    COR_BOLA, POTENCIA_MAX_DRAG, POTENCIA_FATOR,
)
from paredes import Parede, Jogador, desenhar_campo, desenhar_mira, atualizar_bola
from buracos_fase import  desenhar , desenhar_menu , desenhar_campo , desenhar_mira , colidir_rect , checar_buraco , atualizar_bola , desenhar_hud , desenhar_fim_hole , main 

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

    for botao, texto in [(botao_iniciar, "Iniciar"), (botao_regras, "Como Jogar")]:
        cor = COR_BOTAO_HOVER if botao.collidepoint(mouse_pos) else COR_BOTAO
        pygame.draw.rect(tela, cor, botao, border_radius=8)
        pygame.draw.rect(tela, COR_TEXTO, botao, 2, border_radius=8)

        t = fonte_m.render(texto, True, COR_TEXTO)
        tela.blit(t, (botao.centerx - t.get_width() // 2,
                      botao.centery - t.get_height() // 2))

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

    tee = (130, 350)
    hole = (870, 350)
    paredes = [
        Parede(480, 200, 30, 300),
    ]

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
                        jogador.reset(tee)
                        estado = "JOGANDO"

                    elif botao_regras and botao_regras.collidepoint(ev.pos):
                        estado = "REGRAS"

                    box_atual = pygame.Rect(LARGURA // 2 - 200, 220, 400, 50)
                    input_ativo = box_atual.collidepoint(ev.pos)

                if ev.type == pygame.KEYDOWN and input_ativo:
                    if ev.key == pygame.K_BACKSPACE:
                        nome = nome[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if nome.strip():
                            jogador = Jogador(nome.strip(), COR_BOLA)
                            jogador.reset(tee)
                            estado = "JOGANDO"
                    elif ev.unicode.isprintable() and len(nome) < 12:
                        nome += ev.unicode

            elif estado == "JOGANDO":
                if jogador and jogador.parou():
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

        if estado == "JOGANDO" and jogador:
            if not jogador.parou():
                atualizar_bola(jogador, paredes, hole)

        if estado == "MENU":
            botao_iniciar, botao_regras = None, None
            _, botao_iniciar, botao_regras = desenhar_menu(
                tela, fonte_g, fonte_m, nome, input_ativo, mouse_pos
            )

        elif estado == "JOGANDO":
            desenhar_campo(tela, tee, hole, paredes)

            if jogador:
                jogador.desenhar(tela, ativo=jogador.parou())
                if aiming and jogador.parou():
                    desenhar_mira(tela, jogador, mouse_pos)

            hud = fonte_m.render(f"Jogadas: {jogador.tacadas}", True, COR_TEXTO)
            tela.blit(hud, (20, 20))

        elif estado == "REGRAS":
            tela.fill((20, 20, 20))
            txt = fonte_m.render("Tela de regras (placeholder)", True, COR_TEXTO)
            tela.blit(txt, (300, 300))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
