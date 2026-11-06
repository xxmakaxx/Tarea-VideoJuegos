# MakeABridge/widgets.py
import pygame
from engine.ui import Button
from . import estilo
from .settings import GRID

CREMA = (250, 238, 206)
DORADO = (255, 214, 90)
ROJO = (236, 96, 84)


def panel_pixel(surface, rect, color, borde=estilo.CONTORNO, grosor=2):
    #Panel con esquinas "comidas" y bisel (luz arriba/izquierda, sombra abajo/derecha)
    r = pygame.Rect(rect)
    pygame.draw.rect(surface, borde, r.inflate(-2 * grosor, 0))
    pygame.draw.rect(surface, borde, r.inflate(0, -2 * grosor))
    inner = r.inflate(-2 * grosor, -2 * grosor)
    luz = tuple(min(255, c + 36) for c in color)
    sombra = tuple(max(0, c - 36) for c in color)
    pygame.draw.rect(surface, color, inner)
    pygame.draw.rect(surface, luz, (inner.x, inner.y, inner.w, 2))
    pygame.draw.rect(surface, luz, (inner.x, inner.y, 2, inner.h))
    pygame.draw.rect(surface, sombra, (inner.x, inner.bottom - 2, inner.w, 2))
    pygame.draw.rect(surface, sombra, (inner.right - 2, inner.y, 2, inner.h))


def _texto(surface, fuente, texto, pos, color, anclaje="topleft"):
    #Texto con sombra oscura de 1 pixel (se lee mejor sobre madera).
    sombra = fuente.render(texto, True, estilo.CONTORNO)
    t = fuente.render(texto, True, color)
    r = t.get_rect(**{anclaje: pos})
    surface.blit(sombra, r.move(2, 2))
    surface.blit(t, r)
    return r


