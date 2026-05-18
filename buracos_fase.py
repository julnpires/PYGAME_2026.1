import pygame
import sys
import math
import random

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
COR_PAREDE = (95, 60, 35)
COR_PAREDE_DARK = (55, 33, 18)
COR_AREIA = (220, 200, 130)
COR_AREIA_DARK = (195, 175, 105)

RAIO_BOLA = 8
RAIO_BURACO = 14

ATRITO = 0.985
ATRITO_AREIA = 0.91
VEL_MIN = 0.18
POTENCIA_MAX_DRAG = 200
POTENCIA_FATOR = 0.13
COEF_RESTITUICAO = 0.82
VEL_MAX_AFUNDA = 9.0

class Parede:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def desenhar(self, tela):
        sombra = self.rect.move(3, 4)
        pygame.draw.rect(tela, COR_BOLA_SOMBRA, sombra, border_radius=4)
        pygame.draw.rect(tela, COR_PAREDE, self.rect, border_radius=4)
        pygame.draw.rect(tela, COR_PAREDE_DARK, self.rect, 2, border_radius=4)

class Zona:
    """Areia ou água. Neste commit usamos só areia."""
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
                pygame.draw.circle(
                    tela,
                    COR_AREIA_DARK,
                    (px, py),
                    1
                )

    def contem(self, x, y):
        return self.rect.collidepoint(x, y)
    
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


def desenhar_campo(tela, tee, buraco_pos, paredes, zonas):
    tela.fill(COR_FUNDO)
    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))
    pygame.draw.circle(tela, COR_TEE, tee, 14, 1)

    bx, by = buraco_pos
    pygame.draw.circle(tela, (10, 30, 15), (bx + 1, by + 2), RAIO_BURACO + 2)
    pygame.draw.circle(tela, COR_HOLE, (bx, by), RAIO_BURACO)
    pygame.draw.line(tela, (60, 40, 30), (bx, by - 3), (bx, by - 38), 2)
    pygame.draw.polygon(tela, (220, 50, 50),
                        [(bx, by - 38), (bx + 16, by - 33), (bx, by - 26)])
    for z in zonas:
        z.desenhar(tela)
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

def atualizar_bola(j, paredes, buraco_pos, zonas):
    em_areia = any(
    z.tipo == "areia" and z.contem(j.x, j.y)
    for z in zonas
    )
    atrito = ATRITO_AREIA if em_areia else ATRITO
    j.vx *= atrito
    j.vy *= atrito
    for p in paredes:
        colidir_rect(j, p.rect)

    if checar_buraco(j, buraco_pos):
        return

    j.vx *= ATRITO
    j.vy *= ATRITO

    if abs(j.vx) < VEL_MIN:
        j.vx = 0.0
    if abs(j.vy) < VEL_MIN:
        j.vy = 0.0


def desenhar_hud(tela, fonte_m, jogador):
    hud = fonte_m.render(f"Jogadas: {jogador.tacadas}", True, COR_TEXTO)
    tela.blit(hud, (20, 20))


def desenhar_fim_hole(tela, fonte_g, fonte_m, jogador):
    tela.fill(COR_FUNDO)

    for y in range(0, ALTURA, 30):
        if (y // 30) % 2 == 0:
            pygame.draw.rect(tela, COR_GRAMA_CLARA, (0, y, LARGURA, 15))

    titulo = fonte_g.render("Buraco concluido", True, COR_TEXTO)
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

    info = fonte_m.render(
        f"{jogador.nome} terminou em {jogador.tacadas} tacadas.",
        True,
        COR_TEXTO
    )
    tela.blit(info, (LARGURA // 2 - info.get_width() // 2, 160))

    instr = fonte_m.render("Pressione SPACE para jogar de novo", True, COR_TEXTO)
    tela.blit(instr, (LARGURA // 2 - instr.get_width() // 2, 230))

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
    buraco_pos = (870, 350)
    paredes = [
        Parede(480, 200, 30, 300),
    ]
    zonas = [
        Zona(380, 500, 220, 110, "areia"),
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

            elif estado == "FIM_HOLE":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    nome_atual = jogador.nome
                    jogador = Jogador(nome_atual, COR_BOLA)
                    jogador.reset(tee)
                    estado = "JOGANDO"

            elif estado == "REGRAS":
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    estado = "MENU"

        if estado == "JOGANDO" and jogador:
            if not jogador.parou() and not jogador.no_buraco:
                atualizar_bola(jogador, paredes, buraco_pos, zonas)
                if jogador.no_buraco:
                    estado = "FIM_HOLE"

        if estado == "MENU":
            botao_iniciar, botao_regras = None, None
            _, botao_iniciar, botao_regras = desenhar_menu(
                tela, fonte_g, fonte_m, nome, input_ativo, mouse_pos
            )

        elif estado == "JOGANDO":
            desenhar_campo(tela, tee, buraco_pos, paredes)

            if jogador:
                jogador.desenhar(tela, ativo=jogador.parou() and not jogador.no_buraco)
                if aiming and jogador.parou() and not jogador.no_buraco:
                    desenhar_mira(tela, jogador, mouse_pos)

                desenhar_hud(tela, fonte_m, jogador)

        elif estado == "FIM_HOLE":
            desenhar_fim_hole(tela, fonte_g, fonte_m, jogador)

        elif estado == "REGRAS":
            tela.fill((20, 20, 20))
            txt = fonte_m.render("Tela de regras (placeholder)", True, COR_TEXTO)
            tela.blit(txt, (300, 300))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
