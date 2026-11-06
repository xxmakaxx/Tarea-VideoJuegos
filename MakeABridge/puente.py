# MakeABridge/puente.py
import math
import pygame
import pymunk
from engine.game_object import GameObject
from . import estilo
from .settings import (VIGAS, NODO_MASA, EXCESO_PASOS, GRID, CAT_CAMINO, CAT_VIGA, CAT_CAMINANTE)

TINTA = (55, 38, 24)


def _pixel():
    return pygame.Surface((1, 1), pygame.SRCALPHA)


def color_estres(r):
    #Verde (sin esfuerzo) -> amarillo -> rojo (a punto de romperse).
    r = max(0.0, min(1.0, r))
    if r < 0.5:
        t = r / 0.5
        a, b = (70, 170, 80), (235, 200, 50)
    else:
        t = (r - 0.5) / 0.5
        a, b = (235, 200, 50), (220, 50, 40)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Nodo(GameObject):
    #Articulación. Los nodos 'fijos' son anclajes en el terreno.

    def __init__(self, x, y, fijo=False):
        super().__init__(x, y, _pixel())
        self.pos = pygame.Vector2(x, y)
        self.fijo = fijo
        self.body = None            # cuerpo de Pymunk: solo existe durante la prueba

    def posicion(self):
        if self.body is not None and not self.fijo:
            return pygame.Vector2(self.body.position)
        return self.pos

    def dibujar(self, surface):
        p = self.posicion()
        if self.fijo:                                   # anclaje: disco naranja con brillo
            estilo.disco_pixel(surface, (240, 140, 50), p, 8, borde=2)
            estilo.disco_pixel(surface, (255, 206, 120), (p.x - 2, p.y - 2), 2)
        else:                                           # articulación libre: disco claro
            estilo.disco_pixel(surface, (246, 240, 222), p, 6, borde=2)


