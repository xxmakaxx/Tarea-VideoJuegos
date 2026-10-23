# fisicas2d/scenes/menu_scene.py
import pygame
from engine.ui import Scene
from ..widgets import SoundButton
from ..fondo import crear_fondo
from .. import estilo
from ..settings import ANCHO, TITULO


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.fondo = crear_fondo()
        self.fuente_titulo = estilo.fuente_arcade(52)
        self.fuente_sub = estilo.fuente_arcade(14)
        cx = ANCHO // 2
        audio = game.audio
        self.botones = [
            SoundButton(cx - 160, 300, 320, 60, "Comenzar Juego",
                        lambda: game.change_scene("instrucciones"), audio),
            SoundButton(cx - 160, 380, 320, 60, "Salir", game.salir, audio),
        ]

    def on_enter(self):
        # La música sigue sonando en las instrucciones: solo arranca si no estaba sonando.
        try:
            sonando = pygame.mixer.music.get_busy()
        except pygame.error:
            sonando = False
        if not sonando:
            self.game.reproducir_musica("menu", volume=0.4)

    def handle_events(self, events):
        for e in events:
            for b in self.botones:
                b.handle_event(e)

    def update(self):
        self.fondo.update(1)

    def draw(self, surface):
        self.fondo.draw(surface)
        centro = (ANCHO // 2, 170)
        sombra = self.fuente_titulo.render(TITULO, True, (255, 250, 235))
        titulo = self.fuente_titulo.render(TITULO, True, estilo.TINTA)
        surface.blit(sombra, sombra.get_rect(center=(centro[0] + 4, centro[1] + 4)))
        surface.blit(titulo, titulo.get_rect(center=centro))
        sub = self.fuente_sub.render("Build your own bridge", True, estilo.TINTA)
        surface.blit(sub, sub.get_rect(center=(ANCHO // 2, 240)))
        for b in self.botones:
            b.draw(surface)
