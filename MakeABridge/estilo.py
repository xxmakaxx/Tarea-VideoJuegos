# fisicas2d/estilo.py
# Estilo visual "cuaderno ilustrado" (inspirado en Crayon Physics / World of Goo),
# generado por código: no necesita imágenes externas.
import math
import os
import random
import pygame
from .settings import ASSETS_DIR

PAPEL = (241, 230, 205)
TINTA = (55, 38, 24)


_FUENTES = {}


def fuente_arcade(tam):
    """Fuente estilo arcade (Press Start 2P, licencia OFL, en assets/fonts). Si falta, usa una monoespaciada."""
    if tam not in _FUENTES:
        ruta = os.path.join(ASSETS_DIR, "fonts", "PressStart2P-Regular.ttf")
        if os.path.exists(ruta):
            _FUENTES[tam] = pygame.font.Font(ruta, tam)
        else:
            _FUENTES[tam] = pygame.font.SysFont("consolas,couriernew,lucidaconsole,monospace", int(tam * 1.4), bold=True)
    return _FUENTES[tam]


def textura_suelo(ancho, alto, hierba=14):
    """Tierra con piedritas y una franja de pasto. La imagen sobresale 'hierba' px por arriba del suelo."""
    rnd = random.Random(11)
    s = pygame.Surface((ancho, alto + hierba), pygame.SRCALPHA)
    s.fill((112, 82, 52), (0, hierba, ancho, alto))
    for _ in range(ancho * alto // 40):
        x, y = rnd.randrange(ancho), rnd.randrange(hierba, alto + hierba)
        c = rnd.choice(((92, 66, 40), (132, 100, 66), (104, 76, 48)))
        s.fill(c, (x, y, 2, 2))
    pygame.draw.rect(s, (74, 140, 70), (0, hierba - 2, ancho, 8))
    for x in range(0, ancho, 5):
        h = rnd.randint(5, hierba)
        c = (rnd.randint(60, 96), rnd.randint(130, 170), rnd.randint(55, 85))
        pygame.draw.polygon(s, c, [(x, hierba), (x + 2 + rnd.randint(-2, 2), hierba - h), (x + 5, hierba)])
    pygame.draw.line(s, (50, 96, 50), (0, hierba + 6), (ancho, hierba + 6), 2)
    return s


# ---------------------------------------------------------------- fondo
def papel(ancho, alto, suelo_y):
    """Papel con un lavado de acuarela celeste arriba."""
    s = pygame.Surface((ancho, alto))
    s.fill(PAPEL)
    lav = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for y in range(alto):
        a = int(125 * max(0.0, 1 - y / (suelo_y * 0.8)))
        pygame.draw.line(lav, (146, 194, 226, a), (0, y), (ancho, y))
    s.blit(lav, (0, 0))
    return s


def grano_y_vineta(ancho, alto):
    """Capa transparente con grano de papel, fibras y bordes oscurecidos."""
    rnd = random.Random(3)
    ov = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for _ in range(7000):
        x, y = rnd.randrange(ancho), rnd.randrange(alto)
        if rnd.random() < 0.6:
            c = (120, 95, 60, rnd.randint(10, 28))
        else:
            c = (255, 255, 255, rnd.randint(14, 34))
        ov.fill(c, (x, y, rnd.choice((1, 2)), 1))
    for _ in range(220):
        x, y, l = rnd.randrange(ancho), rnd.randrange(alto), rnd.randint(6, 18)
        a = rnd.uniform(0, math.pi)
        pygame.draw.line(ov, (140, 110, 70, 16), (x, y), (x + l * math.cos(a), y + l * math.sin(a)), 1)
    pq = pygame.Surface((50, 30), pygame.SRCALPHA)
    for j in range(30):
        for i in range(50):
            d = math.hypot((i - 24.5) / 25, (j - 14.5) / 15)
            pq.set_at((i, j), (60, 40, 20, min(70, int(max(0.0, d - 0.7) * 110))))
    ov.blit(pygame.transform.smoothscale(pq, (ancho, alto)), (0, 0))
    return ov


def textura_meta():
    """Bandera de meta."""
    s = pygame.Surface((50, 80), pygame.SRCALPHA)
    pygame.draw.line(s, TINTA, (12, 78), (12, 4), 4)
    pygame.draw.line(s, (120, 82, 46), (12, 78), (12, 4), 2)
    bandera = [(14, 6), (46, 18), (14, 32)]
    pygame.draw.polygon(s, (214, 70, 60), bandera)
    pygame.draw.lines(s, TINTA, True, bandera, 2)
    return s


def frames_muneco(n=8):
    """Ciclo de marcha de un muñeco (24x44). El último frame del ciclo vuelve al primero."""
    frames = []
    for i in range(n):
        fase = 2 * math.pi * i / n
        s = pygame.Surface((24, 44), pygame.SRCALPHA)
        cadera = (12, 27)
        pierna = 15
        for signo, color in ((1, (70, 50, 40)), (-1, (40, 30, 26))):
            ang = math.sin(fase) * 0.65 * signo
            pie = (cadera[0] + math.sin(ang) * pierna, cadera[1] + math.cos(ang) * pierna)
            pygame.draw.line(s, color, cadera, pie, 4)
        pygame.draw.line(s, (220, 92, 62), (12, 13), cadera, 6)             # torso
        for signo in (1, -1):
            ang = -math.sin(fase) * 0.6 * signo
            mano = (12 + math.sin(ang) * 11, 15 + math.cos(ang) * 11)
            pygame.draw.line(s, (232, 190, 150), (12, 15), mano, 3)         # brazos
        pygame.draw.circle(s, TINTA, (12, 7), 8)                            # cabeza
        pygame.draw.circle(s, (238, 200, 160), (12, 7), 6)
        pygame.draw.circle(s, TINTA, (14, 6), 1)
        frames.append(s)
    return frames


def frames_gato(n=8):
    """Ciclo de marcha de un gato naranja (44x30) mirando a la derecha. Las patas terminan en y=24."""
    NARANJA, OSCURO, CLARO = (232, 150, 68), (176, 98, 40), (250, 214, 160)
    frames = []
    for i in range(n):
        fase = 2 * math.pi * i / n
        s = pygame.Surface((44, 30), pygame.SRCALPHA)
        # cola (detrás del cuerpo, se mueve un poco)
        balanceo = math.sin(fase) * 2
        pygame.draw.lines(s, TINTA, False, [(8, 12), (3, 9 + balanceo), (3, 3 + balanceo)], 5)
        pygame.draw.lines(s, NARANJA, False, [(8, 12), (3, 9 + balanceo), (3, 3 + balanceo)], 3)
        # patas: dos pares que se alternan
        for x, signo, color in ((11, 1, OSCURO), (28, -1, OSCURO), (16, -1, NARANJA), (33, 1, NARANJA)):
            ang = math.sin(fase) * 0.7 * signo
            pie = (x + math.sin(ang) * 8, 16 + math.cos(ang) * 8)
            pygame.draw.line(s, TINTA, (x, 16), pie, 5)
            pygame.draw.line(s, color, (x, 16), pie, 3)
        # cuerpo con rayas
        pygame.draw.ellipse(s, TINTA, (4, 4, 32, 16))
        pygame.draw.ellipse(s, NARANJA, (5, 5, 30, 14))
        for rx in (13, 19, 25):
            pygame.draw.line(s, OSCURO, (rx, 6), (rx - 2, 11), 2)
        # cabeza y orejas
        pygame.draw.polygon(s, TINTA, [(30, 7), (31, -1), (37, 5)])
        pygame.draw.polygon(s, TINTA, [(36, 5), (42, -1), (43, 8)])
        pygame.draw.polygon(s, NARANJA, [(31, 6), (32, 1), (36, 5)])
        pygame.draw.polygon(s, NARANJA, [(37, 5), (41, 1), (42, 7)])
        pygame.draw.circle(s, TINTA, (36, 11), 8)
        pygame.draw.circle(s, NARANJA, (36, 11), 6)
        pygame.draw.circle(s, CLARO, (39, 13), 3)                   # hocico
        pygame.draw.circle(s, TINTA, (38, 9), 1)                    # ojo
        pygame.draw.circle(s, (230, 110, 120), (42, 12), 1)         # nariz
        for dy in (-1, 1):                                          # bigotes
            pygame.draw.line(s, TINTA, (41, 13), (44, 13 + dy * 2), 1)
        frames.append(s)
    return frames


def frames_caminante(n=8):
    """Devuelve los frames del personaje elegido en settings.PERSONAJE."""
    from .settings import PERSONAJE
    return frames_gato(n) if PERSONAJE == "gato" else frames_muneco(n)
