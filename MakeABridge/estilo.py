# MakeABridge/estilo.py
import math
import os
import random
import pygame
from .settings import ASSETS_DIR

PAPEL = (241, 230, 205)
TINTA = (55, 38, 24)


_FUENTES = {}


def fuente_arcade(tam):
    #Fuente estilo arcade (Press Start 2P, licencia OFL, en assets/fonts). Si no está, se usa una fuente monoespaciada del sistema.
    if tam not in _FUENTES:
        ruta = os.path.join(ASSETS_DIR, "fonts", "PressStart2P-Regular.ttf")
        if os.path.exists(ruta):
            _FUENTES[tam] = pygame.font.Font(ruta, tam)
        else:
            _FUENTES[tam] = pygame.font.SysFont("consolas,couriernew,lucidaconsole,monospace", int(tam * 1.4), bold=True)
    return _FUENTES[tam]


# ---------------------------------------------------------------- utilidades pixel art
PIXEL = 2   # tamaño de cada "pixel de arte" en pantalla. 2 = fino, 3 = más grueso (ver nota sobre el gato)

# Paleta limitada (estilo consola de 8/16 bits)
CONTORNO = (34, 24, 38)
PASTO_CLARO, PASTO, PASTO_OSCURO = (132, 208, 76), (84, 168, 68), (40, 108, 60)
TIERRA, TIERRA_CLARA, TIERRA_OSCURA = (150, 98, 58), (182, 128, 76), (108, 68, 48)
PIEDRA, PIEDRA_OSCURA = (168, 156, 146), (122, 112, 112)


def ampliar(baja, ancho=None, alto=None):
    #Agranda una superficie de baja resolución x PIXEL (vecino más cercano: sin suavizar).
    w, h = baja.get_width() * PIXEL, baja.get_height() * PIXEL
    img = pygame.transform.scale(baja, (w, h))
    if ancho is not None and (ancho, alto) != (w, h):      # recorta al tamaño exacto pedido
        out = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        out.blit(img, (0, 0))
        return out
    return img


def _contorno(s, color=CONTORNO):
    #Agrega un borde de 1 pixel de arte alrededor de lo dibujado (los pixeles transparentes
    #que tocan algo opaco por arriba/abajo/izquierda/derecha pasan a ser 'color')
    w, h = s.get_size()
    marcas = []
    for y in range(h):
        for x in range(w):
            if s.get_at((x, y)).a == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and s.get_at((nx, ny)).a > 0:
                        marcas.append((x, y))
                        break
    for p in marcas:
        s.set_at(p, color)
    return s


