# MakeABridge/fondo.py
import math
import random
import pygame
from engine.background import ParallaxBackground
from . import estilo
from .estilo import PIXEL, ampliar
from .settings import ANCHO, ALTO, SUELO_Y

W = ANCHO // PIXEL          # ancho de las capas en pixeles de arte


def _capa_nubes(cantidad, escala, semilla, sombra=(196, 214, 238)):
    #Nubes blancas de bloques con sombra celeste abajo. No tocan los bordes (empalme del parallax).
    rnd = random.Random(semilla)
    alto = 100
    capa = pygame.Surface((W, alto), pygame.SRCALPHA)
    margen = int(40 * escala)
    for _ in range(cantidad):
        x = rnd.randint(margen, W - margen)
        y = rnd.randint(int(22 * escala), alto - int(24 * escala))
        circulos = [(0, 0, 9), (13, 3, 7), (-13, 4, 6), (5, -6, 7), (-5, 5, 7), (20, 5, 5)]
        for dy, color in ((2, sombra), (0, (255, 255, 255))):       # primero la sombra, luego el blanco
            for dx, ddy, r in circulos:
                pygame.draw.circle(capa, color, (x + int(dx * escala), y + int(ddy * escala) + dy), max(2, int(r * escala)))
        # base plana (las nubes de 8 bits tienen el fondo recto)
        capa.fill((0, 0, 0, 0), (x - int(30 * escala), y + int(12 * escala), int(60 * escala), 30))
    return ampliar(capa)


def _pino(capa, x, base, alto):
    oscuro, medio = (30, 92, 62), (46, 128, 74)
    capa.fill((92, 60, 40), (x, base - 2, 1, 3))
    for k in range(3):
        ancho = 2 + k * 2
        y = base - 3 - (2 - k) * (alto // 3) - alto // 3 + 1
        for fila in range(alto // 3 + 1):
            a = 1 + (fila * ancho) // (alto // 3 + 1)
            capa.fill(oscuro, (x - a, y + fila, 2 * a + 1, 1))
            capa.set_at((x - a, y + fila), medio)


def _capa_relieve(color, claro, borde, amplitud, ondas, base, pinos=0, semilla=1, alto=120, fase=0.0):
    rnd = random.Random(semilla)
    capa = pygame.Surface((W, alto), pygame.SRCALPHA)
    cimas = []
    for x in range(W):
        y = int(base + amplitud * math.sin(2 * math.pi * ondas * x / W + fase)
                + amplitud * 0.35 * math.sin(2 * math.pi * ondas * 2.3 * x / W + fase * 2))
        cimas.append(y)
        capa.fill(color, (x, y, 1, alto - y))
        capa.set_at((x, y), borde)
        if y + 1 < alto:
            capa.set_at((x, y + 1), claro)
        # sombreado en tramado debajo de la cima
        for k in range(3, 9):
            if y + k < alto and (x + k) % 2 == 0 and k % 3 != 0:
                capa.set_at((x, y + k), borde if k > 6 else claro)
    for _ in range(pinos):
        x = rnd.randint(8, W - 8)
        _pino(capa, x, cimas[x] + 3, rnd.choice((9, 12, 15)))
    return ampliar(capa)


class Fondo:

    def __init__(self, scanlines=False):
        self.base = estilo.papel(ANCHO, ALTO, SUELO_Y)
        self.scan = estilo.grano_y_vineta(ANCHO, ALTO) if scanlines else None
        self.parallax = ParallaxBackground()
        self.parallax.add_layer(_capa_nubes(4, 0.9, 1), speed=0.15, y=10)
        self.parallax.add_layer(_capa_relieve((126, 150, 206), (150, 174, 224), (96, 120, 180), 16, 2, 40,
                                              semilla=2, alto=120), speed=0.10, y=SUELO_Y - 205)
        self.parallax.add_layer(_capa_nubes(3, 1.4, 2, sombra=(204, 220, 240)), speed=0.40, y=50)
        self.parallax.add_layer(_capa_relieve((74, 150, 90), (104, 182, 100), (44, 104, 70), 11, 3, 40,
                                              pinos=22, semilla=5, alto=120, fase=1.0),
                                speed=0.25, y=SUELO_Y - 150)

    def update(self, dx):
        self.parallax.update(dx)

    def draw(self, surface):
        surface.blit(self.base, (0, 0))
        self.parallax.draw(surface)
        if self.scan is not None:
            surface.blit(self.scan, (0, 0))


def crear_fondo():
    return Fondo()
