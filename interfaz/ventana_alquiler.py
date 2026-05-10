import tkinter as tk
from tkinter import ttk, messagebox
from interfaz.estilos import (COLORES, FUENTES, boton_primario,
                               boton_secundario, boton_exito)
from negocio.entidades_negocio import VehiculoNegocio, ClienteNegocio
from negocio.alquiler_negocio import AlquilerNegocio
from entidades.vehiculo import Vehiculo

## Ventana de registro de alquiler
class VentanaAlquiler(tk.Frame):

    def __init__(self, parent, usuario, id_cliente=None):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._usuario         = usuario
        self._id_cliente      = id_cliente
        self._negocio         = AlquilerNegocio()
        self._v_negocio       = VehiculoNegocio()
        self._c_negocio       = ClienteNegocio()
        self._todos_vehiculos = []
        self._clientes_combo_map = {}
        self._construir()
        self._cargar_vehiculos()

    def _construir(self):
        tk.Label(self, text="Solicitar Alquiler", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(anchor="w", pady=(0, 10))
        tk.Frame(self, bg=COLORES["acento"], height=2).pack(fill="x", pady=(0, 12))

        panel_datos = tk.Frame(self, bg=COLORES["fondo_panel"], padx=20, pady=16,
                               relief="solid", bd=1)
        panel_datos.pack(fill="x", pady=(0, 12))

        if not self._id_cliente:
            fila_cliente = tk.Frame(panel_datos, bg=COLORES["fondo_panel"])
            fila_cliente.pack(fill="x", pady=4)
            tk.Label(fila_cliente, text="Cliente *", bg=COLORES["fondo_panel"],
                     fg=COLORES["texto"], font=FUENTES["etiqueta"], width=20, anchor="w").pack(side="left")
            self._var_cliente_combo = tk.StringVar()
            self._combo_cliente = ttk.Combobox(
                fila_cliente,
                textvariable=self._var_cliente_combo,
                state="readonly"
            )
            self._combo_cliente.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 8))

            tk.Label(fila_cliente, text="ID manual:", bg=COLORES["fondo_panel"],
                     fg=COLORES["texto"], font=FUENTES["normal"]).pack(side="left", padx=(0, 6))
            self._entry_cliente = tk.Entry(fila_cliente, font=FUENTES["normal"],
                                           bg=COLORES["blanco"], relief="solid", bd=1, width=18)
            self._entry_cliente.pack(side="left", ipady=5, padx=(0, 8))
            boton_primario(fila_cliente, "Verificar", self._verificar_cliente, ancho=10).pack(side="left")
            self._lbl_cliente = tk.Label(panel_datos, text="", bg=COLORES["fondo_panel"],
                                         fg=COLORES["exito"], font=FUENTES["pequena"])
            self._lbl_cliente.pack(anchor="w", padx=4)
            self._cargar_clientes_activos()
        else:
            try:
                cliente = self._c_negocio.buscar(self._id_cliente)
                nombre = cliente.nombre_completo() if cliente else self._id_cliente
                if not cliente:
                    print(f"[VentanaAlquiler] Cliente no encontrado para ID '{self._id_cliente}'.")
            except Exception as error_carga_cliente:
                print(
                    f"[VentanaAlquiler] Error al cargar cliente '{self._id_cliente}': "
                    f"{type(error_carga_cliente).__name__}: {error_carga_cliente}"
                )
                nombre = self._id_cliente
            tk.Label(panel_datos, text=f"Cliente: {nombre}",
                     bg=COLORES["fondo_panel"], fg=COLORES["texto"],
                     font=FUENTES["negrita"]).pack(anchor="w", pady=4)

        fila_fechas = tk.Frame(panel_datos, bg=COLORES["fondo_panel"])
        fila_fechas.pack(fill="x", pady=4)
        tk.Label(fila_fechas, text="Fecha inicio (AAAA-MM-DD) *", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"], width=28, anchor="w").pack(side="left")
        self._entry_inicio = tk.Entry(fila_fechas, font=FUENTES["normal"],
                                      bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entry_inicio.pack(side="left", ipady=5, padx=(0, 20))

        tk.Label(fila_fechas, text="Fecha devolución (AAAA-MM-DD) *", bg=COLORES["fondo_panel"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"]).pack(side="left")
        self._entry_fin = tk.Entry(fila_fechas, font=FUENTES["normal"],
                                   bg=COLORES["blanco"], relief="solid", bd=1, width=14)
        self._entry_fin.pack(side="left", ipady=5, padx=(4, 0))

        barra_filtros = tk.Frame(self, bg=COLORES["fondo"])
        barra_filtros.pack(fill="x", pady=(0, 6))

        tk.Label(barra_filtros, text="Seleccione un vehículo disponible:",
                 bg=COLORES["fondo"], fg=COLORES["texto"],
                 font=FUENTES["negrita"]).pack(side="left", padx=(0, 16))

        tk.Label(barra_filtros, text="Tipo:", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["normal"]).pack(side="left", padx=(0, 4))
        self._var_tipo = tk.StringVar(value="Todos")
        tipos = ["Todos"] + Vehiculo.TIPOS
        tk.OptionMenu(barra_filtros, self._var_tipo, *tipos,
                      command=lambda _: self._aplicar_filtros()).pack(side="left", padx=(0, 16))

        tk.Label(barra_filtros, text="Buscar:", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["normal"]).pack(side="left", padx=(0, 4))
        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *a: self._aplicar_filtros())
        tk.Entry(barra_filtros, textvariable=self._var_busqueda, font=FUENTES["normal"],
                 bg=COLORES["blanco"], relief="solid", bd=1, width=22).pack(side="left", ipady=4)

        boton_secundario(barra_filtros, "Limpiar filtros",
                         self._limpiar_filtros, ancho=14).pack(side="left", padx=(12, 0))

        cols  = ("Placa", "Marca", "Modelo", "Tipo", "Transmisión", "Combustible", "Pasajeros", "Costo/día")
        self._tabla = ttk.Treeview(self, columns=cols, show="headings", height=10)
        anchos = [90, 100, 110, 90, 100, 90, 80, 100]
        for col, ancho in zip(cols, anchos):
            self._tabla.heading(col, text=col, anchor="center")
            self._tabla.column(col, width=ancho, anchor="center")

        self._tabla.tag_configure("par",   background=COLORES["tabla_par"])
        self._tabla.tag_configure("impar", background=COLORES["tabla_impar"])

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._tabla.pack(fill="both", expand=True)

        self._panel_resumen = tk.Frame(self, bg=COLORES["fondo_panel"],
                                       padx=20, pady=12, relief="solid", bd=1)
        self._panel_resumen.pack(fill="x", pady=(10, 0))
        self._lbl_resumen = tk.Label(self._panel_resumen,
                                     text="Seleccione fechas y vehículo, luego presione 'Ver resumen'.",
                                     bg=COLORES["fondo_panel"], fg=COLORES["texto_suave"],
                                     font=FUENTES["normal"])
        self._lbl_resumen.pack(anchor="w")

        botones_accion = tk.Frame(self, bg=COLORES["fondo"])
        botones_accion.pack(fill="x", pady=10)
        boton_exito(botones_accion,   "✅ Confirmar alquiler", self._confirmar,          ancho=22).pack(side="left", padx=(0, 8))
        boton_primario(botones_accion,"🔍 Ver resumen",        self._actualizar_resumen, ancho=16).pack(side="left")

    def _cargar_vehiculos(self):
        self._todos_vehiculos = self._v_negocio.obtener_disponibles()
        self._poblar(self._todos_vehiculos)

    def _poblar(self, lista):
        self._tabla.delete(*self._tabla.get_children())
        for indice, vehiculo in enumerate(lista):
            tag = "par" if indice % 2 == 0 else "impar"
            self._tabla.insert("", "end", values=(
                vehiculo.numero_placa, vehiculo.marca, vehiculo.modelo, vehiculo.tipo,
                vehiculo.transmision, vehiculo.combustible, vehiculo.cantidad_pasajeros,
                f"₡{vehiculo.costo_diario:,.2f}"
            ), tags=(tag,))

    def _aplicar_filtros(self):
        tipo   = self._var_tipo.get()
        texto  = self._var_busqueda.get().strip().lower()
        resultado = self._todos_vehiculos

        if tipo != "Todos":
            resultado = [vehiculo for vehiculo in resultado if vehiculo.tipo == tipo]
        if texto:
            resultado = [vehiculo for vehiculo in resultado
                         if texto in vehiculo.marca.lower()
                         or texto in vehiculo.modelo.lower()
                         or texto in vehiculo.numero_placa.lower()]
        self._poblar(resultado)

    def _limpiar_filtros(self):
        self._var_tipo.set("Todos")
        self._var_busqueda.set("")
        self._poblar(self._todos_vehiculos)

    def _verificar_cliente(self):
        id_cliente = self._obtener_id_cliente_ingresado()
        if not id_cliente:
            self._lbl_cliente.config(text="")
            messagebox.showwarning(
                "Requerido",
                "Seleccione un cliente del listado o ingrese el ID manual.",
                parent=self
            )
            return

        cliente = self._c_negocio.buscar(id_cliente)
        if not cliente:
            self._lbl_cliente.config(text="Cliente no encontrado.", fg=COLORES["peligro"])
            return
        if not cliente.activo:
            self._lbl_cliente.config(text="El cliente está inactivo.", fg=COLORES["peligro"])
            return
        if not cliente.es_mayor_de_edad(18):
            self._lbl_cliente.config(text="El cliente debe ser mayor de 18 años.", fg=COLORES["peligro"])
            return

        self._id_cliente = cliente.identificacion
        self._lbl_cliente.config(text=f"✔ {cliente.nombre_completo()}", fg=COLORES["exito"])
        self._precargar_alquiler_pendiente(cliente.identificacion)

    def _cargar_clientes_activos(self):
        self._clientes_combo_map = {}
        try:
            clientes = self._c_negocio.obtener_activos()
        except Exception:
            clientes = []

        opciones = [""]
        for cliente in clientes:
            identificacion = str(cliente.identificacion)
            opcion = f"{identificacion} - {cliente.nombre_completo()}"
            self._clientes_combo_map[opcion] = identificacion
            opciones.append(opcion)

        self._combo_cliente["values"] = opciones
        self._combo_cliente.current(0)

    def _obtener_id_cliente_ingresado(self):
        if hasattr(self, "_entry_cliente"):
            id_manual = self._entry_cliente.get().strip()
            if id_manual:
                return id_manual

        if hasattr(self, "_var_cliente_combo"):
            seleccionado = self._var_cliente_combo.get().strip()
            if seleccionado:
                return self._clientes_combo_map.get(
                    seleccionado,
                    seleccionado.split(" - ", 1)[0].strip()
                )
        return ""

    def _precargar_alquiler_pendiente(self, id_cliente):
        historial = self._negocio.obtener_historial_cliente(id_cliente)
        alquiler_pendiente = next(
            (alquiler for alquiler in historial if alquiler.estado == "Pendiente"), None)

        if not alquiler_pendiente:
            return

        self._entry_inicio.delete(0, tk.END)
        self._entry_inicio.insert(0, str(alquiler_pendiente.fecha_inicio))

        self._entry_fin.delete(0, tk.END)
        self._entry_fin.insert(0, str(alquiler_pendiente.fecha_devolucion_planificada))

        self._seleccionar_vehiculo_en_tabla(alquiler_pendiente.id_vehiculo)

        self._lbl_cliente.config(
            text=f"✔ {self._c_negocio.buscar(id_cliente).nombre_completo()} — Alquiler pendiente cargado.",
            fg=COLORES["exito"])

    def _seleccionar_vehiculo_en_tabla(self, placa_vehiculo):
        self._limpiar_filtros()
        for fila in self._tabla.get_children():
            valores = self._tabla.item(fila)["values"]
            if str(valores[0]) == str(placa_vehiculo):
                self._tabla.selection_set(fila)
                self._tabla.see(fila)
                return

    def _placa_seleccionada(self):
        seleccion = self._tabla.selection()
        if not seleccion:
            return None
        try:
            return self._tabla.item(seleccion[0])["values"][0]
        except (TypeError, IndexError, KeyError):
            return None

    def _actualizar_resumen(self):
        placa  = self._placa_seleccionada()
        inicio = self._entry_inicio.get().strip()
        fin    = self._entry_fin.get().strip()

        if not placa:
            messagebox.showwarning("Requerido", "Seleccione un vehículo de la tabla.", parent=self)
            return
        if not inicio or not fin:
            messagebox.showwarning("Requerido", "Ingrese las fechas de inicio y devolución.", parent=self)
            return
        try:
            dias     = self._negocio.calcular_dias(inicio, fin)
            vehiculo = self._v_negocio.buscar(str(placa))
            calculo  = self._negocio.calcular_costo(vehiculo.costo_diario, dias)
            texto = (f"Vehículo: {vehiculo.descripcion()}   |   "
                     f"Días: {calculo['cantidad_dias']}   |   "
                     f"Base: ₡{calculo['costo_base']:,.2f}   |   "
                     f"Impuesto (13%): ₡{calculo['impuesto']:,.2f}   |   "
                     f"Seguro: ₡{calculo['costo_seguro']:,.2f}   |   "
                     f"TOTAL: ₡{calculo['total']:,.2f}")
            self._lbl_resumen.config(text=texto, fg=COLORES["texto"])
        except Exception as error:
            self._lbl_resumen.config(text=str(error), fg=COLORES["peligro"])

    def _confirmar(self):
        placa  = self._placa_seleccionada()
        inicio = self._entry_inicio.get().strip()
        fin    = self._entry_fin.get().strip()

        if not self._id_cliente:
            messagebox.showwarning("Requerido", "Verifique el cliente primero.", parent=self)
            return
        if not placa:
            messagebox.showwarning("Requerido", "Seleccione un vehículo.", parent=self)
            return
        if not inicio or not fin:
            messagebox.showwarning("Requerido", "Ingrese las fechas.", parent=self)
            return
        try:
            id_alquiler = self._negocio.registrar_alquiler(
                self._id_cliente, str(placa), inicio, fin,
                es_funcionario=self._usuario.es_funcionario()
            )
            messagebox.showinfo("Éxito",
                f"Alquiler registrado correctamente.\nN° de alquiler: {id_alquiler}", parent=self)
            self._entry_inicio.delete(0, tk.END)
            self._entry_fin.delete(0, tk.END)
            self._lbl_resumen.config(
                text="Seleccione fechas y vehículo, luego presione 'Ver resumen'.",
                fg=COLORES["texto_suave"])
            self._cargar_vehiculos()
        except ValueError as error:
            messagebox.showwarning("No permitido", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)