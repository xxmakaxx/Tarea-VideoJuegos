# Assets utilizados — Make a Bridge

## Gráficos
Todos los gráficos son **procedurales**: se generan por código con Pygame en `MakeABridge/estilo.py`, `MakeABridge/fondo.py`
y `MakeABridge/puente.py`. No se usaron imágenes ni sprites externos.

| Elemento | Dónde se genera |
|---|---|
| Fondo (papel, grano, nubes y colinas en parallax) | `fondo.py`, `estilo.py` |
| Terreno (tierra con pasto) y bandera de meta | `estilo.py` |
| Gato (animación de caminata) | `estilo.py` (`frames_gato`) |
| Vigas, nodos y anclajes | `puente.py` |

## Fuente
| Archivo | Origen | Licencia |
|---|---|---|
| `MakeABridge/assets/fonts/PressStart2P-Regular.ttf` | Press Start 2P, Google Fonts (https://fonts.google.com/specimen/Press+Start+2P) | SIL Open Font License 1.1 (`PressStart2P-OFL.txt`) |

## Sonidos
| Archivo | Uso | Origen |
|---|---|---|
| `click.wav` | Clic en botones | https://freesound.org/people/suntemple/sounds/253168/ |
| `colocar.wav` | Colocar una viga | https://freesound.org/people/Mellau/sounds/506054/ |
| `romper.wav` | Se rompe una viga o el gato cae | https://pixabay.com/sound-effects/film-special-effects-car-crash-sound-effect-376874|
| `exito.wav` | Nivel superado | https://freesound.org/people/thekindles/sounds/854150/ |
| `menu.wav` | Música del menú | https://freesound.org/people/MichaeLydian/sounds/743697/ |
| `game_over.mp3` | Música de Game Over | https://pixabay.com/sound-effects/musical-game-over-417465/ |

## Código y librerías de terceros
| Componente | Origen |
|---|---|
| `engine/` | Motor desarrollado en clase (curso TVJ2D) |
| Pygame | https://www.pygame.org (LGPL) |
| Pymunk | https://www.pymunk.org (MIT) |
