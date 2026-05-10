import tkinter as tk
from interfaz.estilos import COLORES, FUENTES

## Ventana Acerca de
class VentanaAcerca(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._construir()

    def _construir(self):
        contenedor = tk.Frame(self, bg=COLORES["fondo"])
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        ## Encabezado
        tk.Frame(contenedor, bg=COLORES["acento"], height=4, width=420).pack()

        cabecera = tk.Frame(contenedor, bg=COLORES["primario"], padx=40, pady=24)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text="AutoTrust S.A.", bg=COLORES["primario"],
                 fg="#5DADE2", font=FUENTES["logo"]).pack()
        tk.Label(cabecera, text="Gestión de Flotilla Vehicular",
                 bg=COLORES["primario"], fg=COLORES["blanco"],
                 font=FUENTES["pequena"]).pack(pady=(2, 0))

        ## Cuerpo
        cuerpo = tk.Frame(contenedor, bg=COLORES["fondo_panel"],
                          padx=40, pady=28, width=420)
        cuerpo.pack(fill="x")

        def separador():
            tk.Frame(cuerpo, bg=COLORES["borde"], height=1).pack(fill="x", pady=10)

        def bloque(titulo, *lineas):
            tk.Label(cuerpo, text=titulo, bg=COLORES["fondo_panel"],
                     fg=COLORES["secundario"], font=FUENTES["negrita"]).pack(anchor="w")
            for linea in lineas:
                tk.Label(cuerpo, text=linea, bg=COLORES["fondo_panel"],
                         fg=COLORES["texto"], font=FUENTES["normal"]).pack(anchor="w", padx=10)

        bloque("Institución",
               "Colegio Universitario de Cartago")

        separador()

        bloque("Curso",
               "Programación III  |  TI-141")

        separador()

        bloque("Profesora",
               "Milena Mata Sojo")

        separador()

        bloque("Desarrolladores",
               "Marco Rivera Navarro",
               "Diego Salazar Piedra")

        separador()

        bloque("Versión", "1.0.0  —  2025")

        ## Pie
        tk.Frame(contenedor, bg=COLORES["acento"], height=4, width=420).pack()import os
import tkinter as tk
from interfaz.estilos import COLORES, FUENTES
from config.rutas import LOGO_PATH

## Ventana Acerca de
class VentanaAcerca(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self._imagen_logo = None
        self.pack(fill="both", expand=True)
        self._construir()

    def _construir(self):
        contenedor_externo = tk.Frame(self, bg=COLORES["fondo"])
        contenedor_externo.pack(expand=True)

        tk.Frame(contenedor_externo, bg=COLORES["acento"], height=4, width=420).pack()

        ## Cabecera con logo y título
        cabecera = tk.Frame(contenedor_externo, bg=COLORES["primario"], padx=40, pady=20)
        cabecera.pack(fill="x")

        if os.path.exists(LOGO_PATH):
            try:
                imagen_logo = tk.PhotoImage(file=LOGO_PATH)
                ancho = imagen_logo.width()
                alto = imagen_logo.height()
                if ancho > 300 or alto > 300:
                    factor = max((ancho + 299) // 300, (alto + 299) // 300)
                    imagen_logo = imagen_logo.subsample(factor, factor)
                self._imagen_logo = imagen_logo
                tk.Label(
                    cabecera,
                    image=self._imagen_logo,
                    bg=COLORES["primario"]
                ).pack(pady=(0, 8))
            except Exception:
                self._imagen_logo = None

        tk.Label(
            cabecera,
            text="Gestión de Flotilla Vehicular",
            bg=COLORES["primario"],
            fg=COLORES["blanco"],
            font=FUENTES["pequena"]
        ).pack(pady=(2, 0))

        ## Cuerpo de información
        cuerpo = tk.Frame(contenedor_externo, bg=COLORES["fondo_panel"], padx=40, pady=28)
        cuerpo.pack(fill="x")

        def separador():
            tk.Frame(cuerpo, bg=COLORES["borde"], height=1).pack(fill="x", pady=10)

        def bloque(titulo, *lineas):
            tk.Label(
                cuerpo,
                text=titulo,
                bg=COLORES["fondo_panel"],
                fg=COLORES["secundario"],
                font=FUENTES["negrita"],
                justify="center"
            ).pack(anchor="center")
            for linea in lineas:
                tk.Label(
                    cuerpo,
                    text=linea,
                    bg=COLORES["fondo_panel"],
                    fg=COLORES["texto"],
                    font=FUENTES["normal"],
                    justify="center"
                ).pack(anchor="center", padx=10)

        bloque("Institución", "Colegio Universitario de Cartago")
        separador()
        bloque("Curso", "Programación III  |  TI-141")
        separador()
        bloque("Profesora", "Milena Mata Sojo")
        separador()
        bloque("Desarrolladores", "Marco Rivera Navarro", "Diego Salazar Piedra")
        separador()
        bloque("Versión", "1.0.0  —  2026")

        tk.Frame(contenedor_externo, bg=COLORES["acento"], height=4, width=420).pack()