# MakeABridge/main.py   (ejecutar desde la carpeta raíz:  python -m MakeABridge.main)
from .game import FisicasGame


def main():
    juego = FisicasGame()
    juego.run()


if __name__ == "__main__":
    main()
