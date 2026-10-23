# MakeABridge/physics_world.py
import pymunk
from .settings import GRAVEDAD, SUBPASOS


class MundoFisico:
    """Envuelve el pymunk.Space. Avanza la simulación en varios subpasos por frame."""

    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = GRAVEDAD
        self.space.iterations = 40        # más iteraciones = uniones más rígidas

    def step(self, dt, subpasos=SUBPASOS, antes=None, despues=None):
        h = dt / subpasos
        for _ in range(subpasos):
            if antes:
                antes()
            self.space.step(h)
            if despues:
                despues(h)