class SoundButton(Button):
    #Button del motor con retorno de sonido al hacer click (requisito común de la tarea).
    #Se dibuja como panel pixel art (esquinas cuadradas con bisel) en vez del rectángulo redondeado del motor

    def __init__(self, x, y, width, height, text, callback, audio=None, sound_name="click", **kw):
        kw.setdefault("color", (120, 82, 46))          # madera, a juego con el estilo del juego
        kw.setdefault("hover_color", (150, 105, 60))
        super().__init__(x, y, width, height, text, callback, **kw)
        self.audio = audio
        self.sound_name = sound_name
        # el motor pide font_size para la fuente por defecto; acá lo traducimos a la fuente arcade
        self.font = estilo.fuente_arcade(max(8, round(kw.get("font_size", 40) * 0.45)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.audio:
                self.audio.play_sound(self.sound_name)
        super().handle_event(event)

    def draw(self, surface):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        panel_pixel(surface, self.rect, self.hover_color if hover else self.color)
        _texto(surface, self.font, self.text, self.rect.center, self.text_color, "center")


class SelectorMaterial:
    #Tarjeta de un material: muestra la viga tal como se ve en el juego, el nombre, el precio por metro,
    #si se puede caminar encima, el largo máximo y una barra de resistencia. Atajo de teclado = número.

    def __init__(self, x, y, ancho, alto, material, datos, indice, resist_max, callback, audio=None, marco=True, fila=False, ranura=False):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.material, self.datos, self.indice = material, datos, indice
        self.resist_max = resist_max
        self.callback = callback
        self.audio = audio
        self.marco = marco                           # False = sin recuadro, solo la viga y el texto
        self.fila = fila                             # True = disposición para columna vertical (una fila por material)
        self.ranura = ranura                         # True = solo el ícono de la viga (barra inferior)
        self.seleccionado = False
        self.restante = 10 ** 9                      # presupuesto: lo actualiza la escena antes de dibujar
        self.f_nombre = estilo.fuente_arcade(10)
        self.f_chica = estilo.fuente_arcade(8)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            if self.audio:
                self.audio.play_sound("click")
            self.callback()

    def draw(self, surface):
        from .puente import dibujar_viga_pixel       # import diferido: puente importa estilo, no widgets
        r, d = self.rect, self.datos
        if self.ranura:
            return self._dibujar_ranura(surface, dibujar_viga_pixel)
        if self.fila:
            return self._dibujar_fila(surface, dibujar_viga_pixel)
        if not self.marco:
            return self._dibujar_sin_marco(surface, dibujar_viga_pixel)
        hover = r.collidepoint(pygame.mouse.get_pos())
        puede = self.restante >= d["precio"]
        if self.seleccionado:
            fondo, borde = (150, 104, 58), DORADO
        else:
            fondo, borde = ((120, 84, 50) if hover else (92, 62, 40)), estilo.CONTORNO
        if not puede and not self.seleccionado:
            fondo = (70, 56, 50)
        panel_pixel(surface, r, fondo, borde, grosor=2 if not self.seleccionado else 4)

        # número de atajo (esquina superior izquierda)
        ins = pygame.Rect(r.x + 8, r.y + 8, 18, 18)
        pygame.draw.rect(surface, estilo.CONTORNO, ins)
        _texto(surface, self.f_chica, str(self.indice + 1), ins.center, CREMA, "center")

        # muestra de la viga (misma función de dibujo que usa el puente)
        y_m = r.y + 17
        dibujar_viga_pixel(surface, (r.x + 38, y_m), (r.right - 14, y_m), d, d["color"])

        # nombre y precio por metro
        _texto(surface, self.f_nombre, d["nombre"], (r.x + 10, r.y + 32), CREMA)
        _texto(surface, self.f_nombre, f"${d['precio']}", (r.right - 10, r.y + 32),
               CREMA if puede else ROJO, "topright")

        # tipo + largo máximo
        tipo = "pisable" if d["camina"] else "soporte"
        _texto(surface, self.f_chica, f"{tipo} {d['max_largo'] // GRID}m", (r.x + 10, r.y + 46), (226, 200, 150))

        # barra de resistencia (5 segmentos)
        llenos = max(1, round(5 * d["resist"] / self.resist_max))
        for i in range(5):
            seg = pygame.Rect(r.right - 10 - (5 - i) * 7 + 1, r.y + 46, 5, 8)
            pygame.draw.rect(surface, estilo.CONTORNO, seg.inflate(2, 2))
            pygame.draw.rect(surface, (110, 220, 110) if i < llenos else (70, 58, 52), seg)

    def _dibujar_ranura(self, surface, dibujar_viga_pixel):
        #Barra inferior: ícono de la viga (inclinada) + número de atajo + precio. La elegida se resalta con borde dorado
        r, d = self.rect, self.datos
        hover = r.collidepoint(pygame.mouse.get_pos())
        puede = self.restante >= d["precio"]
        if self.seleccionado:
            panel_pixel(surface, r, (126, 112, 138), DORADO, grosor=3)
        elif hover:
            panel_pixel(surface, r, (70, 58, 80), (30, 24, 38), grosor=2)
        capa = pygame.Surface(r.size, pygame.SRCALPHA)
        if d.get("cable"):                                    # el cable es oscuro: en la barra se dibuja claro
            estilo.linea_pixel(capa, (214, 194, 160), (16, r.h - 20), (r.w - 16, 12), 3)
        else:
            dibujar_viga_pixel(capa, (16, r.h - 20), (r.w - 16, 12), d, d["color"])
        if not puede and not self.seleccionado:
            capa.set_alpha(100)
        surface.blit(capa, r.topleft)
        _texto(surface, self.f_chica, str(self.indice + 1), (r.x + 7, r.y + 6), CREMA)
        _texto(surface, self.f_chica, f"${d['precio']}", (r.centerx, r.bottom - 6), CREMA if puede else ROJO, "midbottom")

    def _dibujar_fila(self, surface, dibujar_viga_pixel):
        #Disposición para una columna a la izquierda: nombre y precio arriba, la viga en el medio,
        #tipo/largo y resistencia abajo. Con marco=False flota sobre el cielo
        r, d = self.rect, self.datos
        hover = r.collidepoint(pygame.mouse.get_pos())
        puede = self.restante >= d["precio"]
        if self.marco:
            fondo = (150, 104, 58) if self.seleccionado else ((120, 84, 50) if hover else (92, 62, 40))
            if not puede and not self.seleccionado:
                fondo = (70, 56, 50)
            panel_pixel(surface, r, fondo, DORADO if self.seleccionado else estilo.CONTORNO, grosor=3 if self.seleccionado else 2)
            txt = lambda f, t, p, c, a="topleft": _texto(surface, f, t, p, c, a)
            c_main, c_sub, c_no = CREMA, (226, 200, 150), ROJO
            c_seg_vacio = (70, 58, 52)
        else:
            luz = (250, 242, 214)
            txt = lambda f, t, p, c, a="topleft": _texto_claro(surface, f, t, p, c, luz, a)
            c_main, c_sub, c_no = estilo.TINTA, (70, 52, 44), (190, 40, 40)
            c_seg_vacio = (150, 160, 180)
            if self.seleccionado:                                   # velo claro suave detrás de la elegida
                velo = pygame.Surface(r.size, pygame.SRCALPHA)
                velo.fill((255, 255, 255, 70))
                surface.blit(velo, r.topleft)

        txt(self.f_chica, str(self.indice + 1), (r.x + 6, r.y + 5), c_main)             # atajo de teclado
        txt(self.f_nombre, d["nombre"], (r.x + 22, r.y + 4), c_main)
        txt(self.f_nombre, f"${d['precio']}", (r.right - 8, r.y + 4), c_main if puede else c_no, "topright")

        capa = pygame.Surface(r.size, pygame.SRCALPHA)                                   # muestra de la viga
        dibujar_viga_pixel(capa, (24, 26), (r.w - 12, 26), d, d["color"])
        if not puede and not self.seleccionado:
            capa.set_alpha(110)
        surface.blit(capa, r.topleft)

        tipo = "pisable" if d["camina"] else "soporte"
        txt(self.f_chica, f"{tipo} {d['max_largo'] // GRID}m", (r.x + 22, r.y + 36), c_sub)
        llenos = max(1, round(5 * d["resist"] / self.resist_max))
        for i in range(5):
            seg = pygame.Rect(r.right - 8 - (5 - i) * 7 + 1, r.y + 36, 5, 8)
            pygame.draw.rect(surface, estilo.CONTORNO, seg.inflate(2, 2))
            pygame.draw.rect(surface, (110, 220, 110) if i < llenos else c_seg_vacio, seg)

        if not self.marco:                                                               # marca de selección a la izquierda
            if self.seleccionado:
                barra = pygame.Rect(r.x - 8, r.y + 3, 4, r.h - 6)
                pygame.draw.rect(surface, estilo.CONTORNO, barra.inflate(4, 4))
                pygame.draw.rect(surface, DORADO, barra)
            elif hover:
                barra = pygame.Rect(r.x - 7, r.y + 3, 2, r.h - 6)
                pygame.draw.rect(surface, estilo.CONTORNO, barra.inflate(4, 4))
                pygame.draw.rect(surface, (255, 255, 255), barra)

    def _dibujar_sin_marco(self, surface, dibujar_viga_pixel):
        #Versión limpia: la viga flota sobre el cielo, texto oscuro con sombra clara y una línea dorada si está elegida
        r, d = self.rect, self.datos
        hover = r.collidepoint(pygame.mouse.get_pos())
        puede = self.restante >= d["precio"]
        tinta, luz = estilo.TINTA, (250, 242, 214)

        def txt(fuente, texto, pos, color, ancla="topleft"):
            return _texto_claro(surface, fuente, texto, pos, color, luz, ancla)

        if self.seleccionado:                                   # velo claro muy suave detrás de la elegida
            velo = pygame.Surface(r.size, pygame.SRCALPHA)
            velo.fill((255, 255, 255, 70))
            surface.blit(velo, r.topleft)

        # muestra de la viga (atenuada si no alcanza el presupuesto)
        capa = pygame.Surface(r.size, pygame.SRCALPHA)
        dibujar_viga_pixel(capa, (20, 15), (r.w - 12, 15), d, d["color"])
        if not puede and not self.seleccionado:
            capa.set_alpha(110)
        surface.blit(capa, r.topleft)

        txt(self.f_chica, str(self.indice + 1), (r.x + 5, r.y + 5), tinta)              # atajo de teclado
        txt(self.f_nombre, d["nombre"], (r.x + 6, r.y + 30), tinta)
        txt(self.f_nombre, f"${d['precio']}", (r.right - 6, r.y + 30), (190, 40, 40) if not puede else tinta, "topright")
        tipo = "pisable" if d["camina"] else "soporte"
        txt(self.f_chica, f"{tipo} {d['max_largo'] // GRID}m", (r.x + 6, r.y + 44), (70, 52, 44))

        llenos = max(1, round(5 * d["resist"] / self.resist_max))
        for i in range(5):
            seg = pygame.Rect(r.right - 6 - (5 - i) * 7 + 1, r.y + 44, 5, 8)
            pygame.draw.rect(surface, estilo.CONTORNO, seg.inflate(2, 2))
            pygame.draw.rect(surface, (110, 220, 110) if i < llenos else (150, 160, 180), seg)

        # selección: línea dorada gruesa abajo (y una blanca fina al pasar el mouse)
        if self.seleccionado:
            barra = pygame.Rect(r.x + 2, r.bottom + 1, r.w - 4, 4)
            pygame.draw.rect(surface, estilo.CONTORNO, barra.inflate(4, 4))
            pygame.draw.rect(surface, DORADO, barra)
        elif hover:
            barra = pygame.Rect(r.x + 2, r.bottom + 2, r.w - 4, 2)
            pygame.draw.rect(surface, estilo.CONTORNO, barra.inflate(4, 4))
            pygame.draw.rect(surface, (255, 255, 255), barra)


def _texto_claro(surface, fuente, texto, pos, color, sombra_color, anclaje="topleft"):
    """Texto oscuro con sombra clara de 1 pixel de arte (para leer sobre el cielo)."""
    sombra = fuente.render(texto, True, sombra_color)
    t = fuente.render(texto, True, color)
    r = t.get_rect(**{anclaje: pos})
    surface.blit(sombra, r.move(2, 2))
    surface.blit(t, r)
    return r


class IconButton:
    #Botón cuadrado con un ícono pixelado (jugar, deshacer, basura...). Misma interfaz que SoundButton

    def __init__(self, x, y, ancho, alto, icono, callback, audio=None, color=(120, 82, 46), hover_color=(150, 105, 60),
                 color_icono=CREMA, escala=2):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.callback, self.audio = callback, audio
        self.color, self.hover_color = color, hover_color
        self.img = estilo.icono_pixel(icono, escala, color_icono)
        self.img_apagada = self.img.copy()
        self.img_apagada.set_alpha(90)
        self.deshabilitado = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            if self.deshabilitado:
                return
            if self.audio:
                self.audio.play_sound("click")
            self.callback()

    def draw(self, surface):
        hover = self.rect.collidepoint(pygame.mouse.get_pos()) and not self.deshabilitado
        color = (58, 48, 64) if self.deshabilitado else (self.hover_color if hover else self.color)
        panel_pixel(surface, self.rect, color)
        img = self.img_apagada if self.deshabilitado else self.img
        surface.blit(img, img.get_rect(center=self.rect.center))


def dibujar_info_material(surface, rect, d, resist_max, restante):
    """Panel de información del material elegido (barra inferior): nombre, precio por metro, tipo, largo y resistencia."""
    f1, f2 = estilo.fuente_arcade(12), estilo.fuente_arcade(8)
    x, y = rect.topleft
    r = _texto(surface, f1, d["nombre"], (x, y + 6), CREMA)
    puede = restante >= d["precio"]
    _texto(surface, f2, f"${d['precio']} por metro", (r.right + 14, y + 9), CREMA if puede else ROJO)
    tipo = "se puede caminar" if d["camina"] else "solo estructura"
    _texto(surface, f2, f"{tipo}  -  largo máx. {d['max_largo'] // GRID} m", (x, y + 30), (226, 200, 150))
    _texto(surface, f2, "Resistencia", (rect.right, y + 6), (226, 200, 150), "topright")
    llenos = max(1, round(5 * d["resist"] / resist_max))
    for i in range(5):
        seg = pygame.Rect(rect.right - (5 - i) * 14 + 2, y + 22, 10, 12)
        pygame.draw.rect(surface, estilo.CONTORNO, seg.inflate(4, 4))
        pygame.draw.rect(surface, (110, 220, 110) if i < llenos else (70, 58, 82), seg)
