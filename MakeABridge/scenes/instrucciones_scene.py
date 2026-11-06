# fisicas2d/scenes/instrucciones_scene.py
import pygame
from engine.ui import Scene
from ..widgets import SoundButton
from ..fondo import crear_fondo
from .. import estilo
from ..settings import ANCHO, INTENTOS, NIVELES

# (título, [párrafos]) por columna. Todo lo que el jugador tiene que saber antes de empezar.
COLUMNA_IZQ = [
    ("OBJETIVO", [
        "Construí un puente para que el gato cruce el valle y llegue a la bandera.",
    ]),
    ("CONSTRUIR", [
        "Elegí un material con los botones o con las teclas 1 a 5.",
        "Arrastrá el mouse desde un nodo hasta otro punto para crear una viga. "
        "Los puntos naranjas son anclajes fijos del terreno.",
        "Clic derecho: borrar. Tecla Z: deshacer.",
        "Cada viga cuesta según su largo: cuidá el presupuesto.",
    ]),
    ("LA PRUEBA", [
        "Tocá ¡Probar! y el gato empieza a caminar.",
        "Las vigas pasan de verde a rojo: rojo significa que están por romperse.",
        f"Tenés {INTENTOS} intentos por nivel y hay {len(NIVELES)} niveles. ESC vuelve al menú.",
    ]),
]
COLUMNA_DER = [
    ("MATERIALES", [
        "Camino: es lo único que el gato puede pisar. Máximo 5 m por tramo.",
        "Reforz.: camino más resistente y más caro.",
        "Madera y Acero: vigas de estructura, no se pisan. El acero resiste más.",
        "Cable: barato, pero solo resiste tirones: no empuja.",
    ]),
    ("CONSEJOS", [
        "El Camino debe ir sin huecos desde el ancla naranja de arriba de un "
        "acantilado hasta la del otro lado.",
        "Los triángulos hacen la estructura rígida: poné vigas en diagonal debajo del camino.",
        "Los pilares fijos del valle sirven de apoyo.",
    ]),
]


def envolver(texto, fuente, ancho):
    #Parte un texto en líneas que entren en 'ancho' píxeles
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if fuente.size(prueba)[0] <= ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


class InstruccionesScene(Scene):
    #Pantalla previa al juego: explica todo lo que hay que saber antes de empezar

    def __init__(self, game):
        super().__init__(game)
        self.fondo = crear_fondo()
        self.f_titulo = estilo.fuente_arcade(28)
        self.f_sec = estilo.fuente_arcade(12)
        self.f_txt = estilo.fuente_arcade(10)
        audio = game.audio
        self.botones = [
            SoundButton(ANCHO // 2 - 220, 526, 200, 46, "Volver", lambda: game.change_scene("menu"), audio),
            SoundButton(ANCHO // 2 + 20, 526, 300, 46, "¡A jugar!",
                        lambda: game.change_scene("juego", nivel=0), audio),
        ]
        self.panel = pygame.Surface((ANCHO - 60, 420), pygame.SRCALPHA)
        self.panel.fill((246, 238, 216, 225))
        pygame.draw.rect(self.panel, estilo.TINTA, self.panel.get_rect(), 3, border_radius=8)

    def handle_events(self, events):
        for e in events:
            for b in self.botones:
                b.handle_event(e)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.change_scene("menu")
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.game.audio.play_sound("click")
                    self.game.change_scene("juego", nivel=0)

    def update(self):
        self.fondo.update(1)

    def _dibujar_columna(self, surface, secciones, x, y, ancho):
        sangria = self.f_txt.size("- ")[0]
        alto_linea = self.f_txt.get_linesize() + 5
        for titulo, parrafos in secciones:
            surface.blit(self.f_sec.render(titulo, True, (150, 70, 30)), (x, y))
            y += self.f_sec.get_linesize() + 6
            for parrafo in parrafos:
                for i, linea in enumerate(envolver(parrafo, self.f_txt, ancho - sangria)):
                    if i == 0:
                        surface.blit(self.f_txt.render("-", True, estilo.TINTA), (x, y))
                    surface.blit(self.f_txt.render(linea, True, estilo.TINTA), (x + sangria, y))
                    y += alto_linea
                y += 4
            y += 12

    def draw(self, surface):
        self.fondo.draw(surface)
        titulo = self.f_titulo.render("INSTRUCCIONES", True, estilo.TINTA)
        sombra = self.f_titulo.render("INSTRUCCIONES", True, (255, 250, 235))
        surface.blit(sombra, sombra.get_rect(center=(ANCHO // 2 + 3, 43)))
        surface.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 40)))
        surface.blit(self.panel, (30, 80))
        self._dibujar_columna(surface, COLUMNA_IZQ, 55, 100, 430)
        self._dibujar_columna(surface, COLUMNA_DER, 515, 100, 430)
        for b in self.botones:
            b.draw(surface)
