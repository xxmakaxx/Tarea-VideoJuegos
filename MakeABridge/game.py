# MakeABridge/game.py
import os
from engine.game_loop import Game
from engine.asset_manager import AssetManager
from engine.audio import AudioManager
from .settings import ANCHO, ALTO, FPS, TITULO, ASSETS_DIR
from .scenes.menu_scene import MenuScene
from .scenes.instrucciones_scene import InstruccionesScene
from .scenes.game_scene import GameScene
from .scenes.end_scenes import GameOverScene, VictoryScene


class FisicasGame(Game):
    """Hereda de Game (GameLoop + gestor de escenas) del motor."""

    def __init__(self):
        super().__init__(ANCHO, ALTO, TITULO, FPS)
        self.assets = AssetManager()
        self.audio = AudioManager()
        for nombre in ("click", "colocar", "romper", "exito"):
            ruta = os.path.join(ASSETS_DIR, "sounds", f"{nombre}.wav")
            if os.path.exists(ruta):
                self.audio.load_sound(nombre, ruta)
            else:
                print(f"[aviso] falta el sonido {ruta}")
        self.musicas = {}
        for nombre in ("menu", "game_over"):
            ruta = self._buscar_audio(nombre)
            if ruta:
                self.musicas[nombre] = ruta
            else: 
                print(f"[aviso] falta la música '{nombre}' en {os.path.join(ASSETS_DIR, 'sounds')}")

        self.add_scene("menu", MenuScene)
        self.add_scene("instrucciones", InstruccionesScene)
        self.add_scene("juego", GameScene)        # se instancia de nuevo cada vez: reinicia el nivel
        self.add_scene("game_over", GameOverScene)
        self.add_scene("victoria", VictoryScene)
        self.change_scene("menu")

    def reproducir(self, nombre):
        self.audio.play_sound(nombre)

    @staticmethod
    def _buscar_audio(nombre):
        for ext in (".wav", ".ogg", ".mp3"):
            ruta = os.path.join(ASSETS_DIR, "sounds", nombre + ext)
            if os.path.exists(ruta):
                return ruta
        return None

    def reproducir_musica(self, nombre, loops=-1, volume=0.5):
        ruta = self.musicas.get(nombre)
        if ruta:
            self.audio.load_music(ruta)
            self.audio.play_music(loops=loops, volume=volume)

    def detener_musica(self):
        self.audio.stop_music()

    def salir(self):
        self.running = False
