# fisicas2d/scenes/game_scene.py
import pygame
from engine.ui import Scene
from engine.dialogue_manager import DialogueManager
from ..settings import (ANCHO, ALTO, FPS, SUELO_Y, GRID, PANEL_H, ANCLA_RADIO, INTENTOS, META_X, INICIO_X,
                        RETRASO_INICIO, TIEMPO_MAX, SUBPASOS, VIGAS, NIVELES, ESPERA_VICTORIA, ESPERA_FALLO,
                        DEBUG)
from ..physics_world import MundoFisico
from ..fondo import crear_fondo
from .. import estilo
from ..widgets import SoundButton
from ..entities import Suelo, Plataforma, Caminante
from ..puente import Nodo, Viga, construir_fisica, revisar_roturas

MATERIALES_ORDEN = list(VIGAS.keys())
COLOR_BOTON = (120, 82, 46)
COLOR_BOTON_SEL = (176, 128, 70)


class GameScene(Scene):
    """
    Constructor de puentes (estilo Poly Bridge). Fases:
      construccion -> el jugador arma nodos y vigas dentro del presupuesto (física en pausa)
      prueba       -> la física corre y el muñeco camina por el puente; las vigas se rompen si se sobrecargan
      resultado    -> breve pausa mostrando éxito o desplome
    """

    def __init__(self, game, nivel=0):
        super().__init__(game)
        self.nivel = nivel
        self.datos = NIVELES[nivel]
        self.fondo = crear_fondo()
        self.fuente = estilo.fuente_arcade(12)
        self.fuente_chica = estilo.fuente_arcade(10)
        self.dialogos = DialogueManager(game.screen, 44, color=estilo.TINTA)
        self.dialogos.font = estilo.fuente_arcade(14)
        self.img_meta = estilo.textura_meta()
        self.img_quieto = estilo.frames_caminante()[0]

        d = self.datos
        self.inicio = pygame.Vector2(INICIO_X, d["top_izq"] - Caminante.ALTO_MEDIO - 1)
        self.meta_rect = pygame.Rect(META_X - 25, d["top_der"] - 80, 50, 80)
        self.rects_terreno = [pygame.Rect(0, d["top_izq"], d["izq"], ALTO - d["top_izq"]),
                              pygame.Rect(d["der"], d["top_der"], ANCHO - d["der"], ALTO - d["top_der"])]
        for cx, top, ancho in d["pilares"]:
            self.rects_terreno.append(pygame.Rect(cx - ancho // 2, top, ancho, ALTO - top))

        self.intentos = INTENTOS
        self.nodos, self.vigas = [], []
        self._crear_anclas()
        self.material = MATERIALES_ORDEN[0]
        self.arrastre = None            # nodo desde el que se está arrastrando una viga
        self.fase = "construccion"
        self.resultado = None
        self.t_resultado = 0
        self.t_sim = 0.0
        self.t_quieto = 0.0
        self.hubo_rotura = False       # ya sonó 'romper' en esta prueba
        self.caminante = None
        self.grilla = self._crear_grilla()

        self._crear_botones()
        self._montar()
        self.dialogos.show_message(f"Nivel {nivel + 1}: {d['nombre']}", 3, "center")

    def on_enter(self):
        self.game.audio.stop_music()       # la música es del menú

    # ---------------------------------------------------------------- mundo
    def _montar(self):
        """(Re)crea el mundo físico limpio: terreno + muñeco. El diseño del jugador se conserva."""
        d = self.datos
        self.mundo = MundoFisico()
        self.terreno = pygame.sprite.Group()
        self.actores = pygame.sprite.Group()
        self.caminante = None
        self.arrastre = None
        self.terreno.add(Suelo(self.mundo))
        self.terreno.add(Plataforma(self.mundo, 0, d["top_izq"], d["izq"], ALTO - d["top_izq"]))
        self.terreno.add(Plataforma(self.mundo, d["der"], d["top_der"], ANCHO - d["der"], ALTO - d["top_der"]))
        for cx, top, ancho in d["pilares"]:
            self.terreno.add(Plataforma(self.mundo, cx - ancho // 2, top, ancho, ALTO - top))
        for n in self.nodos:
            n.body = None
        for v in self.vigas:
            v.reiniciar()

    def _crear_anclas(self):
        """Anclajes fijos: bordes y caras de los acantilados y la parte superior de los pilares."""
        d = self.datos
        pts = []
        for x, top in ((d["izq"], d["top_izq"]), (d["der"], d["top_der"])):
            y = top + 5
            while y <= SUELO_Y - 40:
                pts.append((x, y))
                y += 40
        for cx, top, ancho in d["pilares"]:
            pts += [(cx - ancho // 2, top), (cx, top), (cx + ancho // 2, top)]
        for p in pts:
            self.nodos.append(Nodo(p[0], p[1], fijo=True))

    def _crear_grilla(self):
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        for x in range(0, ANCHO, GRID):
            for y in range(PANEL_H, SUELO_Y, GRID):
                if not any(r.collidepoint(x, y) for r in self.rects_terreno):
                    s.fill((90, 70, 50, 70), (x - 1, y - 1, 2, 2))
        return s

    # ------------------------------------------------------- construcción
    @property
    def gastado(self):
        return sum(v.costo for v in self.vigas)

    @property
    def restante(self):
        return self.datos["presupuesto"] - self.gastado

    @staticmethod
    def _snap(p):
        return pygame.Vector2(round(p[0] / GRID) * GRID, round(p[1] / GRID) * GRID)

    def _nodo_cerca(self, pos, radio=ANCLA_RADIO):
        mejor, mejor_d = None, radio
        for n in self.nodos:
            dist = n.pos.distance_to(pos)
            if dist <= mejor_d:
                mejor, mejor_d = n, dist
        return mejor

    def _en_terreno(self, p):
        return any(r.inflate(-4, -4).collidepoint(p) for r in self.rects_terreno)

    def _evaluar(self, origen, pos_fin, material, snap=True):
        """Devuelve (ok, destino_nodo, destino_pos, motivo) para una viga desde 'origen' hasta 'pos_fin'."""
        pos_fin = pygame.Vector2(pos_fin)
        destino = self._nodo_cerca(pos_fin)
        if destino is not None:
            pto = destino.pos
        else:
            pto = self._snap(pos_fin) if snap else pos_fin
            if pto.y < PANEL_H or pto.y > SUELO_Y - 5 or not (0 <= pto.x <= ANCHO) or self._en_terreno(pto):
                return False, None, pto, "posición inválida"
        if destino is origen:
            return False, None, pto, "sin longitud"
        datos = VIGAS[material]
        largo = origen.pos.distance_to(pto)
        if largo < 15:
            return False, None, pto, "muy corta"
        if largo > datos["max_largo"] + 0.5:
            return False, None, pto, f"muy larga (máx. {datos['max_largo'] // GRID} m)"
        if any(r.inflate(-4, -4).clipline(origen.pos, pto) for r in self.rects_terreno):
            return False, None, pto, "atraviesa el terreno"
        if destino is not None and any({v.a, v.b} == {origen, destino} for v in self.vigas):
            return False, None, pto, "ya existe esa unión"
        costo = int(round(largo / GRID * datos["precio"]))
        if costo > self.restante:
            return False, None, pto, "presupuesto insuficiente"
        return True, destino, pto, f"${costo}"

    def agregar_viga(self, origen, pos_fin, material, snap=True):
        """Crea una viga (y el nodo final si no existía). Devuelve (ok, motivo)."""
        ok, destino, pto, motivo = self._evaluar(origen, pos_fin, material, snap)
        if not ok:
            return False, motivo
        if destino is None:
            destino = Nodo(pto.x, pto.y)
            self.nodos.append(destino)
        self.vigas.append(Viga(origen, destino, material))
        return True, motivo

    def _limpiar_huerfanos(self):
        usados = {n for v in self.vigas for n in (v.a, v.b)}
        self.nodos = [n for n in self.nodos if n.fijo or n in usados]

    def _borrar_en(self, pos):
        pos = pygame.Vector2(pos)
        for n in self.nodos:
            if not n.fijo and n.pos.distance_to(pos) <= 10:
                self.vigas = [v for v in self.vigas if n not in (v.a, v.b)]
                self._limpiar_huerfanos()
                return True
        candidatas = [(v.distancia_a(pos), v) for v in self.vigas]
        candidatas = [c for c in candidatas if c[0] <= 8]
        if candidatas:
            self.vigas.remove(min(candidatas, key=lambda c: c[0])[1])
            self._limpiar_huerfanos()
            return True
        return False

    def _deshacer(self):
        if self.vigas:
            self.vigas.pop()
            self._limpiar_huerfanos()

    def _limpiar_todo(self):
        self.vigas = []
        self._limpiar_huerfanos()

    # ------------------------------------------------------------ interfaz
    def _crear_botones(self):
        audio = self.game.audio
        self.botones_mat = []
        x = 20
        for mat in MATERIALES_ORDEN:
            d = VIGAS[mat]
            b = SoundButton(x, 84, 150, 34, f"{d['nombre']} ${d['precio']}",
                            lambda m=mat: self._elegir(m), audio, font_size=22)
            self.botones_mat.append(b)
            x += 156
        self.btn_probar = SoundButton(20, 124, 190, 34, "¡Probar!", self._probar, audio, font_size=26)
        self.btn_limpiar = SoundButton(220, 124, 170, 34, "Limpiar", self._limpiar_todo, audio, font_size=26)
        self.btn_volver = SoundButton(20, 124, 300, 34, "Volver a construir", self._volver_a_construir,
                                      audio, font_size=26)

    def _botones_activos(self):
        if self.fase == "construccion":
            return self.botones_mat + [self.btn_probar, self.btn_limpiar]
        if self.fase == "prueba":
            return [self.btn_volver]
        return []

    def _elegir(self, mat):
        self.material = mat

    def _camino_continuo(self):
        """Comprueba que haya un camino pisable de un acantilado al otro. Devuelve (ok, mensaje)."""
        d = self.datos
        def ancla(x, top):
            for n in self.nodos:
                if n.fijo and abs(n.pos.x - x) < 1 and abs(n.pos.y - (top + 5)) < 1:
                    return n
        inicio, fin = ancla(d["izq"], d["top_izq"]), ancla(d["der"], d["top_der"])
        vecinos = {}
        for v in self.vigas:
            if v.datos["camina"]:
                vecinos.setdefault(v.a, []).append(v.b)
                vecinos.setdefault(v.b, []).append(v.a)
        if not vecinos:
            return False, "No hay Camino: el gato solo pisa vigas de Camino"
        if inicio not in vecinos:
            return False, "El Camino debe empezar en el ancla de arriba (izquierda)"
        if fin not in vecinos:
            return False, "El Camino debe terminar en el ancla de arriba (derecha)"
        visto, pila = {inicio}, [inicio]
        while pila:
            for m in vecinos.get(pila.pop(), []):
                if m not in visto:
                    visto.add(m)
                    pila.append(m)
        if fin not in visto:
            return False, "Hay un hueco en el Camino: unilo de lado a lado"
        return True, ""

    def _probar(self):
        if not self.vigas:
            self.dialogos.show_message("¡Construí algo primero!", 2, "center")
            return
        if self.intentos <= 0:
            return
        ok, mensaje = self._camino_continuo()
        if not ok:
            self.dialogos.show_message(mensaje, 4, "center")      # no cuenta como intento
            self.game.reproducir("click")
            return
        self._montar()
        construir_fisica(self.mundo, self.nodos, self.vigas)
        self.caminante = Caminante(self.mundo, self.inicio.x, self.inicio.y, self.datos["masa_caminante"])
        self.actores.add(self.caminante)
        self.t_sim = 0.0
        self.t_quieto = 0.0
        self.hubo_rotura = False
        self.fase = "prueba"
        self.intentos -= 1

    def _volver_a_construir(self):
        if self.fase == "prueba" and self.t_sim < RETRASO_INICIO:
            self.intentos += 1                      # no empezó a caminar: no cuenta como intento
        elif self.intentos <= 0:
            self.game.change_scene("game_over", nivel=self.nivel)
            return
        self._montar()
        self.fase = "construccion"

    # --------------------------------------------------------------- input
    def handle_events(self, events):
        for e in events:
            for b in self._botones_activos():
                b.handle_event(e)

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.game.change_scene("menu")
                elif self.fase == "construccion":
                    if pygame.K_1 <= e.key < pygame.K_1 + len(MATERIALES_ORDEN):
                        self.material = MATERIALES_ORDEN[e.key - pygame.K_1]
                    elif e.key == pygame.K_z:
                        self._deshacer()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.pos[1] >= PANEL_H and self.fase == "construccion":
                if e.button == 1:
                    self.arrastre = self._nodo_cerca(e.pos)
                elif e.button == 3:
                    if self._borrar_en(e.pos):
                        self.game.reproducir("click")
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.arrastre is not None:
                origen, self.arrastre = self.arrastre, None
                if self.fase == "construccion":
                    ok, motivo = self.agregar_viga(origen, e.pos, self.material)
                    if ok:
                        self.game.reproducir("colocar")
                    if not ok and e.pos[1] >= PANEL_H:
                        self.dialogos.show_message(motivo.capitalize(), 1.2, "center")

    # --------------------------------------------------------------- lógica
    def _terminar(self, resultado, motivo=""):
        self.fase = "resultado"
        self.resultado = resultado
        self.t_resultado = pygame.time.get_ticks()
        if resultado == "exito":
            if self.caminante:
                self.caminante.activo = False
            self.dialogos.show_message("¡Cruzó! El puente aguantó", 2.5, "center")
            self.game.reproducir("exito")
        else:
            if motivo == "tiempo":
                texto = "¡No llegó a tiempo!"
            elif self.hubo_rotura:
                texto = "¡El puente no resistió!"
            else:
                texto = "El gato no pudo cruzar: revisá huecos o escalones"
            self.dialogos.show_message(texto, 2.5, "center")
            if motivo == "cayó" and not self.hubo_rotura:
                self.game.reproducir("romper")      # el puente no se rompió pero no sostuvo al gato
        if DEBUG:
            rotas = sum(1 for v in self.vigas if v.rota)
            pos = self.caminante.body.position if self.caminante else (0, 0)
            print(f"[nivel {self.nivel + 1}] {resultado} {motivo} | vigas rotas: {rotas} | "
                  f"gato en x={pos[0]:.0f} y={pos[1]:.0f} | intentos restantes: {self.intentos}")

    def _despues_de_paso(self, h):
        rotas_antes = sum(v.rota for v in self.vigas)
        revisar_roturas(self.mundo, self.vigas, h)
        if self.fase == "prueba" and not self.hubo_rotura and sum(v.rota for v in self.vigas) > rotas_antes:
            self.hubo_rotura = True
            self.game.reproducir("romper")

    def update(self):
        self.fondo.update(1)
        self.dialogos.update()

        if self.fase in ("prueba", "resultado"):
            if self.fase == "prueba":
                self.caminante.activo = self.t_sim > RETRASO_INICIO
            self.mundo.step(1 / FPS, SUBPASOS, antes=self.caminante.controlar, despues=self._despues_de_paso)
            self.t_sim += 1 / FPS
            self.terreno.update()
            self.actores.update()

        ahora = pygame.time.get_ticks()
        if self.fase == "prueba":
            pos = self.caminante.body.position
            vx = self.caminante.body.velocity.x
            self.t_quieto = self.t_quieto + 1 / FPS if (self.caminante.activo and vx < 10) else 0.0
            if self.meta_rect.collidepoint(pos):
                self._terminar("exito")
            elif pos.y > SUELO_Y - 25 or pos.x < -60 or pos.x > ANCHO + 60:
                self._terminar("fallo", "cayó")
            elif self.t_quieto > 2.0:
                self._terminar("fallo", "atascado")
            elif self.t_sim > TIEMPO_MAX:
                self._terminar("fallo", "tiempo")

        elif self.fase == "resultado":
            if self.resultado == "exito" and ahora - self.t_resultado > ESPERA_VICTORIA:
                if self.nivel + 1 < len(NIVELES):
                    self.game.change_scene("juego", nivel=self.nivel + 1)
                else:
                    self.game.change_scene("victoria", nivel=self.nivel)
            elif self.resultado == "fallo" and ahora - self.t_resultado > ESPERA_FALLO:
                if self.intentos > 0:
                    self._montar()
                    self.fase = "construccion"
                    self.dialogos.show_message(f"Reforzá el puente. Intentos: {self.intentos}", 2.5, "center")
                else:
                    self.game.change_scene("game_over", nivel=self.nivel)

    # --------------------------------------------------------------- dibujo
    def _dibujar_vista_previa(self, surface):
        if self.arrastre is None:
            return
        mp = pygame.mouse.get_pos()
        ok, destino, pto, motivo = self._evaluar(self.arrastre, mp, self.material)
        color = (60, 200, 90) if ok else (220, 60, 50)
        pygame.draw.line(surface, color, self.arrastre.pos, pto, max(3, VIGAS[self.material]["grosor"]))
        pygame.draw.circle(surface, color, (int(pto.x), int(pto.y)), 6, 2)
        t = self.fuente_chica.render(motivo, True, estilo.TINTA)
        surface.blit(t, (pto.x + 10, pto.y - 24))

    def draw(self, surface):
        simulando = self.fase != "construccion"
        self.fondo.draw(surface)
        self.terreno.draw(surface)
        surface.blit(self.img_meta, self.meta_rect.topleft)
        if self.fase == "construccion":
            surface.blit(self.grilla, (0, 0))

        orden = {"cable": 0, "madera": 1, "acero": 1, "camino": 2, "camino_reforzado": 2}
        for v in sorted(self.vigas, key=lambda v: orden[v.material]):
            v.dibujar(surface, simulando)
        for n in self.nodos:
            n.dibujar(surface)

        if self.caminante is not None:
            self.actores.draw(surface)
        else:
            surface.blit(self.img_quieto, self.img_quieto.get_rect(center=self.inicio))
        self._dibujar_vista_previa(surface)

        t1 = self.fuente.render(f"Nivel {self.nivel + 1}/{len(NIVELES)}: {self.datos['nombre']}", True, estilo.TINTA)
        t2 = self.fuente.render(f"Presupuesto: ${self.restante}  Intentos: {self.intentos}", True, estilo.TINTA)
        surface.blit(t1, (20, 46))
        surface.blit(t2, (ANCHO - 20 - t2.get_width(), 46))

        for b in self.botones_mat:
            b.color = COLOR_BOTON_SEL if MATERIALES_ORDEN[self.botones_mat.index(b)] == self.material else COLOR_BOTON
        for b in self._botones_activos():
            b.draw(surface)
        self.dialogos.draw()
