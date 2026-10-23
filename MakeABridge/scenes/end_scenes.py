# fisicas2d/scenes/end_scenes.py
import pygame
from engine.ui import Scene
from ..widgets import SoundButton
from ..fondo import crear_fondo
from .. import estilo
from ..settings import ANCHO, NIVELES


class FinScene(Scene):
    TEXTO = ""
    COLOR = (255, 255, 255)

    def __init__(self, game, nivel=0):
        super().__init__(game)
        self.nivel = nivel
        self.fondo = crear_fondo()
        self.fuente = estilo.fuente_arcade(56)
        self.fuente_sub = estilo.fuente_arcade(14)
        self.subtitulo = ""
        self.botones = []

    def _boton(self, y, texto, callback):
        self.botones.append(SoundButton(ANCHO // 2 - 160, y, 320, 56, texto, callback, self.game.audio))

    def handle_events(self, events):
        for e in events:
            for b in self.botones:
                b.handle_event(e)

    def update(self):
        self.fondo.update(1)

    def draw(self, surface):
        self.fondo.draw(surface)
        sombra = self.fuente.render(self.TEXTO, True, (255, 250, 235))
        t = self.fuente.render(self.TEXTO, True, self.COLOR)
        surface.blit(sombra, sombra.get_rect(center=(ANCHO // 2 + 3, 173)))
        surface.blit(t, t.get_rect(center=(ANCHO // 2, 170)))
        if self.subtitulo:
            sub = self.fuente_sub.render(self.subtitulo, True, estilo.TINTA)
            surface.blit(sub, sub.get_rect(center=(ANCHO // 2, 240)))
        for b in self.botones:
            b.draw(surface)


class GameOverScene(FinScene):
    TEXTO = "GAME OVER"
    COLOR = (160, 48, 40)

    def __init__(self, game, nivel=0):
        super().__init__(game, nivel)
        self.subtitulo = "El puente no resistió... ¡probá otra estructura!"
        self._boton(300, "Reintentar", lambda: game.change_scene("juego", nivel=self.nivel))
        self._boton(370, "Volver al menú", lambda: game.change_scene("menu"))

    def on_enter(self):
        self.game.reproducir_musica("game_over", loops=-1, volume=0.4)

    def on_exit(self):
        self.game.detener_musica()

class VictoryScene(FinScene):
    TEXTO = "¡VICTORIA!"
    COLOR = (44, 120, 66)

    def __init__(self, game, nivel=0):
        super().__init__(game, nivel)
        y = 300
        if nivel + 1 < len(NIVELES):
            self.subtitulo = "¡Nivel superado!"
            self._boton(y, "Siguiente nivel", lambda: game.change_scene("juego", nivel=self.nivel + 1))
            y += 70
        else:
            self.subtitulo = "¡Completaste todos los niveles!"
        self._boton(y, "Volver al menú", lambda: game.change_scene("menu"))
