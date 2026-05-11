import pygame
import sys

LARGURA, ALTURA = 1000, 700
FPS = 60

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption('Multi Mini Golf')
    clock = pygame.time.Clock()

    rodando = True
    while rodando:
        dt = clock.tick(FPS) / 1000.0 

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False

        tela.fill((45, 110, 55))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


