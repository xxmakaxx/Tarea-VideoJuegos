# engine/utils/load_sprites.py
# Helper para leer animaciones exportadas desde Piskel.

import json


def load_piskel_animation(json_path):
    """Devuelve (lista_de_rects, nombre_de_imagen) de un JSON de Piskel."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    frames = []
    for frame_data in data["frames"].values():
        rect = frame_data["frame"]
        frames.append((rect["x"], rect["y"], rect["w"], rect["h"]))
    return frames, data["meta"]["image"]
