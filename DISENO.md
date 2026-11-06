# Documento de diseño — Make a Bridge

**Opción 3 · Juego con físicas 2D (Pygame + Pymunk)** · Tarea TVJ2D 2026

## 1. Idea general

*Make a Bridge* es un constructor de puentes inspirado en Poly Bridge. El jugador arma, con vigas de distintos
materiales, un puente entre dos acantilados para que un gato lo cruce caminando hasta la bandera. El puente no es
un dibujo: está hecho de cuerpos rígidos unidos por articulaciones, así que cada decisión de construcción
(dónde triangular, qué material usar, cuánto gastar) tiene una consecuencia física real.

**Objetivo del jugador:** que el gato llegue a la bandera sin que el puente se rompa, gastando como máximo el presupuesto del nivel.

## 2. Bucle de juego

Cada nivel tiene tres fases (`GameScene`):

1. **Construcción** — la física está en pausa. El jugador arrastra con el mouse desde un nodo hasta otro punto para crear una
   viga. Se ve el costo y si la posición es válida (verde/rojo) antes de soltar.
2. **Prueba** — al presionar «¡Probar!» se crea el mundo físico, el gato espera 0,8 s y empieza a caminar. Las vigas se
   colorean de verde a rojo según su esfuerzo.
3. **Resultado** — éxito (pasa al siguiente nivel) o fallo (vuelve a construir y descuenta un intento). Con 0 intentos, Game Over.

Escenas: Menú → Instrucciones → Juego (3 niveles) → Victoria / Game Over.

## 3. Mecánicas implementadas

**Construcción**
- Grilla de 20 px (= 1 metro): los nodos nuevos se ajustan a la grilla y se enganchan a nodos existentes cercanos.
- Los **anclajes fijos** (puntos naranjas) están en los acantilados y pilares; son los únicos puntos que no se mueven.
- Validaciones al crear una viga: posición válida, largo mínimo y máximo según material, que no atraviese el terreno,
  que no esté duplicada y que alcance el presupuesto.
- Clic derecho borra una viga o un nodo (con sus vigas), `Z` deshace, «Limpiar» borra todo.
- Antes de probar se comprueba que exista un **camino continuo** de un acantilado al otro; si hay un hueco se explica
  dónde y **no gasta intento**.

**Materiales** (precio por metro; la resistencia es la fuerza máxima antes de romperse)

| Material | Precio/m | Resistencia | Se camina | Notas |
|---|---|---|---|---|
| Camino | $120 | 25 000 | Sí | Base del puente; es lo único que pisa el gato |
| Camino reforzado | $240 | 50 000 | Sí | Más pesado y resistente |
| Madera | $80 | 45 000 | No | Viga estructural barata y liviana |
| Acero | $200 | 90 000 | No | La más resistente |
| Cable | $40 | 60 000 | No | Largo hasta 13 m; solo resiste tracción |

**Física (Pymunk)**
- Cada viga es un cuerpo con masa proporcional a su largo y densidad; los extremos se unen con `PivotJoint` (articulaciones),
  por eso hay que **triangular** para que la estructura sea rígida.
- El **cable** usa `SlideJoint`: puede tensarse pero no empuja, como un cable real.
- Después de cada subpaso se mide el impulso de cada unión; si una viga supera su resistencia durante 8 subpasos
  seguidos, se rompe (se elimina la unión y cae). El esfuerzo se suaviza para el color y no por un pico instantáneo.
- Se simulan 4 subpasos por frame y 40 iteraciones del solver para que las estructuras sean estables.
- Las vigas que no son camino no colisionan con nada (filtros de colisión), así el gato solo interactúa con el camino y el terreno.

**El gato** es un `PhysicsObject` del motor con cápsula que no rota, masa propia por nivel y velocidad horizontal objetivo constante:
camina, **no es lanzado**. Falla si cae al valle, queda trabado 2 s o supera 45 s.

## 4. Niveles y dificultad

| Nivel | Luz entre acantilados | Obstáculos | Presupuesto | Masa del gato |
|---|---|---|---|---|
| 1. El primer puente | 15 m | — | $10 000 | 6 |
| 2. El valle ancho | 21 m | pilar central | $15 000 | 8 |
| 3. El abismo | 24 m | pilar angosto + desnivel de 2 m | $20 000 | 10 |

La dificultad sube por tres vías: tramos más largos, un gato más pesado (más carga) y terreno más complejo
(pilares y desnivel). El presupuesto crece muy poco, así que hay que elegir materiales con criterio.
Cada nivel da 5 intentos.

## 5. Decisiones de jugabilidad

- **Construir y probar por separado** para que el jugador pueda pensar sin presión y la física solo corra cuando decide probar.
- **Retroalimentación visual del esfuerzo** (verde → amarillo → rojo): enseña qué parte falla y qué reforzar sin explicar física.
- **Intentos limitados** para que probar no sea gratis, pero los errores de construcción evitables (huecos) no penalizan.
- **Camino separado de la estructura**: obliga a pensar en dos capas, la superficie por donde se camina y el esqueleto que la sostiene.
- **Muñeco que camina** en vez de proyectiles: el desafío es el equilibrio y la distribución de cargas.
- **Estilo visual** pixel art de 8 bits con fondo en parallax (nubes y colinas con pinos en movimiento) y fuente arcade (Press Start 2P).
- **Sonido** en cada acción: clic, colocar viga, romper, éxito, y música en el menú y en Game Over.

## 6. Arquitectura

El juego hereda del motor hecho en clase (`engine/`): `Game` y `Scene` (bucle y escenas), `PhysicsObject` y `GameObject`
(objetos), `AudioManager`, `AssetManager`, `ParallaxBackground`, `Button` y `DialogueManager`.

```
MakeABridge/
  main.py, game.py        punto de entrada y Game con las escenas
  settings.py             constantes: física, materiales, niveles
  physics_world.py        envoltorio del Space de Pymunk con subpasos
  puente.py               Nodo, Viga y conversión a física + detección de roturas
  entities.py             Suelo, Plataforma, Caminante (gato)
  fondo.py, estilo.py     fondo parallax y gráficos procedurales
  widgets.py              botón con sonido
  scenes/                 menú, instrucciones, juego, victoria y game over
```
