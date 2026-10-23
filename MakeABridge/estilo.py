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


def fuente_manuscrita(tam):
    """Intenta fuentes de tipo manuscrito; si no existen usa la de Pygame."""
    return pygame.font.SysFont("segoeprint,bradleyhandITC,comicsansms,georgia", tam)


def _jit(rnd, a=1.2):
    return rnd.uniform(-a, a)


# ---------------------------------------------------------------- contornos
def _contorno_rect(s, rnd, color=TINTA, pasadas=2, grosor=2):
    w, h = s.get_size()
    for _ in range(pasadas):
        pts = [(1 + _jit(rnd), 1 + _jit(rnd)), (w - 2 + _jit(rnd), 1 + _jit(rnd)),
               (w - 2 + _jit(rnd), h - 2 + _jit(rnd)), (1 + _jit(rnd), h - 2 + _jit(rnd))]
        pygame.draw.lines(s, color, True, pts, grosor)


def _contorno_circulo(s, rnd, color=TINTA, pasadas=2, grosor=2):
    w, h = s.get_size()
    cx, cy, r = w / 2, h / 2, w / 2 - 2
    for _ in range(pasadas):
        pts = []
        for i in range(24):
            a = 2 * math.pi * i / 24
            rr = r + _jit(rnd, 1.0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        pygame.draw.lines(s, color, True, pts, grosor)


# ---------------------------------------------------------------- materiales
def _veta(s, rnd, n, color):
    w, h = s.get_size()
    horizontal = w >= h
    largo, ancho = (w, h) if horizontal else (h, w)
    for _ in range(n):
        p = rnd.uniform(3, ancho - 3)
        fase = rnd.uniform(0, 6.28)
        amp = rnd.uniform(0.6, 1.8)
        pts = []
        for t in range(0, largo + 1, 5):
            lat = p + amp * math.sin(t / 9 + fase)
            pts.append((t, lat) if horizontal else (lat, t))
        pygame.draw.lines(s, color, False, pts, 1)


def textura_bloque(ancho, alto, material):
    rnd = random.Random()
    ancho, alto = int(ancho), int(alto)
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)

    if material == "madera":
        s.fill((181, 126, 72))
        _veta(s, rnd, max(3, min(ancho, alto) // 5), (140, 92, 50))
        if min(ancho, alto) >= 28:
            nx, ny = rnd.randint(8, ancho - 16), rnd.randint(6, alto - 12)
            pygame.draw.ellipse(s, (120, 78, 42), (nx, ny, 9, 6), 2)
        pygame.draw.line(s, (214, 164, 104), (2, 2), (ancho - 3, 2), 2)
        pygame.draw.line(s, (130, 86, 48), (2, alto - 3), (ancho - 3, alto - 3), 2)
        color_borde = TINTA

    elif material == "piedra":
        s.fill((128, 128, 138))
        for _ in range(max(10, ancho * alto // 22)):
            x, y = rnd.randrange(ancho), rnd.randrange(alto)
            c = rnd.choice(((104, 104, 114), (150, 150, 160), (118, 116, 126)))
            s.fill(c, (x, y, 2, 2))
        for _ in range(2):
            x, y = rnd.randint(4, ancho - 4), rnd.randint(4, alto - 4)
            pts = [(x, y)]
            for _ in range(4):
                x = max(2, min(ancho - 3, x + rnd.randint(-6, 6)))
                y = max(2, min(alto - 3, y + rnd.randint(2, 7)))
                pts.append((x, y))
            pygame.draw.lines(s, (80, 80, 92), False, pts, 1)
        pygame.draw.line(s, (176, 176, 186), (2, 2), (ancho - 3, 2), 2)
        pygame.draw.line(s, (90, 90, 102), (2, alto - 3), (ancho - 3, alto - 3), 2)
        color_borde = TINTA

    else:  # vidrio
        s.fill((176, 222, 238, 175))
        for k in range(0, ancho + alto, 14):
            pygame.draw.line(s, (255, 255, 255, 215), (k, 0), (k - alto, alto), 2)
        color_borde = (62, 112, 136)

    _contorno_rect(s, rnd, color_borde)
    return s


def textura_proyectil(radio):
    rnd = random.Random()
    d = 2 * radio
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, (88, 80, 94), (radio, radio), radio - 1)
    pygame.draw.circle(s, (128, 120, 138), (radio - 2, radio - 3), radio - 5)
    pygame.draw.circle(s, (196, 190, 206), (radio - 5, radio - 6), 3)
    _contorno_circulo(s, rnd)
    return s


def textura_objetivo(radio):
    rnd = random.Random()
    d = 2 * radio
    cx = cy = radio
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, (78, 170, 84), (cx, cy), radio - 1)
    pygame.draw.circle(s, (112, 206, 112), (cx - 2, cy - 3), radio - 5)
    pygame.draw.circle(s, (170, 235, 160), (cx - 6, cy - 9), 3)
    for ex in (-6, 6):
        pygame.draw.circle(s, (255, 255, 255), (cx + ex, cy - 2), 5)
        pygame.draw.circle(s, TINTA, (cx + ex + 1, cy - 1), 2)
    pygame.draw.arc(s, TINTA, pygame.Rect(cx - 6, cy + 1, 12, 8), math.pi, 2 * math.pi, 2)
    _contorno_circulo(s, rnd)
    return s


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


def dibujar_honda(surface, origen, suelo_y):
    """Horquilla de madera. Devuelve las dos puntas (donde se atan las bandas)."""
    ox, oy = int(origen[0]), int(origen[1])
    cruz = (ox, oy + 28)
    izq, der = (ox - 16, oy - 2), (ox + 16, oy - 2)
    for color, g in ((TINTA, 14), ((120, 82, 46), 9)):
        pygame.draw.line(surface, color, (ox, suelo_y), cruz, g)
        pygame.draw.line(surface, color, cruz, izq, max(g - 3, 4))
        pygame.draw.line(surface, color, cruz, der, max(g - 3, 4))
    return izq, der


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
