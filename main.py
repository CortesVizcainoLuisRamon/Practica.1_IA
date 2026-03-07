"""
Punto de entrada principal de la aplicación.
Ejecutar desde la raíz del proyecto:

    python main.py

O desde Docker:

    docker compose up
"""
import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import App

if __name__ == "__main__":
    app = App()
    app.update_idletasks()
    sw = app.winfo_screenwidth()
    sh = app.winfo_screenheight()
    app.geometry(f"1200x800+{(sw-1200)//2}+{(sh-800)//2}")
    app.mainloop()
