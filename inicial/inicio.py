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
    tela.blit(titulo, (LARGURA // 2 - titulo.getwidth() // 2, 80))

    box = pygame.Rect(LARGURA // 2 - 200, 220, 400, 50)
    pygame.draw.rect(tela, COR_CAIXA, box, border_radius=8)
    pygame.draw.rect(tela, COR_TEXTO, box, 2, border_radius=8)

    cursor = '_' if (pygame.time.get_ticks() // 500) % 2 == 0 and ativo_input else ''
    txt = fonte_m.render(nome + cursor, True, COR_TEXTO)
    tela.blit(text, (box.x +10, box.y +12))
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
                    
                if ev.typer == pygame.KEYDOWN and input_ativo:
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


