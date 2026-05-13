import pygame
import sys

LARGURA, ALTURA = 1000, 700
FPS = 60

COR_FUNDO = (45, 110, 55)
COR_TEXTO = (240, 240, 240)
COR_CAIXA = (30, 60, 35)
COR_BOTAO = (40, 80, 50)
COR_BOTAO_HOVER = (60,120,70)

def desenhar_menu(tela, fonte_g, fonte_m, nome, ativo_input, mouse_pos):
    tela.fill(COR_FUNDO)
    titulo = fonte_g.render("Buraco 6", True, COR_TEXTO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

    box = pygame.Rect(LARGURA // 2 - 200, 220, 400, 50)
    pygame.draw.rect(tela, COR_CAIXA, box, border_radius=8)
    pygame.draw.rect(tela, COR_TEXTO, box, 2, border_radius=8)

    cursor = '_' if (pygame.time.get_ticks() // 500) % 2 == 0 and ativo_input else ''
    txt = fonte_m.render(nome + cursor, True, COR_TEXTO)
    tela.blit(txt, (box.x +10, box.y +12))
    label = fonte_m.render('Digite seu nome:', True, COR_TEXTO)
    tela.blit(label, (box.x, box.y - 30))

    botao_iniciar = pygame.Rect( LARGURA // 2 -150, 320, 300, 50)
    botao_regras = pygame.Rect(LARGURA // 2 -150, 390, 300, 50)

    for botao, texto in [(botao_iniciar, 'Iniciar'), (botao_regras, 'Como Jogar')]:
        cor = COR_BOTAO_HOVER if botao.collidepoint(mouse_pos) else COR_BOTAO
        pygame.draw.rect(tela, cor,botao, border_radius=8)
        pygame.draw.rect(tela, COR_TEXTO, botao, 2, border_radius=8)
        t = fonte_m.render(texto, True, COR_TEXTO)
        tela.blit(t, (botao.centerx - t.get_width() // 2,
                      botao.centery - t.get_height() // 2))
        
    return box, botao_iniciar, botao_regras

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption('Multi Mini Golf')
    clock = pygame.time.Clock()

    fonte_g = pygame.font.SysFont('Arial', 48, bold = True)
    fonte_m = pygame.font.SysFont('Arial', 24)

    estado = 'MENU'
    nome = ''
    input_ativo = True

    rodando = True
    while rodando:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(FPS) / 1000.0 

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False

            if estado == 'MENU':
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    box, botao_iniciar, botao_regras = desenhar_menu(
                        tela, fonte_g, fonte_m, nome, input_ativo, mouse_pos
                    )

                    if box.collidepoint(ev.pos):
                        input_ativo = True
                    else:
                        input_ativo = False
                    
                    if botao_iniciar.collidepoint(ev.pos) and nome.strip():
                        print('Iniciar jogo com:', nome)
                        estado = 'JOGANDO'
                    if botao_regras.collidepoint(ev.pos):
                        print('Abrir tela de regras')
                        estado = 'REGRAS'
                    
                if ev.type == pygame.KEYDOWN and input_ativo:
                    if ev.key == pygame.K_BACKSPACE:
                        nome = nome[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if nome.strip():
                            estado = 'JOGANDO'
                    elif ev.unicode.isprintable() and len(nome) < 12:
                        nome += ev.unicode
                    
        if estado == "MENU":
            desenhar_menu(tela, fonte_g, fonte_m, nome, input_ativo, mouse_pos)

        elif estado == "JOGANDO":
            tela.fill((0, 0, 0))
            txt = fonte_m.render("Jogo ainda não implementado", True, COR_TEXTO)
            tela.blit(txt, (300, 300))

        elif estado == "REGRAS":
            tela.fill((20, 20, 20))
            txt = fonte_m.render("Tela de regras (placeholder)", True, COR_TEXTO)
            tela.blit(txt, (300, 300))
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


import math

LARGURA, ALTURA = 1000, 700
FPS = 60

COR_FUNDO = (45, 110, 55)
COR_TEXTO = (240, 240, 240)
COR_CAIXA = (30, 60, 35)
COR_BOTAO = (40, 80, 50)
COR_BOTAO_HOVER = (60, 120, 70)

COR_GRAMA_CLARA = (60, 135, 70)
COR_BOLA = (255, 95, 95)
COR_BOLA_SOMBRA = (20, 60, 30)
COR_HOLE = (15, 15, 15)
COR_TEE = (240, 240, 240)

RAIO_BOLA = 8
RAIO_BURACO = 14

ATRITO = 0.985
VEL_MIN = 0.18
POTENCIA_MAX_DRAG = 200
POTENCIA_FATOR = 0.13


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

    def reset(self, tee):
        self.x = float(tee[0])
        self.y = float(tee[1])
        self.vx = 0.0
        self.vy = 0.0
        self.tacadas = 0
        self.pos_inicio_tacada = (self.x, self.y)

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


def desenhar_campo(tela, tee, hole):
    tela.fill(COR_FUNDO)

    # gramado simples em faixas
    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    # tee
    pygame.draw.circle(tela, COR_TEE, tee, 14, 1)

    # buraco
    bx, by = hole
    pygame.draw.circle(tela, COR_HOLE, (bx, by), RAIO_BURACO)
    pygame.draw.line(tela, (60, 40, 30), (bx, by - 3), (bx, by - 38), 2)
    pygame.draw.polygon(tela, (220, 50, 50),
                        [(bx, by - 38), (bx + 16, by - 33), (bx, by - 26)])


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


def atualizar_bola(j):
    j.x += j.vx
    j.y += j.vy
    j.vx *= ATRITO
    j.vy *= ATRITO

    if abs(j.vx) < VEL_MIN:
        j.vx = 0.0
    if abs(j.vy) < VEL_MIN:
        j.vy = 0.0


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

                    input_ativo = botao_iniciar is None or pygame.Rect(
                        LARGURA // 2 - 200, 220, 400, 50
                    ).collidepoint(ev.pos)

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

        # Update
        if estado == "JOGANDO" and jogador:
            if not jogador.parou():
                atualizar_bola(jogador)

        # Render
        if estado == "MENU":
            botao_iniciar, botao_regras = None, None
            box, botao_iniciar, botao_regras = desenhar_menu(
                tela, fonte_g, fonte_m, nome, input_ativo, mouse_pos
            )

        elif estado == "JOGANDO":
            desenhar_campo(tela, tee, hole)

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

