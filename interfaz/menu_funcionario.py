import tkinter as tk
from tkinter import messagebox
from interfaz.estilos import COLORES, FUENTES, aplicar_tema, crear_topbar
from interfaz.mant_clientes import MantenimientoClientes
from interfaz.mant_funcionarios import MantenimientoFuncionarios
from interfaz.mant_vehiculos import MantenimientoVehiculos
from interfaz.mant_imagenes import MantenimientoImagenes
from interfaz.ventana_alquiler import VentanaAlquiler
from interfaz.ventana_estado_alquiler import VentanaEstadoAlquiler
from interfaz.ventana_devolucion import VentanaDevolucion
from interfaz.ventana_reportes import VentanaReportes
from interfaz.ventana_acerca import VentanaAcerca

class MenuFuncionario(tk.Toplevel):

    MODULOS = [
        ("clientes",     "👥", "Clientes",           "_modulo_clientes"),
        ("funcionarios", "🧑‍💼", "Funcionarios",       "_modulo_funcionarios"),
        ("vehiculos",    "🚗", "Vehículos",           "_modulo_vehiculos"),
        ("imagenes",     "🖼",  "Imágenes",            "_modulo_imagenes"),
        ("---", None, None, None),
        ("alquileres",   "📋", "Alquileres",          "_modulo_alquileres"),
        ("estado_alq",   "🔄", "Estado Alquileres",   "_modulo_estado_alquileres"),
        ("devoluciones", "↩",  "Devoluciones",        "_modulo_devoluciones"),
        ("reportes",     "📊", "Reportes",            "_modulo_reportes"),
        ("---", None, None, None),
        ("acerca",       "ℹ",  "Acerca de",           "_modulo_acerca"),
    ]

    def __init__(self, master, login, usuario):
        super().__init__(master)
        self._master  = master
        self._login   = login
        self._usuario = usuario
        self._activo  = None
        self._btns    = {}

        self.title("AutoTrust S.A. — Panel Funcionario")
        self.configure(bg=COLORES["fondo_sidebar"])
        self.state("zoomed")
        self._construir()
        self.protocol("WM_DELETE_WINDOW", self._salir)
        self._modulo_clientes()

    def _construir(self):
        crear_topbar(self, titulo="Panel Funcionario",
                     usuario=self._usuario.nombre_usuario)

        contenedor = tk.Frame(self, bg=COLORES["fondo"])
        contenedor.pack(fill="both", expand=True)

        self._sidebar = tk.Frame(contenedor, bg=COLORES["fondo_sidebar"], width=220)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        self._frame_contenido = tk.Frame(contenedor, bg=COLORES["fondo"])
        self._frame_contenido.pack(side="left", fill="both", expand=True)

        self._construir_sidebar()

    def _construir_sidebar(self):
        ## Perfil
        perfil = tk.Frame(self._sidebar, bg=COLORES["fondo_sidebar"], pady=22)
        perfil.pack(fill="x", padx=16)

        circulo = tk.Frame(perfil, bg=COLORES["acento"], width=44, height=44)
        circulo.pack()
        circulo.pack_propagate(False)
        inicial = self._usuario.nombre_usuario[0].upper()
        tk.Label(circulo, text=inicial, bg=COLORES["acento"],
                 fg=COLORES["blanco"], font=("Segoe UI", 16, "bold")).pack(expand=True)

        tk.Label(perfil, text=self._usuario.nombre_usuario,
                 bg=COLORES["fondo_sidebar"], fg=COLORES["blanco"],
                 font=FUENTES["negrita"]).pack(pady=(8, 2))
        tk.Label(perfil, text="Funcionario",
                 bg=COLORES["fondo_sidebar"], fg=COLORES["texto_sidebar"],
                 font=FUENTES["mini"]).pack()

        tk.Frame(self._sidebar, bg=COLORES["sidebar_separador"],
                 height=1).pack(fill="x", padx=16, pady=(10, 6))

        ## Items del menú
        for clave, icono, etiqueta, _ in self.MODULOS:
            if clave == "---":
                tk.Frame(self._sidebar, bg=COLORES["sidebar_separador"],
                         height=1).pack(fill="x", padx=16, pady=6)
                continue
            btn = self._item_sidebar(clave, icono, etiqueta)
            self._btns[clave] = btn

        ## Botón cerrar sesión al fondo
        tk.Frame(self._sidebar, bg=COLORES["fondo_sidebar"]).pack(expand=True)
        tk.Frame(self._sidebar, bg=COLORES["sidebar_separador"],
                 height=1).pack(fill="x", padx=16, pady=4)
        btn_salir = tk.Button(
            self._sidebar,
            text="  🚪  Cerrar Sesión",
            command=self._cerrar_sesion,
            bg=COLORES["fondo_sidebar"], fg="#E74C3C",
            font=FUENTES["normal"],
            relief="flat", cursor="hand2",
            anchor="w", padx=20, pady=10, bd=0,
            activebackground=COLORES["sidebar_hover"],
            activeforeground="#E74C3C",
        )
        btn_salir.pack(fill="x", pady=(0, 10))
        btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg=COLORES["sidebar_hover"]))
        btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg=COLORES["fondo_sidebar"]))

    def _item_sidebar(self, clave, icono, etiqueta):
        ## Crea un botón para el sidebar con comportamiento de hover y activo
        btn = tk.Button(
            self._sidebar,
            text=f"  {icono}  {etiqueta}",
            command=lambda c=clave: self._activar(c),
            bg=COLORES["fondo_sidebar"], fg=COLORES["texto_sidebar"],
            font=FUENTES["normal"],
            relief="flat", cursor="hand2",
            anchor="w", padx=20, pady=9, bd=0,
            activebackground=COLORES["sidebar_activo"],
            activeforeground=COLORES["blanco"],
        )
        btn.pack(fill="x", padx=8, pady=1)
        btn.bind("<Enter>", lambda e, b=btn, k=clave: b.config(
            bg=COLORES["sidebar_hover"], fg=COLORES["blanco"])
            if k != self._activo else None)
        btn.bind("<Leave>", lambda e, b=btn, k=clave: b.config(
            bg=COLORES["sidebar_activo"] if k == self._activo else COLORES["fondo_sidebar"],
            fg=COLORES["blanco"] if k == self._activo else COLORES["texto_sidebar"])
        )
        return btn

    ## ──────────────────────────────────────────────────────────────────────────
    ##  _marcar_activo: actualiza el estado visual del botón activo en el sidebar
    ## ──────────────────────────────────────────────────────────────────────────
    def _marcar_activo(self, clave):
        if self._activo and self._activo in self._btns:
            self._btns[self._activo].config(
                bg=COLORES["fondo_sidebar"],
                fg=COLORES["texto_sidebar"])
        self._activo = clave
        if clave in self._btns:
            self._btns[clave].config(
                bg=COLORES["sidebar_activo"],
                fg=COLORES["blanco"])

    ## ─────────────────────────────────────────────────────────────────────────────────────────────
    ##  _activar: marca el módulo activo y llama al método correspondiente para mostrar su contenido
    ## ─────────────────────────────────────────────────────────────────────────────────────────────
    def _activar(self, clave):
        self._marcar_activo(clave)
        metodo = next((m for c, _, _, m in self.MODULOS if c == clave), None)
        if metodo:
            getattr(self, metodo)()

    def _limpiar(self):
        for w in self._frame_contenido.winfo_children():
            w.destroy()

    ## ────────────────────────────────────────────────────────────────────
    ##  Módulos: usan _marcar_activo (no _activar) para evitar recursividad
    ## ────────────────────────────────────────────────────────────────────
    def _modulo_clientes(self):
        self._marcar_activo("clientes")
        self._limpiar()
        MantenimientoClientes(self._frame_contenido)

    def _modulo_funcionarios(self):
        self._marcar_activo("funcionarios")
        self._limpiar()
        MantenimientoFuncionarios(self._frame_contenido)

    def _modulo_vehiculos(self):
        self._marcar_activo("vehiculos")
        self._limpiar()
        MantenimientoVehiculos(self._frame_contenido)

    def _modulo_imagenes(self):
        self._marcar_activo("imagenes")
        self._limpiar()
        MantenimientoImagenes(self._frame_contenido)

    def _modulo_alquileres(self):
        self._marcar_activo("alquileres")
        self._limpiar()
        VentanaAlquiler(self._frame_contenido, self._usuario)

    def _modulo_estado_alquileres(self):
        self._marcar_activo("estado_alq")
        self._limpiar()
        VentanaEstadoAlquiler(self._frame_contenido)

    def _modulo_devoluciones(self):
        self._marcar_activo("devoluciones")
        self._limpiar()
        VentanaDevolucion(self._frame_contenido)

    def _modulo_reportes(self):
        self._marcar_activo("reportes")
        self._limpiar()
        VentanaReportes(self._frame_contenido)

    def _modulo_acerca(self):
        self._marcar_activo("acerca")
        self._limpiar()
        VentanaAcerca(self._frame_contenido)

    def _cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión",
                "¿Desea cerrar la sesión?", parent=self):
            self.destroy()
            self._login.deiconify()

    def _salir(self):
        if messagebox.askyesno("Salir",
                "¿Desea salir del sistema?", parent=self):
            self._master.destroy()