def dibujar_viga_pixel(surface, p1, p2, datos, color):
    #Viga pixelada: contorno oscuro + relleno + luz arriba + junturas (camino) o remaches (vigas)
    p1, p2 = pygame.Vector2(p1), pygame.Vector2(p2)
    if datos.get("cable"):
        estilo.linea_pixel(surface, TINTA, p1, p2, 2)
        return

    P = estilo.PIXEL
    gl = max(1, round(datos["grosor"] / P))      # grosor en pixeles de arte
    m = gl + 4
    x0, y0 = int(min(p1.x, p2.x) // P) - m, int(min(p1.y, p2.y) // P) - m
    x1, y1 = int(max(p1.x, p2.x) // P) + m, int(max(p1.y, p2.y) // P) + m
    tmp = pygame.Surface((x1 - x0 + 1, y1 - y0 + 1), pygame.SRCALPHA)
    a = pygame.Vector2(p1.x / P - x0, p1.y / P - y0)
    b = pygame.Vector2(p2.x / P - x0, p2.y / P - y0)
    d = b - a
    largo = d.length()
    pygame.draw.line(tmp, estilo.CONTORNO, a, b, gl + 2)      # contorno
    pygame.draw.line(tmp, color, a, b, gl)                    # relleno
    if largo > 0:
        u = d / largo
        n = pygame.Vector2(-u.y, u.x)
        if n.y > 0:                                           # que "arriba" sea hacia y negativa
            n = -n
        claro = tuple(min(255, ch + 46) for ch in color)
        oscuro = tuple(max(0, ch - 46) for ch in color)
        off = gl / 2 - 0.5
        pygame.draw.line(tmp, claro, a + n * off, b + n * off, 1)       # luz arriba
        pygame.draw.line(tmp, oscuro, a - n * off, b - n * off, 1)      # sombra abajo
        if datos["camina"]:                                         # tablas: junturas cada 4 px
            k = 2.0
            while k < largo - 1:
                q = a + u * k
                for t in range(-(gl // 2) + 1, gl // 2):
                    pt = (int(round(q.x + n.x * t)), int(round(q.y + n.y * t)))
                    if 0 <= pt[0] < tmp.get_width() and 0 <= pt[1] < tmp.get_height():
                        tmp.set_at(pt, oscuro)
                k += 4
        else:                                                            # vigas: remaches en los extremos
            for q in (a + u * 1, b - u * 1):
                pt = (int(round(q.x)), int(round(q.y)))
                tmp.set_at(pt, claro)
    surface.blit(estilo.ampliar(tmp), (x0 * P, y0 * P))





class Viga(GameObject):
    #Una viga entre dos nodos. Según el material puede ser camino (se camina), viga o cable

    def __init__(self, a, b, material):
        super().__init__(a.pos.x, a.pos.y, _pixel())
        self.a, self.b, self.material = a, b, material
        self.datos = VIGAS[material]
        self.longitud = a.pos.distance_to(b.pos)
        self.reiniciar()

    def reiniciar(self):
        self.cuerpo = None
        self.juntas = []
        self.rota = False
        self.estres = 0.0
        self._exceso = 0

    @property
    def costo(self):
        return int(round(self.longitud / GRID * self.datos["precio"]))

    def extremos(self):
        if self.cuerpo is not None and not self.datos.get("cable"):
            m = self.longitud / 2
            return (pygame.Vector2(self.cuerpo.local_to_world((-m, 0))),
                    pygame.Vector2(self.cuerpo.local_to_world((m, 0))))
        return self.a.posicion(), self.b.posicion()

    def distancia_a(self, p):
        #Distancia de un punto al segmento (para poder borrarla con el mouse)
        a, b = self.a.pos, self.b.pos
        ab = b - a
        t = 0 if ab.length_squared() == 0 else max(0, min(1, (p - a).dot(ab) / ab.length_squared()))
        return (a + ab * t).distance_to(p)

    def dibujar(self, surface, simulando):
        """Dibuja la viga con aspecto pixel art (ver dibujar_viga_pixel)."""
        if self.datos.get("cable") and self.rota:
            return
        p1, p2 = self.extremos()
        base = self.datos["color"]
        if simulando:
            r = round(self.estres * 4) / 4              # el color cambia por escalones (como una paleta de 8 bits)
            c = color_estres(r)
            color = tuple(int(base[i] * 0.3 + c[i] * 0.7) for i in range(3))
        else:
            color = base
        dibujar_viga_pixel(surface, p1, p2, self.datos, color)


# ----------------------------------------------------------------------- física
def construir_fisica(mundo, nodos, vigas):
    #Crea cuerpos y uniones de Pymunk a partir del diseño del jugador
    space = mundo.space
    for n in nodos:
        if not n.fijo:
            n.body = pymunk.Body(NODO_MASA, pymunk.moment_for_circle(NODO_MASA, 0, 6))
            n.body.position = (n.pos.x, n.pos.y)
            space.add(n.body)

    for v in vigas:
        v.reiniciar()
        pa, pb = v.a.pos, v.b.pos
        ba = space.static_body if v.a.fijo else v.a.body
        bb = space.static_body if v.b.fijo else v.b.body

        if v.datos.get("cable"):
            if ba is bb:                      # dos anclajes: ambos son el cuerpo estático y Pymunk no admite a is b
                v.juntas = []
                continue
            anc_a = (pa.x, pa.y) if v.a.fijo else (0, 0)
            anc_b = (pb.x, pb.y) if v.b.fijo else (0, 0)
            v.juntas = [pymunk.SlideJoint(ba, bb, anc_a, anc_b, 0, v.longitud)]
            space.add(*v.juntas)
            continue

        masa = v.datos["densidad"] * v.longitud
        m = v.longitud / 2
        radio = v.datos["grosor"] / 2
        cuerpo = pymunk.Body(masa, pymunk.moment_for_segment(masa, (-m, 0), (m, 0), radio))
        d = pb - pa
        cuerpo.position = ((pa.x + pb.x) / 2, (pa.y + pb.y) / 2)
        cuerpo.angle = math.atan2(d.y, d.x)
        forma = pymunk.Segment(cuerpo, (-m, 0), (m, 0), radio)
        forma.friction = 0.9
        forma.elasticity = 0.0
        if v.datos["camina"]:
            forma.filter = pymunk.ShapeFilter(categories=CAT_CAMINO, mask=CAT_CAMINANTE)
        else:
            forma.filter = pymunk.ShapeFilter(categories=CAT_VIGA, mask=0)
        v.cuerpo = cuerpo
        v.juntas = [pymunk.PivotJoint(cuerpo, ba, (pa.x, pa.y)),
                    pymunk.PivotJoint(cuerpo, bb, (pb.x, pb.y))]
        space.add(cuerpo, forma, *v.juntas)


def revisar_roturas(mundo, vigas, dt):
    #Después de cada subpaso: mide la fuerza de cada unión y rompe las vigas sobrecargadas
    for v in vigas:
        if v.rota or not v.juntas:
            continue
        fuerza = max(j.impulse for j in v.juntas) / dt
        ratio = fuerza / v.datos["resist"]
        v.estres = 0.9 * v.estres + 0.1 * ratio
        if ratio > 1.0:
            v._exceso += 1
        else:
            v._exceso = max(0, v._exceso - 1)
        if v._exceso >= EXCESO_PASOS:
            mundo.space.remove(*v.juntas)
            v.juntas = []
            v.rota = True
