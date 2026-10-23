# MakeABridge/fondo.py
import math
import random
import pygame
from engine.background import ParallaxBackground
from . import estilo
from .settings import ANCHO, ALTO, SUELO_Y


def _capa_nubes(cantidad, escala, alpha, semilla):
    """Nubes suaves; no tocan los bordes para que el empalme del parallax no se note."""
    rnd = random.Random(semilla)
    alto = 200
    capa = pygame.Surface((ANCHO, alto), pygame.SRCALPHA)
    margen = int(80 * escala)
    for _ in range(cantidad):
        x = rnd.randint(margen, ANCHO - margen)
        y = rnd.randint(int(40 * escala), alto - int(40 * escala))
        for sombra, color in ((5, (222, 216, 205, alpha)), (0, (255, 255, 255, alpha))):
            for dx, dy, r in [(0, 0, 28), (30, 6, 22), (-30, 8, 20), (12, -14, 22)]:
                pygame.draw.circle(capa, color, (x + int(dx * escala), y + int(dy * escala) + sombra),
                                   int(r * escala))
    return capa


def _capa_colinas(color, borde, amplitud, ondas, alto=220):
    """Colinas tipo acuarela; con 'ondas' entero los extremos coinciden (empalme invisible)."""
    capa = pygame.Surface((ANCHO, alto), pygame.SRCALPHA)
    cima = []
    for x in range(0, ANCHO + 1, 10):
        cima.append((x, alto * 0.55 + amplitud * math.sin(2 * math.pi * ondas * x / ANCHO)))
    pygame.draw.polygon(capa, color, [(0, alto)] + cima + [(ANCHO, alto)])
    pygame.draw.lines(capa, borde, False, cima, 2)
    return capa


class Fondo:
    """Papel + acuarela + parallax + grano. Misma interfaz que ParallaxBackground (update/draw)."""

    def __init__(self):
        self.base = estilo.papel(ANCHO, ALTO, SUELO_Y)
        self.grano = estilo.grano_y_vineta(ANCHO, ALTO)
        self.parallax = ParallaxBackground()
        self.parallax.add_layer(_capa_nubes(4, 1.0, 170, 1), speed=0.15, y=10)
        self.parallax.add_layer(_capa_colinas((150, 178, 138, 215), (96, 124, 90, 255), 24, 2),
                                speed=0.10, y=SUELO_Y - 205)
        self.parallax.add_layer(_capa_nubes(3, 1.5, 215, 2), speed=0.40, y=60)
        self.parallax.add_layer(_capa_colinas((112, 156, 100, 235), (66, 104, 62, 255), 17, 3),
                                speed=0.25, y=SUELO_Y - 150)

    def update(self, dx):
        self.parallax.update(dx)

    def draw(self, surface):
        surface.blit(self.base, (0, 0))
        self.parallax.draw(surface)
        surface.blit(self.grano, (0, 0))


def crear_fondo():
    return Fondo()
