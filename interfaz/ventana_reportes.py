import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from interfaz.estilos import (COLORES, FUENTES, boton_primario, boton_secundario)
from negocio.alquiler_negocio import AlquilerNegocio
from negocio.entidades_negocio import ClienteNegocio, VehiculoNegocio

## Ventana de reportes con gráficos matplotlib
class VentanaReportes(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._negocio_alquiler = AlquilerNegocio()
        self._negocio_cliente  = ClienteNegocio()
        self._negocio_vehiculo = VehiculoNegocio()
        self._construir()

    def _construir(self):
        tk.Label(self, text="Reportes", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(anchor="w", pady=(0, 10))
        tk.Frame(self, bg=COLORES["acento"], height=2).pack(fill="x", pady=(0, 12))

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        self._tab_barras()
        self._tab_lineas()
        self._tab_detalle()

    ## ── Tab 1: Vehículos más rentados (barras) ───────────────────
    def _tab_barras(self):
        tab = tk.Frame(self._notebook, bg=COLORES["fondo"])
        self._notebook.add(tab, text="  🚗 Vehículos más rentados  ")

        panel = tk.Frame(tab, bg=COLORES["fondo_panel"],
                         padx=16, pady=12, relief="solid", bd=1)
        panel.pack(fill="x", padx=10, pady=(10, 6))

        tk.Label(panel, text="Vehículos más rentados por período",
                 bg=COLORES["fondo_panel"], fg=COLORES["secundario"],
                 font=FUENTES["negrita"]).pack(anchor="w", pady=(0, 8))

        fila = tk.Frame(panel, bg=COLORES["fondo_panel"])
        fila.pack(fill="x")

        tk.Label(fila, text="Desde (AAAA-MM-DD):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"],
                 width=22, anchor="w").pack(side="left")
        self._entrada_desde_barras = tk.Entry(fila, font=FUENTES["normal"],
                                              bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entrada_desde_barras.pack(side="left", ipady=5, padx=(0, 16))

        tk.Label(fila, text="Hasta (AAAA-MM-DD):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"]).pack(side="left")
        self._entrada_hasta_barras = tk.Entry(fila, font=FUENTES["normal"],
                                              bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entrada_hasta_barras.pack(side="left", ipady=5, padx=(0, 16))

        boton_primario(fila, "📊 Generar gráfico",
                       self._generar_barras, ancho=18).pack(side="left")

        self._frame_barras = tk.Frame(tab, bg=COLORES["fondo"])
        self._frame_barras.pack(fill="both", expand=True, padx=10, pady=6)

        tk.Label(self._frame_barras,
                 text="Ingrese un rango de fechas y presione 'Generar gráfico'.",
                 bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                 font=FUENTES["normal"]).pack(expand=True)

    def _generar_barras(self):
        desde = self._entrada_desde_barras.get().strip()
        hasta = self._entrada_hasta_barras.get().strip()
        if not desde or not hasta:
            messagebox.showwarning("Requerido", "Ingrese el rango de fechas.", parent=self)
            return
        try:
            alquileres = self._negocio_alquiler.obtener_alquileres_por_periodo(desde, hasta)
            if not alquileres:
                messagebox.showinfo("Sin datos",
                    "No hay alquileres en el período indicado.", parent=self)
                return

            ## Mapea placa → marca/modelo usando negocio de vehículo
            cache_vehiculos = {}
            conteo = {}
            for alquiler in alquileres:
                if alquiler.estado == "Cancelado":
                    continue
                placa = alquiler.id_vehiculo
                if placa not in cache_vehiculos:
                    cache_vehiculos[placa] = self._negocio_vehiculo.buscar(placa)
                vehiculo = cache_vehiculos[placa]
                clave = f"{vehiculo.marca}\n{vehiculo.modelo}" if vehiculo else placa
                conteo[clave] = conteo.get(clave, 0) + 1

            if not conteo:
                messagebox.showinfo("Sin datos",
                    "No hay alquileres activos en ese período.", parent=self)
                return

            etiquetas = []
            valores   = []
            for clave, cantidad in sorted(conteo.items(), key=lambda x: x[1], reverse=True):
                etiquetas.append(clave)
                valores.append(cantidad)

            total        = sum(valores)
            porcentajes  = [round(v / total * 100, 1) for v in valores]

            self._dibujar_barras(etiquetas, valores, porcentajes, desde, hasta)

        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)

    def _dibujar_barras(self, etiquetas, valores, porcentajes, desde, hasta):
        for widget in self._frame_barras.winfo_children():
            widget.destroy()

        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        figura, eje = plt.subplots(figsize=(10, 5))
        figura.patch.set_facecolor("#F4F7FA")
        eje.set_facecolor("#FFFFFF")

        colores_barras = ["#2E86C1", "#1E8449", "#D4AC0D", "#C0392B",
                          "#8E44AD", "#1ABC9C", "#E67E22", "#2980B9"]
        barras = eje.bar(range(len(etiquetas)), valores,
                         color=colores_barras[:len(etiquetas)],
                         edgecolor="white", linewidth=0.8)

        for barra, porcentaje in zip(barras, porcentajes):
            eje.text(barra.get_x() + barra.get_width() / 2,
                     barra.get_height() + 0.1,
                     f"{porcentaje}%", ha="center", va="bottom",
                     fontsize=9, fontweight="bold", color="#1A252F")

        eje.set_xticks(range(len(etiquetas)))
        eje.set_xticklabels(etiquetas, fontsize=9)
        eje.set_ylabel("Cantidad de alquileres", fontsize=10)
        eje.set_title(f"Vehículos más rentados por modelo\nPeríodo: {desde} → {hasta}",
                      fontsize=12, fontweight="bold", color="#0F2235")
        eje.yaxis.get_major_locator().set_params(integer=True)
        eje.spines[["top", "right"]].set_visible(False)
        eje.grid(axis="y", linestyle="--", alpha=0.5)

        figura.tight_layout()

        lienzo = FigureCanvasTkAgg(figura, master=self._frame_barras)
        lienzo.draw()
        lienzo.get_tk_widget().pack(fill="both", expand=True)
        plt.close(figura)

    ## ── Tab 2: Segmentación por edad (líneas) ────────────────────
    def _tab_lineas(self):
        tab = tk.Frame(self._notebook, bg=COLORES["fondo"])
        self._notebook.add(tab, text="  👥 Segmentación por edad  ")

        panel = tk.Frame(tab, bg=COLORES["fondo_panel"],
                         padx=16, pady=12, relief="solid", bd=1)
        panel.pack(fill="x", padx=10, pady=(10, 6))

        tk.Label(panel, text="Segmentación de clientes por edad — año a consultar",
                 bg=COLORES["fondo_panel"], fg=COLORES["secundario"],
                 font=FUENTES["negrita"]).pack(anchor="w", pady=(0, 8))

        fila = tk.Frame(panel, bg=COLORES["fondo_panel"])
        fila.pack(fill="x")

        tk.Label(fila, text="Año (AAAA):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"],
                 width=14, anchor="w").pack(side="left")
        self._entrada_anio = tk.Entry(fila, font=FUENTES["normal"],
                                      bg=COLORES["blanco"], relief="solid", bd=1, width=8)
        self._entrada_anio.pack(side="left", ipady=5, padx=(0, 16))

        boton_primario(fila, "📈 Generar gráfico",
                       self._generar_lineas, ancho=18).pack(side="left")

        self._frame_lineas = tk.Frame(tab, bg=COLORES["fondo"])
        self._frame_lineas.pack(fill="both", expand=True, padx=10, pady=6)

        tk.Label(self._frame_lineas,
                 text="Ingrese el año y presione 'Generar gráfico'.",
                 bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                 font=FUENTES["normal"]).pack(expand=True)

    def _generar_lineas(self):
        anio_str = self._entrada_anio.get().strip()
        if not anio_str or not anio_str.isdigit() or len(anio_str) != 4:
            messagebox.showwarning("Requerido", "Ingrese un año válido (ej. 2025).", parent=self)
            return

        anio = int(anio_str)
        try:
            desde      = f"{anio}-01-01"
            hasta      = f"{anio}-12-31"
            alquileres = self._negocio_alquiler.obtener_alquileres_por_periodo(desde, hasta)

            ## Obtiene todos los clientes y los mapea por identificación
            lista_clientes = self._negocio_cliente.obtener_todos()
            mapa_clientes  = {cliente.identificacion: cliente for cliente in lista_clientes}

            ## Rangos de edad: 18-19, 20-24, luego periodos de 5 años
            rangos           = [(18, 19), (20, 24)] + [(inicio, inicio + 4) for inicio in range(25, 96, 5)]
            etiquetas_rangos = [f"{rango[0]}-{rango[1]}" for rango in rangos]

            ## Inicializa conteo por rango y mes
            datos = {etiqueta: [0] * 12 for etiqueta in etiquetas_rangos}

            for alquiler in alquileres:
                if alquiler.estado == "Cancelado":
                    continue
                cliente = mapa_clientes.get(alquiler.id_cliente)
                if not cliente or not cliente.fecha_nacimiento:
                    continue

                fecha_nacimiento = cliente.fecha_nacimiento
                ## Convierte a date si viene como cadena
                if isinstance(fecha_nacimiento, str) and fecha_nacimiento:
                    try:
                        fecha_nacimiento = datetime.strptime(fecha_nacimiento[:10], "%Y-%m-%d").date()
                    except Exception:
                        continue

                fecha_inicio = alquiler.fecha_inicio
                if not hasattr(fecha_inicio, "year"):
                    continue

                ## Calcula edad al momento del alquiler
                edad = fecha_inicio.year - fecha_nacimiento.year - (
                    (fecha_inicio.month, fecha_inicio.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
                indice_mes = fecha_inicio.month - 1

                for etiqueta, (edad_min, edad_max) in zip(etiquetas_rangos, rangos):
                    if edad_min <= edad <= edad_max:
                        datos[etiqueta][indice_mes] += 1
                        break

            ## Solo grafica rangos con al menos un alquiler
            datos_activos = {clave: valores for clave, valores in datos.items() if any(v > 0 for v in valores)}

            self._dibujar_lineas(datos_activos, anio)

        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)

    def _dibujar_lineas(self, datos, anio):
        for widget in self._frame_lineas.winfo_children():
            widget.destroy()

        if not datos:
            tk.Label(self._frame_lineas,
                     text=f"No hay datos de alquileres con clientes registrados en {anio}.",
                     bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                     font=FUENTES["normal"]).pack(expand=True)
            return

        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        meses  = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                  "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        paleta = ["#2E86C1", "#1E8449", "#D4AC0D", "#C0392B",
                  "#8E44AD", "#1ABC9C", "#E67E22", "#2980B9",
                  "#CB4335", "#117A65", "#9B59B6", "#D35400"]

        figura, eje = plt.subplots(figsize=(12, 5))
        figura.patch.set_facecolor("#F4F7FA")
        eje.set_facecolor("#FFFFFF")

        for indice, (etiqueta, valores) in enumerate(datos.items()):
            color = paleta[indice % len(paleta)]
            eje.plot(meses, valores, marker="o", linewidth=2, label=etiqueta, color=color)
            for indice_mes, valor in enumerate(valores):
                if valor > 0:
                    eje.annotate(str(valor), (meses[indice_mes], valor),
                                 textcoords="offset points", xytext=(0, 6),
                                 ha="center", fontsize=7, color=color)

        eje.set_xlabel("Mes", fontsize=10)
        eje.set_ylabel("Cantidad de alquileres", fontsize=10)
        eje.set_title(f"Segmentación de clientes por edad — Año {anio}",
                      fontsize=12, fontweight="bold", color="#0F2235")
        eje.legend(title="Rango de edad", bbox_to_anchor=(1.01, 1),
                   loc="upper left", fontsize=8)
        eje.yaxis.get_major_locator().set_params(integer=True)
        eje.spines[["top", "right"]].set_visible(False)
        eje.grid(axis="y", linestyle="--", alpha=0.4)

        figura.tight_layout()

        lienzo = FigureCanvasTkAgg(figura, master=self._frame_lineas)
        lienzo.draw()
        lienzo.get_tk_widget().pack(fill="both", expand=True)
        plt.close(figura)

    ## ── Tab 3: Reporte tabular detallado ─────────────────────────
    def _tab_detalle(self):
        tab = tk.Frame(self._notebook, bg=COLORES["fondo"])
        self._notebook.add(tab, text="  📋 Detalle de alquileres  ")

        panel = tk.Frame(tab, bg=COLORES["fondo_panel"],
                         padx=16, pady=10, relief="solid", bd=1)
        panel.pack(fill="x", padx=10, pady=(10, 6))

        fila = tk.Frame(panel, bg=COLORES["fondo_panel"])
        fila.pack(fill="x")

        tk.Label(fila, text="Desde (AAAA-MM-DD):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"],
                 width=22, anchor="w").pack(side="left")
        self._entrada_desde_detalle = tk.Entry(fila, font=FUENTES["normal"],
                                               bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entrada_desde_detalle.pack(side="left", ipady=5, padx=(0, 16))

        tk.Label(fila, text="Hasta (AAAA-MM-DD):", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"]).pack(side="left")
        self._entrada_hasta_detalle = tk.Entry(fila, font=FUENTES["normal"],
                                               bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entrada_hasta_detalle.pack(side="left", ipady=5, padx=(0, 16))

        boton_primario(fila, "📊 Generar", self._generar_detalle, ancho=14).pack(side="left")
        boton_secundario(fila, "Limpiar",  self._limpiar_detalle, ancho=10).pack(side="left", padx=(8, 0))

        self._panel_resumen = tk.Frame(tab, bg=COLORES["fondo_panel"],
                                        padx=16, pady=8, relief="solid", bd=1)
        self._panel_resumen.pack(fill="x", padx=10, pady=(0, 6))
        self._etiqueta_resumen = tk.Label(self._panel_resumen, text="",
                                           bg=COLORES["fondo_panel"], fg=COLORES["texto"],
                                           font=FUENTES["negrita"])
        self._etiqueta_resumen.pack(anchor="w")

        columnas_detalle = ("ID", "Cliente", "Vehículo", "F. Inicio", "F. Devolución",
                            "Días", "Base", "Impuesto", "Seguro", "Total", "Estado")
        contenedor_tabla = tk.Frame(tab, bg=COLORES["fondo"])
        contenedor_tabla.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._tabla_detalle = ttk.Treeview(contenedor_tabla, columns=columnas_detalle,
                                            show="headings", height=16)
        anchos_detalle = [55, 120, 100, 100, 110, 45, 100, 90, 90, 100, 100]
        for columna, ancho in zip(columnas_detalle, anchos_detalle):
            self._tabla_detalle.heading(columna, text=columna, anchor="center")
            self._tabla_detalle.column(columna, width=ancho, anchor="center")
        self._tabla_detalle.tag_configure("par",   background=COLORES["tabla_par"])
        self._tabla_detalle.tag_configure("impar", background=COLORES["tabla_impar"])

        scroll = ttk.Scrollbar(contenedor_tabla, orient="vertical", command=self._tabla_detalle.yview)
        self._tabla_detalle.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._tabla_detalle.pack(fill="both", expand=True)

    def _generar_detalle(self):
        desde = self._entrada_desde_detalle.get().strip()
        hasta = self._entrada_hasta_detalle.get().strip()
        if not desde or not hasta:
            messagebox.showwarning("Requerido", "Ingrese el rango de fechas.", parent=self)
            return
        try:
            alquileres = self._negocio_alquiler.obtener_alquileres_por_periodo(desde, hasta)
            self._tabla_detalle.delete(*self._tabla_detalle.get_children())
            for indice, alquiler in enumerate(alquileres):
                etiqueta = "par" if indice % 2 == 0 else "impar"
                self._tabla_detalle.insert("", "end", values=(
                    alquiler.id_alquiler, alquiler.id_cliente, alquiler.id_vehiculo,
                    str(alquiler.fecha_inicio), str(alquiler.fecha_devolucion_planificada),
                    alquiler.cantidad_dias, f"₡{alquiler.costo_base:,.2f}",
                    f"₡{alquiler.impuesto:,.2f}", f"₡{alquiler.costo_seguro:,.2f}",
                    f"₡{alquiler.total:,.2f}", alquiler.estado
                ), tags=(etiqueta,))
            total_recaudado = sum(a.total for a in alquileres if a.estado != "Cancelado")
            self._etiqueta_resumen.config(
                text=(f"Período: {desde} → {hasta}   |   "
                      f"Alquileres: {len(alquileres)}   |   "
                      f"Total recaudado: ₡{total_recaudado:,.2f}"))
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)

    def _limpiar_detalle(self):
        self._entrada_desde_detalle.delete(0, tk.END)
        self._entrada_hasta_detalle.delete(0, tk.END)
        self._tabla_detalle.delete(*self._tabla_detalle.get_children())
        self._etiqueta_resumen.config(text="")