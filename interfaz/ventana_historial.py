import tkinter as tk
from tkinter import ttk
from interfaz.estilos import COLORES, FUENTES
from negocio.alquiler_negocio import AlquilerNegocio

## Ventana de historial de alquileres del cliente
class VentanaHistorial(tk.Frame):

    def __init__(self, parent, id_cliente):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._id_cliente = id_cliente
        self._negocio    = AlquilerNegocio()
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        tk.Label(self, text="Mis Alquileres", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(anchor="w", pady=(0, 10))
        tk.Frame(self, bg=COLORES["acento"], height=2).pack(fill="x", pady=(0, 12))

        ## Resumen
        self._frame_resumen = tk.Frame(self, bg=COLORES["fondo_panel"],
                                        padx=16, pady=10, relief="solid", bd=1)
        self._frame_resumen.pack(fill="x", pady=(0, 12))
        self._lbl_resumen = tk.Label(self._frame_resumen, text="",
                                      bg=COLORES["fondo_panel"], fg=COLORES["texto"],
                                      font=FUENTES["normal"])
        self._lbl_resumen.pack(anchor="w")

        ## Tabla
        cols  = ("ID", "Vehículo", "F. Inicio", "F. Devolución", "Días",
                 "Costo base", "Impuesto", "Seguro", "Total", "Estado")
        self._tabla = ttk.Treeview(self, columns=cols, show="headings", height=20)
        anchos = [60, 120, 100, 110, 50, 110, 100, 100, 110, 100]
        for col, ancho in zip(cols, anchos):
            self._tabla.heading(col, text=col, anchor="center")
            self._tabla.column(col, width=ancho, anchor="center")

        self._tabla.tag_configure("Pendiente",   background="#FEF9E7")
        self._tabla.tag_configure("En préstamo", background="#D5F5E3")
        self._tabla.tag_configure("Devuelto",    background="#EBF5FB")
        self._tabla.tag_configure("Cancelado",   background="#FADBD8")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._tabla.pack(fill="both", expand=True)

    def _cargar_tabla(self):
        alquileres = self._negocio.obtener_historial_cliente(self._id_cliente)
        self._tabla.delete(*self._tabla.get_children())

        total_gastado = 0.0
        for a in alquileres:
            self._tabla.insert("", "end", values=(
                a.id_alquiler,
                a.id_vehiculo,
                str(a.fecha_inicio),
                str(a.fecha_devolucion_planificada),
                a.cantidad_dias,
                f"₡{a.costo_base:,.2f}",
                f"₡{a.impuesto:,.2f}",
                f"₡{a.costo_seguro:,.2f}",
                f"₡{a.total:,.2f}",
                a.estado
            ), tags=(a.estado,))
            if a.estado not in ("Cancelado",):
                total_gastado += a.total

        total_alq = len(alquileres)
        activos   = sum(1 for a in alquileres if a.estado in ("Pendiente", "En préstamo"))
        self._lbl_resumen.config(
            text=(f"Total de alquileres: {total_alq}   |   "
                  f"Activos: {activos}   |   "
                  f"Total invertido: ₡{total_gastado:,.2f}"))