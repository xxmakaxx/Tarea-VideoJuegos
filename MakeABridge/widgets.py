# fisicas2d/widgets.py
import pygame
from engine.ui import Button
from . import estilo


class SoundButton(Button):
    """Button del motor con retorno de sonido al hacer click (requisito común de la tarea)."""

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
