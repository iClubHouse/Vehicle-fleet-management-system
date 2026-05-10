import tkinter as tk
from tkinter import ttk, messagebox
from interfaz.estilos import (COLORES, FUENTES, boton_primario,
                               boton_peligro, boton_secundario, boton_exito,
                               centrar_ventana)
from negocio.entidades_negocio import VehiculoNegocio
from entidades.vehiculo import Vehiculo

## Módulo de mantenimiento de vehículos
class MantenimientoVehiculos(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._negocio = VehiculoNegocio()
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        tk.Label(self, text="Mantenimiento de Vehículos", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(anchor="w", pady=(0, 10))
        tk.Frame(self, bg=COLORES["acento"], height=2).pack(fill="x", pady=(0, 12))

        barra = tk.Frame(self, bg=COLORES["fondo"])
        barra.pack(fill="x", pady=(0, 10))

        boton_exito(barra,    "➕ Agregar",        self._agregar,        ancho=14).pack(side="left", padx=(0, 6))
        boton_primario(barra, "✏ Editar",          self._editar,         ancho=14).pack(side="left", padx=(0, 6))
        boton_peligro(barra,  "🔒 Cambiar estado", self._cambiar_estado, ancho=16).pack(side="left")

        tk.Label(barra, text="Buscar:", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["normal"]).pack(side="right", padx=(10, 4))
        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *a: self._filtrar())
        tk.Entry(barra, textvariable=self._var_busqueda, font=FUENTES["normal"],
                 bg=COLORES["blanco"], relief="solid", bd=1, width=22).pack(side="right", ipady=4)

        cols  = ("Placa", "Marca", "Modelo", "Tipo", "Transmisión", "Combustible", "Pasajeros", "Costo/día", "Disponible")
        self._tabla = ttk.Treeview(self, columns=cols, show="headings", height=18)
        anchos = [90, 100, 110, 90, 100, 90, 80, 90, 80]
        for col, ancho in zip(cols, anchos):
            self._tabla.heading(col, text=col, anchor="center")
            self._tabla.column(col, width=ancho, anchor="center")

        self._tabla.tag_configure("par",   background=COLORES["tabla_par"])
        self._tabla.tag_configure("impar", background=COLORES["tabla_impar"])

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._tabla.pack(fill="both", expand=True)
        self._tabla.bind("<Double-1>", lambda e: self._editar())

        self._todos = []

    def _cargar_tabla(self):
        self._todos = self._negocio.obtener_todos()
        self._poblar(self._todos)

    def _poblar(self, lista):
        self._tabla.delete(*self._tabla.get_children())
        for indice, vehiculo in enumerate(lista):
            tag = "par" if indice % 2 == 0 else "impar"
            self._tabla.insert("", "end", values=(
                vehiculo.numero_placa, vehiculo.marca, vehiculo.modelo, vehiculo.tipo,
                vehiculo.transmision, vehiculo.combustible, vehiculo.cantidad_pasajeros,
                f"₡{vehiculo.costo_diario:,.2f}",
                "Sí" if vehiculo.disponible else "No"
            ), tags=(tag,))

    def _filtrar(self):
        texto = self._var_busqueda.get().strip().lower()
        if not texto:
            self._poblar(self._todos)
        else:
            filtrados = [vehiculo for vehiculo in self._todos
                         if texto in vehiculo.numero_placa.lower()
                         or texto in vehiculo.marca.lower()
                         or texto in vehiculo.modelo.lower()]
            self._poblar(filtrados)

    def _seleccionado_placa(self):
        seleccion = self._tabla.selection()
        if not seleccion:
            messagebox.showinfo("Selección", "Seleccione un vehículo de la tabla.", parent=self)
            return None
        return self._tabla.item(seleccion[0])["values"][0]

    def _vehiculo_seleccionado(self):
        placa = self._seleccionado_placa()
        if not placa:
            return None
        return self._negocio.buscar(str(placa))

    def _agregar(self):
        dialogo = DialogoVehiculo(self, "Agregar vehículo")
        self.wait_window(dialogo)
        self._cargar_tabla()

    def _editar(self):
        placa = self._seleccionado_placa()
        if not placa:
            return
        dialogo = DialogoVehiculo(self, "Editar vehículo", placa=str(placa))
        self.wait_window(dialogo)
        self._cargar_tabla()

    def _cambiar_estado(self):
        vehiculo = self._vehiculo_seleccionado()
        if not vehiculo:
            return
        estado_nuevo = "Inactivo" if vehiculo.disponible else "Activo"
        if not messagebox.askyesno("Confirmar",
                f"¿Cambiar estado de {vehiculo.numero_placa} a '{estado_nuevo}'?", parent=self):
            return
        try:
            if vehiculo.disponible:
                self._negocio.desactivar(vehiculo.numero_placa)
            else:
                self._negocio.reactivar(vehiculo.numero_placa)
            messagebox.showinfo("Listo", f"Estado cambiado a '{estado_nuevo}'.", parent=self)
            self._cargar_tabla()
        except ValueError as error:
            messagebox.showwarning("No permitido", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)


## Diálogo para agregar/editar vehículo
class DialogoVehiculo(tk.Toplevel):

    def __init__(self, parent, titulo, placa=None):
        super().__init__(parent)
        self.title(f"AutoTrust - {titulo}")
        self.configure(bg=COLORES["fondo"])
        self.resizable(False, False)
        self._placa   = placa
        self._negocio = VehiculoNegocio()
        self._campos  = {}
        self._construir()
        centrar_ventana(self, 520, 580)
        self.grab_set()
        if placa:
            self._cargar_datos()

    def _construir(self):
        encabezado = tk.Frame(self, bg=COLORES["primario"], pady=10)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text=self.title().replace("AutoTrust - ", ""),
                 bg=COLORES["primario"], fg=COLORES["blanco"],
                 font=FUENTES["subtitulo"]).pack()

        contenido = tk.Frame(self, bg=COLORES["fondo"], padx=24, pady=16)
        contenido.pack(fill="both", expand=True)

        def fila(etiqueta, clave, tipo="entry", opciones=None):
            fila_frame = tk.Frame(contenido, bg=COLORES["fondo"])
            fila_frame.pack(fill="x", pady=4)
            tk.Label(fila_frame, text=etiqueta, bg=COLORES["fondo"], fg=COLORES["texto"],
                     font=FUENTES["etiqueta"], width=24, anchor="w").pack(side="left")
            if tipo == "entry":
                widget = tk.Entry(fila_frame, font=FUENTES["normal"], bg=COLORES["blanco"],
                                  relief="solid", bd=1)
                widget.pack(side="left", fill="x", expand=True, ipady=5)
            elif tipo == "combo":
                widget = tk.StringVar(value=opciones[0])
                tk.OptionMenu(fila_frame, widget, *opciones).pack(side="left", fill="x", expand=True)
            self._campos[clave] = widget

        fila("Número de placa *",    "numero_placa")
        fila("Marca *",              "marca")
        fila("Modelo *",             "modelo")
        fila("Tipo",                 "tipo",        "combo", Vehiculo.TIPOS)
        fila("Transmisión",          "transmision", "combo", Vehiculo.TRANSMISIONES)
        fila("Combustible",          "combustible", "combo", Vehiculo.COMBUSTIBLES)
        fila("Color",                "color")
        fila("Cantidad pasajeros *", "cantidad_pasajeros")
        fila("Cantidad maletas",     "cantidad_maletas")
        fila("Costo diario (₡) *",   "costo_diario")
        fila("Número de motor *",    "numero_motor")

        if self._placa:
            self._campos["numero_placa"].config(state="disabled")

        botones = tk.Frame(contenido, bg=COLORES["fondo"])
        botones.pack(fill="x", pady=14)
        boton_exito(botones,      "💾 Guardar", self._guardar, ancho=16).pack(side="left", padx=4)
        boton_secundario(botones, "Cancelar",   self.destroy,  ancho=16).pack(side="left", padx=4)

    def _get(self, clave):
        widget = self._campos[clave]
        return widget.get() if isinstance(widget, tk.StringVar) else widget.get().strip()

    def _cargar_datos(self):
        vehiculo = self._negocio.buscar(self._placa)
        if not vehiculo:
            return
        mapeo = {
            "marca":              vehiculo.marca,
            "modelo":             vehiculo.modelo,
            "color":              vehiculo.color,
            "cantidad_pasajeros": str(vehiculo.cantidad_pasajeros),
            "cantidad_maletas":   str(vehiculo.cantidad_maletas),
            "costo_diario":       str(vehiculo.costo_diario),
            "numero_motor":       vehiculo.numero_motor,
        }
        for clave, valor in mapeo.items():
            widget = self._campos[clave]
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, valor)
        for clave, valor in [("tipo", vehiculo.tipo), ("transmision", vehiculo.transmision),
                              ("combustible", vehiculo.combustible)]:
            if isinstance(self._campos[clave], tk.StringVar):
                self._campos[clave].set(valor)

    def _guardar(self):
        try:
            if self._placa:
                datos = {
                    "marca":              self._get("marca"),
                    "modelo":             self._get("modelo"),
                    "tipo":               self._get("tipo"),
                    "transmision":        self._get("transmision"),
                    "combustible":        self._get("combustible"),
                    "color":              self._get("color"),
                    "cantidad_pasajeros": int(self._get("cantidad_pasajeros") or 0),
                    "cantidad_maletas":   int(self._get("cantidad_maletas") or 0),
                    "costo_diario":       float(self._get("costo_diario") or 0),
                    "numero_motor":       self._get("numero_motor"),
                }
                self._negocio.actualizar(self._placa, datos)
            else:
                vehiculo = Vehiculo(
                    numero_placa=self._get("numero_placa"),
                    marca=self._get("marca"),
                    modelo=self._get("modelo"),
                    tipo=self._get("tipo"),
                    transmision=self._get("transmision"),
                    combustible=self._get("combustible"),
                    color=self._get("color"),
                    cantidad_pasajeros=int(self._get("cantidad_pasajeros") or 0),
                    cantidad_maletas=int(self._get("cantidad_maletas") or 0),
                    costo_diario=float(self._get("costo_diario") or 0),
                    numero_motor=self._get("numero_motor"),
                )
                self._negocio.registrar(vehiculo)

            messagebox.showinfo("Guardado", "Vehículo guardado correctamente.", parent=self)
            self.destroy()
        except ValueError as error:
            messagebox.showwarning("Validación", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)