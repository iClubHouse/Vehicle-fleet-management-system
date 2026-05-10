import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from interfaz.estilos import COLORES, FUENTES, boton_primario, boton_secundario
from config.rutas import ruta_imagen
from negocio.entidades_negocio import VehiculoNegocio
from datos.sql_dao import AlquilerDAO
from entidades.vehiculo import Vehiculo

## Ventana de consulta de vehículos disponibles (con filtro de fechas)
class VentanaConsulta(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._negocio   = VehiculoNegocio()
        self._alq_dao   = AlquilerDAO()
        self._todos     = []
        self._img_label = None
        self._img_ref   = None
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        tk.Label(self, text="Vehículos Disponibles", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(anchor="w", pady=(0, 10))
        tk.Frame(self, bg=COLORES["acento"], height=2).pack(fill="x", pady=(0, 12))

        ## Panel de filtros
        panel_filtros = tk.Frame(self, bg=COLORES["fondo_panel"],
                                  padx=16, pady=12, relief="solid", bd=1)
        panel_filtros.pack(fill="x", pady=(0, 10))

        ## Fila 1: rango de fechas
        fila_fechas = tk.Frame(panel_filtros, bg=COLORES["fondo_panel"])
        fila_fechas.pack(fill="x", pady=(0, 6))

        tk.Label(fila_fechas, text="Fecha inicio (AAAA-MM-DD):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"],
                 width=28, anchor="w").pack(side="left")
        self._entry_inicio = tk.Entry(fila_fechas, font=FUENTES["normal"],
                                       bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entry_inicio.pack(side="left", ipady=5, padx=(0, 20))

        tk.Label(fila_fechas, text="Fecha devolución (AAAA-MM-DD):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"]).pack(side="left")
        self._entry_fin = tk.Entry(fila_fechas, font=FUENTES["normal"],
                                    bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entry_fin.pack(side="left", ipady=5, padx=(0, 16))

        boton_primario(fila_fechas, "🔍 Buscar disponibles",
                       self._filtrar_fechas, ancho=20).pack(side="left")

        ## Fila 2: tipo y búsqueda de texto
        fila_filtros = tk.Frame(panel_filtros, bg=COLORES["fondo_panel"])
        fila_filtros.pack(fill="x")

        tk.Label(fila_filtros, text="Tipo:", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["normal"]).pack(side="left", padx=(0, 4))
        self._var_tipo = tk.StringVar(value="Todos")
        tipos = ["Todos"] + Vehiculo.TIPOS
        tk.OptionMenu(fila_filtros, self._var_tipo, *tipos,
                      command=lambda _: self._aplicar_filtros()).pack(side="left", padx=(0, 16))

        tk.Label(fila_filtros, text="Buscar:", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["normal"]).pack(side="left", padx=(0, 4))
        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *a: self._aplicar_filtros())
        tk.Entry(fila_filtros, textvariable=self._var_busqueda, font=FUENTES["normal"],
                 bg=COLORES["blanco"], relief="solid", bd=1, width=22).pack(side="left", ipady=4)

        boton_secundario(fila_filtros, "Limpiar filtros",
                         self._limpiar_filtros, ancho=14).pack(side="left", padx=(16, 0))

        self._lbl_estado = tk.Label(panel_filtros, text="",
                                     bg=COLORES["fondo_panel"], fg=COLORES["texto_suave"],
                                     font=FUENTES["pequena"])
        self._lbl_estado.pack(anchor="w", pady=(6, 0))

        ## Layout: tabla izquierda, imagen derecha
        contenedor = tk.Frame(self, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True)

        ## Tabla de vehículos
        cols = ("Placa", "Marca", "Modelo", "Tipo", "Transmisión",
                "Combustible", "Color", "Pasajeros", "Maletas", "Costo/día")
        tabla_frame = tk.Frame(contenedor, bg=COLORES["fondo"])
        tabla_frame.pack(side="left", fill="both", expand=True)

        self._tabla = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=18)
        anchos = [90, 100, 110, 90, 100, 90, 90, 75, 65, 100]
        for col, ancho in zip(cols, anchos):
            self._tabla.heading(col, text=col, anchor="center")
            self._tabla.column(col, width=ancho, anchor="center")

        self._tabla.tag_configure("par",   background=COLORES["tabla_par"])
        self._tabla.tag_configure("impar", background=COLORES["tabla_impar"])

        scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._tabla.pack(fill="both", expand=True)
        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        ## Panel de imagen — ancho ampliado para mejor visualización
        self._panel_img = tk.Frame(contenedor, bg=COLORES["fondo_panel"],
                                    width=300, relief="solid", bd=1)
        self._panel_img.pack(side="right", fill="y", padx=(10, 0))
        self._panel_img.pack_propagate(False)

        tk.Label(self._panel_img, text="Vista previa",
             bg=COLORES["fondo_panel"], fg=COLORES["texto_suave"],
             font=("Segoe UI", 11, "bold")).pack(pady=(16, 6))

        self._img_label = tk.Label(self._panel_img, bg=COLORES["fondo_panel"],
                                    text="Seleccione un\nvehículo",
                                    fg=COLORES["texto_suave"], font=FUENTES["normal"])
        self._img_label.pack(expand=True)

        self._lbl_nombre_img = tk.Label(self._panel_img, text="",
                                         bg=COLORES["fondo_panel"], fg=COLORES["texto"],
                                         font=("Segoe UI", 10, "bold"), wraplength=270)
        self._lbl_nombre_img.pack(pady=(4, 16))

        self._disponibles_filtrados = []

    def _cargar_tabla(self):
        self._todos = self._negocio.obtener_disponibles()
        self._disponibles_filtrados = list(self._todos)
        self._poblar(self._disponibles_filtrados)
        self._lbl_estado.config(text=f"Total disponibles: {len(self._todos)} vehículos")
        self._limpiar_vista_previa()

    def _poblar(self, lista):
        self._tabla.delete(*self._tabla.get_children())
        for indice, vehiculo in enumerate(lista):
            tag = "par" if indice % 2 == 0 else "impar"
            self._tabla.insert("", "end", values=(
                vehiculo.numero_placa, vehiculo.marca, vehiculo.modelo, vehiculo.tipo,
                vehiculo.transmision, vehiculo.combustible, vehiculo.color,
                vehiculo.cantidad_pasajeros, vehiculo.cantidad_maletas,
                f"₡{vehiculo.costo_diario:,.2f}"
            ), tags=(tag,))

    def _filtrar_fechas(self):
        inicio = self._entry_inicio.get().strip()
        fin    = self._entry_fin.get().strip()

        if not inicio and not fin:
            self._disponibles_filtrados = list(self._todos)
            self._aplicar_filtros()
            return

        if not inicio or not fin:
            messagebox.showwarning("Requerido",
                "Ingrese ambas fechas para filtrar por disponibilidad.", parent=self)
            return

        try:
            fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
            fecha_fin    = datetime.strptime(fin,    "%Y-%m-%d").date()
            if fecha_fin < fecha_inicio:
                messagebox.showwarning("Fechas inválidas",
                    "La fecha de devolución no puede ser anterior al inicio.", parent=self)
                return
        except ValueError:
            messagebox.showwarning("Formato inválido",
                "Use el formato AAAA-MM-DD para las fechas.", parent=self)
            return

        disponibles = []
        for vehiculo in self._todos:
            tiene_conflicto = self._alq_dao.vehiculo_tiene_reserva_en_fechas(
                vehiculo.numero_placa, inicio, fin)
            if not tiene_conflicto:
                disponibles.append(vehiculo)

        self._disponibles_filtrados = disponibles
        self._aplicar_filtros()
        self._lbl_estado.config(
            text=f"Disponibles del {inicio} al {fin}: {len(disponibles)} vehículos")

    def _aplicar_filtros(self):
        tipo  = self._var_tipo.get()
        texto = self._var_busqueda.get().strip().lower()
        resultado = self._disponibles_filtrados

        if tipo != "Todos":
            resultado = [vehiculo for vehiculo in resultado if vehiculo.tipo == tipo]
        if texto:
            resultado = [vehiculo for vehiculo in resultado
                         if texto in vehiculo.marca.lower()
                         or texto in vehiculo.modelo.lower()
                         or texto in vehiculo.numero_placa.lower()]
        self._poblar(resultado)

    def _limpiar_filtros(self):
        self._entry_inicio.delete(0, tk.END)
        self._entry_fin.delete(0, tk.END)
        self._var_tipo.set("Todos")
        self._var_busqueda.set("")
        self._cargar_tabla()

    def _limpiar_vista_previa(self):
        self._img_ref = None
        self._img_label.config(image="", text="Seleccione un\nvehículo")
        self._lbl_nombre_img.config(text="")

    def _al_seleccionar(self, event=None):
        seleccion = self._tabla.selection()
        if not seleccion:
            return
        valores = self._tabla.item(seleccion[0])["values"]
        marca   = str(valores[1])
        modelo  = str(valores[2])

        ## Carga la imagen del modelo seleccionado desde la ruta registrada
        try:
            modelo_imagen = self._negocio.obtener_imagen(marca, modelo)
            if modelo_imagen and modelo_imagen.ruta_imagen:
                ruta = ruta_imagen(modelo_imagen.ruta_imagen)
                imagen = tk.PhotoImage(file=ruta)
                ancho = imagen.width()
                alto = imagen.height()
                if ancho > 280 or alto > 220:
                    factor = max((ancho + 279) // 280, (alto + 219) // 220)
                    imagen = imagen.subsample(factor, factor)
                self._img_ref = imagen
                self._img_label.config(image=self._img_ref, text="")
            else:
                self._img_label.config(image="", text="Sin imagen\ndisponible")
                self._img_ref = None
        except Exception:
            self._img_label.config(image="", text="Sin imagen\ndisponible")
            self._img_ref = None

        self._lbl_nombre_img.config(
            text=f"{marca} {modelo}\n{valores[3]} | {valores[4]}")