def linea_pixel(surface, color, p1, p2, grosor):
    #Línea gruesa con aspecto pixelado (se dibuja en baja resolución y se agranda).
    #p1/p2 en píxeles de pantalla, grosor en píxeles de pantalla.
    P = PIXEL
    gl = max(1, round(grosor / P))
    m = gl + 2
    x0, y0 = int(min(p1[0], p2[0]) // P) - m, int(min(p1[1], p2[1]) // P) - m
    x1, y1 = int(max(p1[0], p2[0]) // P) + m, int(max(p1[1], p2[1]) // P) + m
    tmp = pygame.Surface((x1 - x0 + 1, y1 - y0 + 1), pygame.SRCALPHA)
    pygame.draw.line(tmp, color, (p1[0] / P - x0, p1[1] / P - y0), (p2[0] / P - x0, p2[1] / P - y0), gl)
    surface.blit(ampliar(tmp), (x0 * P, y0 * P))


def disco_pixel(surface, color, centro, radio, borde=0, borde_color=CONTORNO):
    #Círculo pixelado. radio en píxeles de pantalla
    P = PIXEL
    r = max(1, round(radio / P))
    tmp = pygame.Surface((2 * r + 3, 2 * r + 3), pygame.SRCALPHA)
    c = (r + 1, r + 1)
    if borde:
        pygame.draw.circle(tmp, borde_color, c, r)
        pygame.draw.circle(tmp, color, c, max(1, r - borde))
    else:
        pygame.draw.circle(tmp, color, c, r)
    surface.blit(ampliar(tmp), (round(centro[0] / P) * P - (r + 1) * P, round(centro[1] / P) * P - (r + 1) * P))


# ---------------------------------------------------------------- terreno
def textura_suelo(ancho, alto, hierba=14):
    #Tierra con piedritas, estratos y pasto en bloques. La imagen sobresale 'hierba' px por arriba
    rnd = random.Random(11)
    w, h = -(-ancho // PIXEL), -(-(alto + hierba) // PIXEL)
    gh = hierba // PIXEL                       # fila donde empieza la superficie
    s = pygame.Surface((w, h), pygame.SRCALPHA)

    # tierra
    s.fill(TIERRA, (0, gh, w, h - gh))
    for y in range(gh + 4, h):
        for x in range(w):
            r = rnd.random()
            if r < 0.07:
                s.set_at((x, y), TIERRA_OSCURA)
            elif r < 0.12:
                s.set_at((x, y), TIERRA_CLARA)
    # sombra bajo el pasto (tramado en damero)
    for y in range(gh + 4, gh + 8):
        for x in range(w):
            if (x + y) % 2 == 0 or y < gh + 6:
                s.set_at((x, y), TIERRA_OSCURA)
    # estratos: líneas oscuras horizontales con "ladrillos" desfasados
    for i, y in enumerate(range(gh + 14, h, 12)):
        for x in range(w):
            if (x + i * 5) % 11 < 7:
                s.set_at((x, y), TIERRA_OSCURA)
    # piedritas
    for _ in range(w * h // 260):
        x, y = rnd.randrange(1, w - 3), rnd.randrange(gh + 9, max(gh + 10, h - 2))
        s.fill(PIEDRA, (x, y, 2, 1))
        s.fill(PIEDRA_OSCURA, (x, y + 1, 2, 1))
        s.set_at((x, y), (214, 204, 196))
    # pasto: tapa de 3 filas + pelito oscuro debajo
    s.fill(PASTO_CLARO, (0, gh, w, 1))
    s.fill(PASTO, (0, gh + 1, w, 2))
    s.fill(PASTO_OSCURO, (0, gh + 3, w, 1))
    # flecos que cuelgan del pasto
    for x in range(w):
        if rnd.random() < 0.55:
            s.set_at((x, gh + 4), PASTO_OSCURO)
        if rnd.random() < 0.25:
            s.set_at((x, gh + 5), PASTO_OSCURO)
    # pastitos que sobresalen por arriba
    x = 0
    while x < w:
        alto_p = rnd.randint(1, gh)
        s.set_at((x, gh - 1), PASTO)
        for k in range(2, alto_p + 1):
            s.set_at((x, gh - k), PASTO_CLARO if k == alto_p else PASTO)
        x += rnd.randint(2, 4)

    _contorno(s)
    # bordes laterales firmes (el contorno automático no los ve si tocan el borde de la imagen)
    for y in range(gh, h):
        s.set_at((0, y), CONTORNO)
        s.set_at((w - 1, y), CONTORNO)
    return ampliar(s, ancho, alto + hierba)


# ---------------------------------------------------------------- fondo
SKY = [(76, 132, 232), (104, 160, 244), (136, 188, 250), (170, 214, 252), (204, 234, 252), (232, 246, 252)]


def papel(ancho, alto, suelo_y):
    #Cielo en franjas con tramado (dither) entre colores + sol pixelado. (Se llama 'papel' por compatibilidad.)
    w, h = ancho // PIXEL, alto // PIXEL
    s = pygame.Surface((w, h))
    zona = (suelo_y // PIXEL)
    n = len(SKY)
    banda = zona / n
    for y in range(h):
        i = min(n - 1, int(y / banda))
        base = SKY[i]
        sig = SKY[min(n - 1, i + 1)]
        pos = y - i * banda                       # fila dentro de la banda
        resto = banda - pos
        for x in range(w):
            c = base
            if resto < 6 and i < n - 1:           # últimas filas: mezcla en damero con la banda siguiente
                if resto < 2 and (x + y) % 2 == 0:
                    c = sig
                elif 2 <= resto < 4 and (x % 2 == 0 and y % 2 == 0):
                    c = sig
                elif 4 <= resto < 6 and (x % 4 == 0 and y % 2 == 0):
                    c = sig
            s.set_at((x, y), c)
    # sol
    cx, cy = int(w * 0.91), int(h * 0.37)
    pygame.draw.circle(s, (255, 236, 130), (cx, cy), 14)
    pygame.draw.circle(s, (255, 250, 190), (cx - 1, cy - 1), 10)
    for ang in range(0, 360, 45):                 # rayitos
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        pygame.draw.line(s, (255, 236, 130), (cx + dx * 18, cy + dy * 18), (cx + dx * 23, cy + dy * 23), 1)
    return ampliar(s)


def grano_y_vineta(ancho, alto):
    #Capa de líneas de escaneo muy suaves (efecto CRT). Si no te gusta, no la dibujes en fondo.py.
    ov = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for y in range(0, alto, PIXEL * 2):
        ov.fill((0, 0, 30, 14), (0, y, ancho, PIXEL))
    return ov


def textura_meta():
    #Bandera de meta pixelada (50x80).
    s = pygame.Surface((25, 40), pygame.SRCALPHA)
    # banderín rojo (triángulo escalonado) con borde claro arriba y sombra abajo
    for r in range(13):
        largo = int(15 - abs(r - 6) * 2.3)
        if largo < 1:
            continue
        for c in range(largo):
            col = (226, 66, 58)
            if r < 2:
                col = (250, 120, 100)
            elif r > 9:
                col = (170, 40, 52)
            s.set_at((7 + c, 3 + r), col)
    # mástil
    s.fill((176, 120, 70), (6, 2, 2, 36))
    s.fill((222, 170, 100), (6, 2, 1, 36))
    # bolita dorada
    s.fill((255, 218, 70), (5, 0, 4, 2))
    # montoncito de piedras en la base
    s.fill(PIEDRA, (2, 35, 11, 4))
    s.fill(PIEDRA_OSCURA, (2, 38, 11, 1))
    s.fill((214, 204, 196), (4, 35, 3, 1))
    _contorno(s)
    return ampliar(s)


def frames_muneco(n=8):
    #Ciclo de marcha de un muñeco (24x44). El último frame del ciclo vuelve al primero.
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
    #Ciclo de marcha de un gato naranja pixelado (44x30 en pantalla = 22x15 pixeles de arte).
    #Mira a la derecha. Los pies terminan en y=24, para que encaje con la física.
    NAR, OSC, CLA = (240, 152, 64), (190, 98, 44), (252, 226, 178)
    ROSA, OJO = (240, 120, 140), (34, 24, 38)
    frames = []
    for i in range(n):
        fase = 2 * math.pi * i / n
        s = pygame.Surface((22, 15), pygame.SRCALPHA)
        # cola: base horizontal y punta que se balancea
        punta = 1 + round(math.sin(fase) * 1.2) + 1
        s.fill(NAR, (2, 4, 2, 2))
        s.fill(NAR, (1, punta, 2, 6 - punta))
        s.fill(OSC, (1, punta, 2, 1))
        # patas del fondo (más oscuras): par diagonal contrario
        for x0, desfase in ((5, math.pi), (14, 0.0)):
            dx = round(math.sin(fase + desfase) * 2)
            alza = 1 if math.cos(fase + desfase) > 0.55 else 0
            s.fill(OSC, (x0 + dx, 8, 2, 3 - alza))
        # cuerpo (con esquinas recortadas)
        s.fill(NAR, (3, 3, 12, 5))
        for p in ((3, 3), (14, 3), (3, 7), (14, 7)):
            s.set_at(p, (0, 0, 0, 0))
        s.fill(CLA, (5, 7, 8, 1))                                # panza
        for rx in (6, 9, 11):                                     # rayas
            s.fill(OSC, (rx, 3, 1, 2))
        # cabeza y orejas
        s.fill(NAR, (13, 3, 8, 6))
        for p in ((13, 3), (20, 3), (13, 8), (20, 8)):
            s.set_at(p, (0, 0, 0, 0))
        for p in ((13, 1), (13, 2), (14, 2), (20, 1), (20, 2), (19, 2)):
            s.set_at(p, NAR)
        s.set_at((13, 2), ROSA)
        s.set_at((20, 2), ROSA)
        s.fill(OSC, (12, 4, 1, 4))                                # cuello: separa cabeza y cuerpo
        s.fill(CLA, (17, 6, 4, 2))                                # hocico
        s.set_at((20, 6), ROSA)                                   # nariz
        s.fill(OJO, (17, 4, 1, 2))                                # ojo
        s.set_at((16, 3), OSC)                                    # rayas de la frente
        s.set_at((16, 4), OSC)
        # patas del frente (más claras): par diagonal
        for x0, desfase in ((3, 0.0), (12, math.pi)):
            dx = round(math.sin(fase + desfase) * 2)
            alza = 1 if math.cos(fase + desfase) > 0.55 else 0
            s.fill(NAR, (x0 + dx, 8, 2, 3 - alza))
            s.set_at((x0 + dx, 10 - alza), CLA)                   # patita blanca
            s.set_at((x0 + dx + 1, 10 - alza), CLA)
        _contorno(s)
        frames.append(ampliar(s))
    return frames


def frames_caminante(n=8):
    #Devuelve los frames del personaje elegido en settings.PERSONAJE
    from .settings import PERSONAJE
    return frames_gato(n) if PERSONAJE == "gato" else frames_muneco(n)


# ---------------------------------------------------------------- iconos pixelados para la interfaz
def icono_pixel(nombre, escala=3, color=(250, 238, 206)):
    def lienzo(w, h):
        return pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)            # 1 pixel de margen para el contorno

    if nombre == "jugar":
        s = lienzo(12, 11)
        for r in range(11):
            s.fill(color, (1, 1 + r, min(r, 10 - r) * 2 + 2, 1))
    elif nombre == "deshacer":
        s = lienzo(13, 8)
        for fila, patron in enumerate(("..#..........",
                                       ".##..........",
                                       "###########..",
                                       ".##.......###",
                                       "..#.......###",
                                       "..........###",
                                       "....#######..",
                                       ".............")):
            for x, ch in enumerate(patron):
                if ch == "#":
                    s.set_at((1 + x, 1 + fila), color)
    elif nombre == "basura":
        s = lienzo(10, 12)
        s.fill(color, (4, 1, 4, 2))                                          # manija
        s.fill(color, (1, 3, 10, 2))                                         # tapa
        s.fill(color, (2, 6, 8, 7))                                          # tacho
        for x in (4, 7):
            s.fill(tuple(max(0, c - 90) for c in color), (x, 7, 1, 5))       # rayitas
    elif nombre == "corazon":
        s = lienzo(7, 6)
        for fila, patron in enumerate((".##.##.", "#######", "#######", ".#####.", "..###..", "...#...")):
            for x, ch in enumerate(patron):
                if ch == "#":
                    s.set_at((1 + x, 1 + fila), color)
        s.set_at((2, 2), tuple(min(255, c + 60) for c in color))             # brillo
    else:
        raise ValueError(nombre)
    _contorno(s)
    return pygame.transform.scale(s, (s.get_width() * escala, s.get_height() * escala))
