# MakeABridge/settings.py
import os

ANCHO, ALTO, FPS = 1000, 600, 60
TITULO = "Make a Bridge"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# --- Física ---
GRAVEDAD = (0, 900)          # y positivo = hacia abajo (igual que pygame)
SUELO_Y = 560                # fondo del valle
SUBPASOS = 4                 # pasos de física por frame (más = estructuras más rígidas y estables)
NODO_MASA = 2.0              # masa de cada articulación
EXCESO_PASOS = 8             # pasos seguidos sobre el límite de fuerza para que una viga se rompa

# --- Categorías de colisión (qué choca con qué) ---
CAT_CAMINANTE = 0b0001
CAT_CAMINO = 0b0010
CAT_TERRENO = 0b0100
CAT_VIGA = 0b1000            # vigas que NO se caminan: no chocan con nada

# --- Construcción ---
GRID = 20                    # 1 "metro" = 20 px; los nodos nuevos se acomodan a esta grilla
PANEL_H = 165                # franja superior reservada para la interfaz
ANCLA_RADIO = 14             # distancia para "enganchar" con un nodo existente
INTENTOS = 5                 # pruebas por nivel

# precio por metro (20 px); resist = fuerza máxima que soporta antes de romperse
VIGAS = {
    "camino":           {"nombre": "Camino",     "precio": 120, "densidad": 0.05,  "resist": 25000, "grosor": 10,
                         "camina": True,  "max_largo": 100, "color": (156, 112, 66)},
    "camino_reforzado": {"nombre": "Reforz.", "precio": 240, "densidad": 0.08,  "resist": 50000, "grosor": 12,
                         "camina": True,  "max_largo": 100, "color": (110, 78, 52)},
    "madera":           {"nombre": "Madera",     "precio": 80,  "densidad": 0.02,  "resist": 45000, "grosor": 6,
                         "camina": False, "max_largo": 120, "color": (196, 146, 84)},
    "acero":            {"nombre": "Acero",      "precio": 200, "densidad": 0.06,  "resist": 90000, "grosor": 6,
                         "camina": False, "max_largo": 120, "color": (112, 124, 146)},
    "cable":            {"nombre": "Cable",      "precio": 40,  "densidad": 0.004, "resist": 60000, "grosor": 2,
                         "camina": False, "max_largo": 260, "color": (60, 50, 44), "cable": True},
}

# --- Caminante ---
PERSONAJE = "gato"           
INICIO_X = 90
META_X = 880
VEL_CAMINANTE = 90
RETRASO_INICIO = 0.8         # s antes de empezar a caminar
TIEMPO_MAX = 45              # s simulados máximos por prueba

# --- Niveles ---
# izq: el acantilado izquierdo termina en x=izq | der: el derecho empieza en x=der
# top_*: altura de la superficie | pilares: (x_centro, altura, ancho) fijos en el valle
NIVELES = [
    {"nombre": "El primer puente", "izq": 250, "der": 550, "top_izq": 355, "top_der": 355,
     "pilares": [], "presupuesto": 10000, "masa_caminante": 6},
    {"nombre": "El valle ancho", "izq": 220, "der": 640, "top_izq": 355, "top_der": 355,
     "pilares": [(430, 455, 60)], "presupuesto": 15000, "masa_caminante": 8},
    {"nombre": "El abismo", "izq": 200, "der": 680, "top_izq": 355, "top_der": 395,
     "pilares": [(440, 475, 40)], "presupuesto": 20000, "masa_caminante": 10},
]

# --- Fin de partida ---
ESPERA_VICTORIA = 2500       
ESPERA_FALLO = 1800          
DEBUG = False
