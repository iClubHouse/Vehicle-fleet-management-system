import tkinter as tk
from tkinter import ttk, messagebox
from interfaz.estilos import (COLORES, FUENTES, boton_primario,
                               boton_peligro, boton_secundario, boton_exito)
from negocio.alquiler_negocio import AlquilerNegocio, DevolucionNegocio

## Ventana de registro de devoluciones
class VentanaDevolucion(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._negocio            = AlquilerNegocio()
        self._dev_negocio        = DevolucionNegocio()
        self._alquiler           = None
        self._danios             = []
        self._dias_atraso        = 0
        self._monto_penalizacion = 0.0
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        ## Canvas scrollable que respeta el ancho del contenedor
        canvas    = tk.Canvas(self, bg=COLORES["fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._body  = tk.Frame(canvas, bg=COLORES["fondo"])
        id_ventana  = canvas.create_window((0, 0), window=self._body, anchor="nw")

        self._body.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(id_ventana, width=e.width))

        tk.Label(self._body, text="Registro de Devoluciones", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(
                     anchor="w", padx=24, pady=(16, 6))
        tk.Frame(self._body, bg=COLORES["acento"], height=2).pack(
            fill="x", padx=24, pady=(0, 12))

        self._construir_tabla_alquileres()
        self._construir_panel_devolucion()
        self._construir_panel_danios()
        self._construir_panel_resumen()
        self._construir_boton_confirmar()

    def _construir_tabla_alquileres(self):
        panel = tk.Frame(self._body, bg=COLORES["fondo_panel"], relief="solid", bd=1)
        panel.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(panel, text="Alquileres activos (En préstamo):",
                 bg=COLORES["fondo_panel"], fg=COLORES["texto"],
                 font=FUENTES["negrita"]).pack(anchor="w", padx=16, pady=(12, 6))

        tabla_wrap = tk.Frame(panel, bg=COLORES["fondo_panel"])
        tabla_wrap.pack(fill="x", padx=16, pady=(0, 12))

        cols = ("ID", "Cliente", "Vehículo", "F. Inicio", "F. Devolución planificada", "Total alquiler")
        self._tabla_alq = ttk.Treeview(tabla_wrap, columns=cols, show="headings", height=4)
        anchos = [60, 160, 120, 110, 190, 130]
        for col, ancho in zip(cols, anchos):
            self._tabla_alq.heading(col, text=col, anchor="center")
            self._tabla_alq.column(col, width=ancho, anchor="center")
        self._tabla_alq.tag_configure("par",   background=COLORES["tabla_par"])
        self._tabla_alq.tag_configure("impar", background=COLORES["tabla_impar"])
        ## Al hacer clic en una fila se carga el alquiler
        self._tabla_alq.bind("<<TreeviewSelect>>", self._al_seleccionar)

        scrollbar_alq = ttk.Scrollbar(tabla_wrap, orient="vertical", command=self._tabla_alq.yview)
        self._tabla_alq.configure(yscrollcommand=scrollbar_alq.set)
        scrollbar_alq.pack(side="right", fill="y")
        self._tabla_alq.pack(fill="x")

    def _construir_panel_devolucion(self):
        panel = tk.Frame(self._body, bg=COLORES["fondo_panel"], relief="solid", bd=1)
        panel.pack(fill="x", padx=24, pady=(0, 10))

        self._lbl_info = tk.Label(panel,
                                   text="Seleccione un alquiler de la tabla.",
                                   bg=COLORES["fondo_panel"], fg=COLORES["texto_suave"],
                                   font=FUENTES["normal"])
        self._lbl_info.pack(anchor="w", padx=16, pady=(12, 8))

        fila_fecha = tk.Frame(panel, bg=COLORES["fondo_panel"])
        fila_fecha.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(fila_fecha, text="Fecha devolución real (AAAA-MM-DD) *",
                 bg=COLORES["fondo_panel"], fg=COLORES["texto"],
                 font=FUENTES["etiqueta"], width=36, anchor="w").pack(side="left")
        self._entry_fecha = tk.Entry(fila_fecha, font=FUENTES["normal"],
                                     bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entry_fecha.pack(side="left", ipady=5)

        boton_primario(panel, "🔍 Calcular penalización",
                       self._calcular, ancho=22).pack(anchor="w", padx=16, pady=(0, 12))

    def _construir_panel_danios(self):
        panel = tk.Frame(self._body, bg=COLORES["fondo_panel"], relief="solid", bd=1)
        panel.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(panel, text="Daños (opcional)",
                 bg=COLORES["fondo_panel"], fg=COLORES["secundario"],
                 font=FUENTES["negrita"]).pack(anchor="w", padx=16, pady=(12, 6))

        fila_danio = tk.Frame(panel, bg=COLORES["fondo_panel"])
        fila_danio.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(fila_danio, text="Descripción:", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"],
                 width=14, anchor="w").pack(side="left")
        self._entry_desc = tk.Entry(fila_danio, font=FUENTES["normal"],
                                    bg=COLORES["blanco"], relief="solid", bd=1, width=34)
        self._entry_desc.pack(side="left", ipady=5, padx=(0, 10))
        tk.Label(fila_danio, text="Costo (₡):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"]).pack(side="left")
        self._entry_costo = tk.Entry(fila_danio, font=FUENTES["normal"],
                                     bg=COLORES["blanco"], relief="solid", bd=1, width=12)
        self._entry_costo.pack(side="left", ipady=5, padx=(4, 8))
        boton_exito(fila_danio, "➕ Agregar", self._agregar_danio, ancho=12).pack(side="left")

        tabla_wrap = tk.Frame(panel, bg=COLORES["fondo_panel"])
        tabla_wrap.pack(fill="x", padx=16, pady=(0, 6))
        cols_danio = ("Descripción", "Costo")
        self._tabla_danios = ttk.Treeview(tabla_wrap, columns=cols_danio,
                                           show="headings", height=3)
        self._tabla_danios.heading("Descripción", text="Descripción", anchor="center")
        self._tabla_danios.column("Descripción", width=500, anchor="center")
        self._tabla_danios.heading("Costo", text="Costo (₡)", anchor="center")
        self._tabla_danios.column("Costo", width=130, anchor="center")
        self._tabla_danios.pack(fill="x")

        boton_peligro(panel, "🗑 Quitar daño seleccionado",
                      self._quitar_danio, ancho=24).pack(anchor="w", padx=16, pady=(4, 12))

    def _construir_panel_resumen(self):
        self._panel_resumen = tk.Frame(self._body, bg=COLORES["fondo_panel"],
                                        relief="solid", bd=1)
        self._panel_resumen.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(self._panel_resumen, text="Resumen de cobros",
                 bg=COLORES["fondo_panel"], fg=COLORES["secundario"],
                 font=FUENTES["negrita"]).pack(anchor="w", padx=16, pady=(12, 6))

        def fila_resumen(variable_texto, negrita=False):
            fuente = FUENTES["negrita"] if negrita else FUENTES["normal"]
            tk.Label(self._panel_resumen, textvariable=variable_texto,
                     bg=COLORES["fondo_panel"], fg=COLORES["texto"],
                     font=fuente, anchor="w").pack(anchor="w", padx=32, pady=1)

        self._var_costo_original = tk.StringVar(value="Costo original del alquiler:  —")
        self._var_penalizacion   = tk.StringVar(value="Penalización por atraso:       —")
        self._var_danios_total   = tk.StringVar(value="Total por daños:               —")
        self._var_gran_total     = tk.StringVar(value="TOTAL A COBRAR:                —")

        fila_resumen(self._var_costo_original)
        fila_resumen(self._var_penalizacion)
        fila_resumen(self._var_danios_total)
        tk.Frame(self._panel_resumen, bg=COLORES["borde"], height=1).pack(
            fill="x", padx=16, pady=6)
        fila_resumen(self._var_gran_total, negrita=True)
        tk.Frame(self._panel_resumen, bg=COLORES["fondo_panel"]).pack(pady=6)

    def _construir_boton_confirmar(self):
        tk.Frame(self._body, bg=COLORES["borde"], height=1).pack(
            fill="x", padx=24, pady=(0, 10))
        boton_exito(self._body, "✅ Confirmar devolución",
                    self._confirmar, ancho=26).pack(anchor="w", padx=24, pady=(0, 20))

    ## ── Carga de datos ───────────────────────────────────────────

    def _cargar_tabla(self):
        todos   = self._negocio.obtener_pendientes_en_prestamo()
        activos = [alquiler for alquiler in todos if alquiler.estado == "En préstamo"]
        self._tabla_alq.delete(*self._tabla_alq.get_children())
        for indice, alquiler in enumerate(activos):
            tag = "par" if indice % 2 == 0 else "impar"
            self._tabla_alq.insert("", "end", iid=str(alquiler.id_alquiler), values=(
                alquiler.id_alquiler, alquiler.id_cliente, alquiler.id_vehiculo,
                str(alquiler.fecha_inicio),
                str(alquiler.fecha_devolucion_planificada),
                f"₡{alquiler.total:,.2f}"
            ), tags=(tag,))
        self._alquileres = activos

    ## ── Acciones ─────────────────────────────────────────────────

    def _al_seleccionar(self, event=None):
        seleccion = self._tabla_alq.selection()
        if not seleccion:
            return
        try:
            id_alquiler = int(seleccion[0])
        except (TypeError, ValueError, IndexError):
            messagebox.showwarning("Inválido", "No se pudo identificar el alquiler seleccionado.", parent=self)
            return
        self._alquiler = next((alquiler for alquiler in self._alquileres
                                if alquiler.id_alquiler == id_alquiler), None)
        if self._alquiler:
            self._lbl_info.config(
                text=(f"Alquiler #{self._alquiler.id_alquiler}   |   "
                      f"Cliente: {self._alquiler.id_cliente}   |   "
                      f"Vehículo: {self._alquiler.id_vehiculo}   |   "
                      f"Devolución planificada: {self._alquiler.fecha_devolucion_planificada}"),
                fg=COLORES["texto"])
            self._danios.clear()
            self._tabla_danios.delete(*self._tabla_danios.get_children())
            self._dias_atraso        = 0
            self._monto_penalizacion = 0.0
            self._actualizar_resumen()

    def _calcular(self):
        if not self._alquiler:
            messagebox.showwarning("Requerido", "Seleccione un alquiler.", parent=self)
            return
        fecha = self._entry_fecha.get().strip()
        if not fecha:
            messagebox.showwarning("Requerido", "Ingrese la fecha de devolución real.", parent=self)
            return
        try:
            resultado            = self._dev_negocio.calcular_devolucion(self._alquiler, fecha)
            self._dias_atraso        = resultado["dias_atraso"]
            self._monto_penalizacion = resultado["monto_penalizacion"]
            self._actualizar_resumen()
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)

    def _agregar_danio(self):
        descripcion = self._entry_desc.get().strip()
        costo_texto = self._entry_costo.get().strip()
        if not descripcion:
            messagebox.showwarning("Requerido", "Ingrese la descripción del daño.", parent=self)
            return
        try:
            costo = float(costo_texto or 0)
            if costo < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Inválido", "El costo debe ser un número positivo.", parent=self)
            return
        self._danios.append({"descripcion": descripcion, "costo": costo})
        self._tabla_danios.insert("", "end", values=(descripcion, f"₡{costo:,.2f}"))
        self._entry_desc.delete(0, tk.END)
        self._entry_costo.delete(0, tk.END)
        self._actualizar_resumen()

    def _quitar_danio(self):
        seleccion = self._tabla_danios.selection()
        if not seleccion:
            return
        indice = self._tabla_danios.index(seleccion[0])
        self._danios.pop(indice)
        self._tabla_danios.delete(seleccion[0])
        self._actualizar_resumen()

    def _actualizar_resumen(self):
        if not self._alquiler:
            self._var_costo_original.set("Costo original del alquiler:  —")
            self._var_penalizacion.set(  "Penalización por atraso:       —")
            self._var_danios_total.set(  "Total por daños:               —")
            self._var_gran_total.set(    "TOTAL A COBRAR:                —")
            return

        costo_original = self._alquiler.total
        costo_danios   = sum(danio["costo"] for danio in self._danios)
        gran_total     = costo_original + self._monto_penalizacion + costo_danios

        if self._dias_atraso > 0:
            texto_penalizacion = f"₡{self._monto_penalizacion:,.2f}  ({self._dias_atraso} día(s) de atraso)"
        else:
            texto_penalizacion = "₡0.00  (sin atraso)"

        self._var_costo_original.set(f"Costo original del alquiler:   ₡{costo_original:,.2f}")
        self._var_penalizacion.set(  f"Penalización por atraso:       {texto_penalizacion}")
        self._var_danios_total.set(  f"Total por daños:               ₡{costo_danios:,.2f}  ({len(self._danios)} daño(s))")
        self._var_gran_total.set(    f"TOTAL A COBRAR:                ₡{gran_total:,.2f}")

    def _confirmar(self):
        if not self._alquiler:
            messagebox.showwarning("Requerido", "Seleccione un alquiler.", parent=self)
            return
        fecha = self._entry_fecha.get().strip()
        if not fecha:
            messagebox.showwarning("Requerido", "Ingrese la fecha de devolución real.", parent=self)
            return
        if not messagebox.askyesno("Confirmar",
                "¿Registrar la devolución con los datos ingresados?", parent=self):
            return
        try:
            id_devolucion, cargos_extra = self._dev_negocio.registrar_devolucion(
                self._alquiler, fecha, self._danios)
            gran_total = self._alquiler.total + cargos_extra
            messagebox.showinfo("Éxito",
                f"Devolución #{id_devolucion} registrada correctamente.\n"
                f"Costo original: ₡{self._alquiler.total:,.2f}\n"
                f"Cargos extra (atraso + daños): ₡{cargos_extra:,.2f}\n"
                f"Total cobrado: ₡{gran_total:,.2f}",
                parent=self)
            self._alquiler           = None
            self._danios.clear()
            self._dias_atraso        = 0
            self._monto_penalizacion = 0.0
            self._lbl_info.config(text="Seleccione un alquiler de la tabla.",
                                   fg=COLORES["texto_suave"])
            self._entry_fecha.delete(0, tk.END)
            self._tabla_danios.delete(*self._tabla_danios.get_children())
            self._actualizar_resumen()
            self._cargar_tabla()
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)