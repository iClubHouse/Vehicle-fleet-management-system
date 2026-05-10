import tkinter as tk
from tkinter import ttk, messagebox
from interfaz.estilos import (COLORES, FUENTES, boton_primario,
                               boton_peligro, boton_secundario)
from negocio.alquiler_negocio import AlquilerNegocio

## Ventana de gestión de estado de alquileres
class VentanaEstadoAlquiler(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._negocio = AlquilerNegocio()
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        tk.Label(self, text="Estado de Alquileres", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(anchor="w", pady=(0, 10))
        tk.Frame(self, bg=COLORES["acento"], height=2).pack(fill="x", pady=(0, 12))

        barra = tk.Frame(self, bg=COLORES["fondo"])
        barra.pack(fill="x", pady=(0, 10))

        boton_primario(barra, "▶ Activar (En préstamo)", self._activar,     ancho=22).pack(side="left", padx=(0, 8))
        boton_peligro(barra,  "✖ Cancelar alquiler",     self._cancelar,    ancho=20).pack(side="left", padx=(0, 8))
        boton_secundario(barra,"🔄 Actualizar",           self._cargar_tabla, ancho=14).pack(side="left")

        columnas = ("ID", "Cliente", "Vehículo", "F. Inicio", "F. Devolución", "Días", "Total", "Estado")
        self._tabla = ttk.Treeview(self, columns=columnas, show="headings", height=20)
        anchos = [60, 130, 110, 100, 110, 50, 110, 100]
        for columna, ancho in zip(columnas, anchos):
            self._tabla.heading(columna, text=columna, anchor="center")
            self._tabla.column(columna, width=ancho, anchor="center")

        self._tabla.tag_configure("par",       background=COLORES["tabla_par"])
        self._tabla.tag_configure("impar",     background=COLORES["tabla_impar"])
        self._tabla.tag_configure("prestamo",  background="#D5F5E3")
        self._tabla.tag_configure("pendiente", background="#FEF9E7")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._tabla.pack(fill="both", expand=True)

        self._alquileres = []

    def _cargar_tabla(self):
        self._alquileres = self._negocio.obtener_pendientes_en_prestamo()
        self._tabla.delete(*self._tabla.get_children())
        for indice, alquiler in enumerate(self._alquileres):
            if alquiler.estado == "En préstamo":
                etiqueta = "prestamo"
            elif alquiler.estado == "Pendiente":
                etiqueta = "pendiente"
            else:
                etiqueta = "par" if indice % 2 == 0 else "impar"
            self._tabla.insert("", "end", iid=str(alquiler.id_alquiler), values=(
                alquiler.id_alquiler, alquiler.id_cliente, alquiler.id_vehiculo,
                str(alquiler.fecha_inicio), str(alquiler.fecha_devolucion_planificada),
                alquiler.cantidad_dias, f"₡{alquiler.total:,.2f}", alquiler.estado
            ), tags=(etiqueta,))

    def _obtener_seleccionado(self):
        seleccion = self._tabla.selection()
        if not seleccion:
            messagebox.showinfo("Selección", "Seleccione un alquiler de la tabla.", parent=self)
            return None
        return int(seleccion[0])

    def _activar(self):
        id_alquiler = self._obtener_seleccionado()
        if id_alquiler is None:
            return
        alquiler = next((a for a in self._alquileres if a.id_alquiler == id_alquiler), None)
        if not alquiler:
            return
        if alquiler.estado != "Pendiente":
            messagebox.showwarning("No permitido",
                "Solo se pueden activar alquileres en estado 'Pendiente'.", parent=self)
            return
        if not messagebox.askyesno("Confirmar",
                f"¿Activar alquiler #{id_alquiler} como 'En préstamo'?", parent=self):
            return
        try:
            self._negocio.activar_alquiler(id_alquiler)
            messagebox.showinfo("Listo", "Alquiler activado correctamente.", parent=self)
            self._cargar_tabla()
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)

    def _cancelar(self):
        id_alquiler = self._obtener_seleccionado()
        if id_alquiler is None:
            return
        alquiler = next((a for a in self._alquileres if a.id_alquiler == id_alquiler), None)
        if not alquiler:
            return
        if alquiler.estado != "Pendiente":
            messagebox.showwarning("No permitido",
                "Solo se pueden cancelar alquileres en estado 'Pendiente'.", parent=self)
            return
        if not messagebox.askyesno("Confirmar",
                f"¿Cancelar el alquiler #{id_alquiler}? Esta acción no se puede deshacer.",
                parent=self):
            return
        try:
            self._negocio.cancelar_alquiler(id_alquiler)
            messagebox.showinfo("Listo", "Alquiler cancelado y vehículo liberado.", parent=self)
            self._cargar_tabla()
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)