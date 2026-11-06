# MakeABridge/entities.py
import pygame
import pymunk
from engine.physics_object import PhysicsObject, add_static_segment, COLLISION_PLAYER, COLLISION_WALL
from engine.game_object import GameObject
from . import estilo
from .settings import (SUELO_Y, ANCHO, ALTO, VEL_CAMINANTE, CAT_CAMINANTE, CAT_CAMINO, CAT_TERRENO,
                       PERSONAJE)

HIERBA = 14   # px de pasto que sobresalen por encima de la superficie


class Suelo(GameObject):
    """Fondo del valle."""

    def __init__(self, mundo):
        imagen = estilo.textura_suelo(ANCHO, ALTO - SUELO_Y, HIERBA)
        super().__init__(ANCHO // 2, SUELO_Y - HIERBA + imagen.get_height() // 2, imagen)
        self.shape = add_static_segment(mundo.space, (0, SUELO_Y + 5), (ANCHO, SUELO_Y + 5),
                                        thickness=5, elasticity=0.0, friction=1.0,
                                        collision_type=COLLISION_WALL)
        self.shape.filter = pymunk.ShapeFilter(categories=CAT_TERRENO, mask=CAT_CAMINANTE)


class Plataforma(GameObject):
    #Terreno fijo (acantilado o pilar del valle): imagen de tierra con pasto + polígono estático de Pymunk

    def __init__(self, mundo, x, top, ancho, alto):
        imagen = estilo.textura_suelo(ancho, alto, HIERBA)
        super().__init__(x + ancho // 2, top - HIERBA + imagen.get_height() // 2, imagen)
        self.rect_fisico = pygame.Rect(x, top, ancho, alto)
        vertices = [(x, top), (x + ancho, top), (x + ancho, top + alto), (x, top + alto)]
        self.shape = pymunk.Poly(mundo.space.static_body, vertices)
        self.shape.friction = 1.0
        self.shape.elasticity = 0.0
        self.shape.collision_type = COLLISION_WALL
        self.shape.filter = pymunk.ShapeFilter(categories=CAT_TERRENO, mask=CAT_CAMINANTE)
        mundo.space.add(self.shape)


class Caminante(PhysicsObject):
    #El gato que cruza el puente. Es un PhysicsObject del motor con una cápsula que no rota,
    #y camina hacia la derecha empujándose con una velocidad objetivo (no es lanzado.
    if PERSONAJE == "gato":
        PUNTOS, RADIO = ((-9, 0), (9, 0)), 9
    else:
        PUNTOS, RADIO = ((0, -10), (0, 10)), 11
    ALTO_MEDIO = RADIO + max(abs(p[1]) for p in PUNTOS)     # del centro a los pies

    def __init__(self, mundo, x, y, masa):
        frames = estilo.frames_caminante()
        super().__init__(x, y, frames[0], mundo.space, mass=masa, shape="box",
                         elasticity=0.0, friction=0.5, collision_type=COLLISION_PLAYER)
        self.frames_marcha = frames
        self.activo = False
        # La caja que crea el motor se reemplaza por una cápsula (desliza mejor sobre las uniones)
        mundo.space.remove(self.body, self.shape)
        self.body.moment = float("inf")            # no rota: siempre de pie
        self.shape = pymunk.Segment(self.body, self.PUNTOS[0], self.PUNTOS[1], self.RADIO)
        self.shape.friction = 0.5
        self.shape.elasticity = 0.0
        self.shape.collision_type = COLLISION_PLAYER
        self.shape.filter = pymunk.ShapeFilter(categories=CAT_CAMINANTE, mask=CAT_CAMINO | CAT_TERRENO)
        self.shape.parent = self
        mundo.space.add(self.body, self.shape)

    def controlar(self):
        #Se llama antes de cada subpaso de física.
        if self.activo:
            self.body.velocity = (VEL_CAMINANTE, self.body.velocity.y)

    def update(self, *args, **kwargs):
        if self.activo:
            idx = int(self.body.position.x / 9) % len(self.frames_marcha)
        else:
            idx = 0
        self.original_image = self.frames_marcha[idx]
        self.update_from_physics()
