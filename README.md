# Make a Bridge — Constructor de puentes con físicas 2D (Pygame + Pymunk)

Construí un puente con vigas unidas por articulaciones para que un gato lo cruce caminando hasta la bandera.
Cada material pesa, cuesta y resiste distinto: si una viga soporta más fuerza de la que aguanta, se rompe.

## Documentación de la entrega
- [Documento de diseño](DISENO.md): decisiones de jugabilidad y mecánicas implementadas.
- [Lista de assets](ASSETS.md): qué se usó y de dónde se obtuvo.
- Video de demostración: se encuentra dentro de la carpeta raíz.

## Instalación
1. Clonar el repositorio (incluye la carpeta `engine/` del curso junto a `MakeABridge/`).
2. (Opcional) crear un entorno virtual: `python -m venv venv` y activarlo.
3. Instalar dependencias: `pip install -r requirements.txt`

## Ejecución
Desde la carpeta raíz del repositorio:

    python -m MakeABridge.main

## Cómo se juega
Al tocar «Comenzar Juego» aparece una pantalla de Instrucciones; desde ahí se pasa al juego.

1. **Construcción**: elegí un material y arrastrá con el mouse desde un nodo (los puntos naranjas son anclajes fijos)
   hasta otro punto para crear una viga. Hay un presupuesto limitado.
   - `1` a `5`: material · arrastrar: crear viga · clic derecho: borrar · `Z`: deshacer · `ESC`: menú.
2. **Prueba** (botón «¡Probar!»): se activa la física y el gato camina hacia la bandera. Las vigas pasan de verde a rojo
   según su esfuerzo. Hay 5 intentos por nivel.

Materiales: camino, camino reforzado, madera, acero y cable (solo resiste tracción). Para que el puente aguante hay que triangular.

## Niveles
1. El primer puente · 2. El valle ancho · 3. El abismo

## Estructura
    engine/        motor hecho en clase
    MakeABridge/   el juego (escenas, física del puente, estilo y assets)
    VideoMuestra/ video corto de la jugabilidad
