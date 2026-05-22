import pygame
import math

from config import (
    COR_PMOVEL,
    COR_PMOVEL_DARK,
    COR_PMOVEL_PATH,
)


class ParedeMovel:
    def _init_(
        self,
        x_a,
        y_a,
        w,
        h,
        x_b,
        y_b,
        velocidade=1.5,
        fase_inicial=0.0
    ):
        self.x_a = x_a
        self.y_a = y_a

        self.x_b = x_b
        self.y_b = y_b

        self.w = w
        self.h = h

        self.velocidade = velocidade
        self.fase = fase_inicial

        self.rect = pygame.Rect(x_a, y_a, w, h)

    def update(self, dt):
        self.fase += self.velocidade * dt

        t = (math.sin(self.fase) + 1) / 2

        self.rect.x = int(
            self.x_a + (self.x_b - self.x_a) * t
        )

        self.rect.y = int(
            self.y_a + (self.y_b - self.y_a) * t
        )

    def desenhar(self, tela):

        cx_a = self.x_a + self.w / 2
        cy_a = self.y_a + self.h / 2

        cx_b = self.x_b + self.w / 2
        cy_b = self.y_b + self.h / 2

        n = 14

        for i in range(0, n, 2):

            t1 = i / n
            t2 = (i + 1) / n

            pygame.draw.line(
                tela,
                COR_PMOVEL_PATH,

                (
                    cx_a + (cx_b - cx_a) * t1,
                    cy_a + (cy_b - cy_a) * t1
                ),

                (
                    cx_a + (cx_b - cx_a) * t2,
                    cy_a + (cy_b - cy_a) * t2
                ),

                1
            )

        for px, py in [
            (self.x_a, self.y_a),
            (self.x_b, self.y_b)
        ]:

            ghost = pygame.Rect(
                px,
                py,
                self.w,
                self.h
            )

            pygame.draw.rect(
                tela,
                COR_PMOVEL_PATH,
                ghost,
                1,
                border_radius=4
            )

        sombra = self.rect.move(3, 4)

        pygame.draw.rect(
            tela,
            (20, 20, 20),
            sombra,
            border_radius=4
        )

        pygame.draw.rect(
            tela,
            COR_PMOVEL,
            self.rect,
            border_radius=4
        )

        pygame.draw.rect(
            tela,
            COR_PMOVEL_DARK,
            self.rect,
            2,
            border_radius=4
        )

        for i in range(0, max(self.rect.w, self.rect.h), 10):

            if self.rect.w >= self.rect.h:

                x = self.rect.left + i

                if x < self.rect.right:

                    pygame.draw.line(
                        tela,
                        COR_PMOVEL_DARK,
                        (x, self.rect.top + 3),
                        (x, self.rect.bottom - 3),
                        1
                    )

            else:

                y = self.rect.top + i

                if y < self.rect.bottom:

                    pygame.draw.line(
                        tela,
                        COR_PMOVEL_DARK,
                        (self.rect.left + 3, y),
                        (self.rect.right - 3, y),
                        1
                    )