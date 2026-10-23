# Cruce Seguro — Constructor de puentes con físicas 2D (Pygame + Pymunk)

Construí un puente de verdad, con vigas unidas por articulaciones, para que un muñeco lo cruce caminando.
Cada material pesa, cuesta y resiste distinto: si una viga soporta más fuerza de la que aguanta, se rompe.

## Instalación
1. Clonar el repositorio (debe incluir la carpeta `engine/` del curso junto a `MakeABridge/`).
2. (Opcional) crear un entorno virtual: `python -m venv venv` y activarlo.
3. Instalar dependencias: `pip install -r requirements.txt`

## Ejecución
Desde la carpeta raíz del repositorio:

    python -m MakeABridge.main

## Cómo se juega
Al tocar "Comenzar Juego" aparece una pantalla de **Instrucciones** con todo lo necesario; desde ahí se pasa al juego.

Cada nivel tiene dos fases:

1. **Construcción**: elegí un material y arrastrá con el mouse desde un nodo (los puntos naranjas son anclajes
   fijos en el terreno) hasta otro punto para crear una viga. Cada viga cuesta según su largo y su material,
   y tenés un presupuesto limitado.
   - `1` a `5`: material · arrastrar: crear viga · clic derecho: borrar · `Z`: deshacer.
2. **Prueba** (botón "¡Probar!"): se activa la física y el muñeco empieza a caminar hacia la bandera.
   Las vigas se colorean según su esfuerzo (verde = tranquila, rojo = a punto de romperse).

Materiales: camino (se puede caminar), camino reforzado, madera, acero y cable (solo resiste tracción).
Para que el puente aguante hay que triangular la estructura. Tenés 5 pruebas por nivel; `ESC` vuelve al menú.

## Niveles
1. El primer puente: un tramo corto.
2. El valle ancho: un tramo más largo, con un pilar en el medio y un muñeco más pesado.
3. El abismo: el tramo más largo, con desnivel entre los acantilados y el muñeco más pesado.

## Mecánicas físicas
- Las vigas son cuerpos rígidos de Pymunk unidos por articulaciones (PivotJoint); los cables usan SlideJoint.
- La fuerza de cada unión se mide en cada paso de la simulación y la viga se rompe si supera su resistencia.
- El muñeco es un cuerpo con masa propia que camina sobre las vigas de tipo camino.

## Assets
(Completar: lista de assets y de dónde se obtuvieron. Los gráficos son procedurales, generados con Pygame
en `MakeABridge/estilo.py`. Sonidos esperados en `MakeABridge/assets/sounds/`: click, colocar, romper, exito, y la música del menú `menu.wav`.
Fuente: Press Start 2P (Google Fonts, licencia SIL OFL; texto en `assets/fonts/PressStart2P-OFL.txt`).)
