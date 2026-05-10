import tkinter as tk
from tkinter import messagebox
from interfaz.estilos import COLORES, FUENTES, aplicar_tema, crear_topbar
from datos.mongo_dao import ClienteDAO
from interfaz.ventana_consulta import VentanaConsulta
from interfaz.ventana_alquiler import VentanaAlquiler
from interfaz.ventana_historial import VentanaHistorial
from interfaz.mant_clientes import DialogoCliente
from interfaz.ventana_acerca import VentanaAcerca

class MenuCliente(tk.Toplevel):

    MODULOS = [
        ("vehiculos",  "🚗", "Vehículos disponibles", "_vehiculos_disponibles"),
        ("alquiler",   "📋", "Solicitar alquiler",    "_solicitar_alquiler"),
        ("historial",  "📂", "Mis alquileres",        "_historial"),
        ("---", None, None, None),
        ("mis_datos",  "👤", "Mis datos",             "_mis_datos"),
        ("acerca",     "ℹ",  "Acerca de",             "_acerca"),
    ]

    def __init__(self, master, login, usuario):
        super().__init__(master)
        self._master  = master
        self._login   = login
        self._usuario = usuario
        self._cliente = self._cargar_cliente()
        self._activo  = None
        self._btns    = {}

        self.title("AutoTrust S.A. — Portal Cliente")
        self.configure(bg=COLORES["fondo_sidebar"])
        self.state("zoomed")
        self._construir()
        self.protocol("WM_DELETE_WINDOW", self._salir)
        self._vehiculos_disponibles()

    def _cargar_cliente(self):
        try:
            return ClienteDAO()._col.find_one({"_id": self._usuario.id_perfil})
        except Exception:
            return None

    def _nombre_cliente(self):
        if self._cliente:
            return f"{self._cliente.get('nombre','')} {self._cliente.get('primer_apellido','')}".strip()
        return self._usuario.nombre_usuario

    def _construir(self):
        crear_topbar(self, titulo="Portal Cliente",
                     usuario=self._nombre_cliente())

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

        circulo = tk.Frame(perfil, bg="#1E8449", width=44, height=44)
        circulo.pack()
        circulo.pack_propagate(False)
        inicial = self._nombre_cliente()[0].upper() if self._nombre_cliente() else "C"
        tk.Label(circulo, text=inicial, bg="#1E8449",
                 fg=COLORES["blanco"], font=("Segoe UI", 16, "bold")).pack(expand=True)

        tk.Label(perfil, text=self._nombre_cliente(),
                 bg=COLORES["fondo_sidebar"], fg=COLORES["blanco"],
                 font=FUENTES["negrita"]).pack(pady=(8, 2))
        tk.Label(perfil, text="Cliente",
                 bg=COLORES["fondo_sidebar"], fg=COLORES["texto_sidebar"],
                 font=FUENTES["mini"]).pack()

        tk.Frame(self._sidebar, bg=COLORES["sidebar_separador"],
                 height=1).pack(fill="x", padx=16, pady=(10, 6))

        for clave, icono, etiqueta, _ in self.MODULOS:
            if clave == "---":
                tk.Frame(self._sidebar, bg=COLORES["sidebar_separador"],
                         height=1).pack(fill="x", padx=16, pady=6)
                continue
            btn = self._item_sidebar(clave, icono, etiqueta)
            self._btns[clave] = btn

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

    ## ─────────────────────────────────────────────────────────────
    ##  Marcado de módulo activo y navegación
    ## ─────────────────────────────────────────────────────────────
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

    ## ─────────────────────────────────────────────────────────────
    ##  _activar: actualiza sidebar Y llama al módulo.
    ## ─────────────────────────────────────────────────────────────
    def _activar(self, clave):
        self._marcar_activo(clave)
        metodo = next((m for c, _, _, m in self.MODULOS if c == clave), None)
        if metodo:
            getattr(self, metodo)()

    def _limpiar(self):
        for widget in self._frame_contenido.winfo_children():
            widget.destroy()

    ## ─────────────────────────────────────────────────────────────────────
    ##  Módulos: usan _marcar_activo (no _activar) para evitar recursividad
    ## ─────────────────────────────────────────────────────────────────────
    def _vehiculos_disponibles(self):
        self._marcar_activo("vehiculos")
        self._limpiar()
        VentanaConsulta(self._frame_contenido)

    def _solicitar_alquiler(self):
        self._marcar_activo("alquiler")
        self._limpiar()
        if self._cliente:
            VentanaAlquiler(self._frame_contenido, self._usuario,
                            self._cliente.get("identificacion"))
        else:
            tk.Label(self._frame_contenido,
                     text="No se encontraron datos del cliente.",
                     bg=COLORES["fondo"], fg=COLORES["texto"]).pack(pady=20)

    def _historial(self):
        self._marcar_activo("historial")
        self._limpiar()
        if self._cliente:
            VentanaHistorial(self._frame_contenido,
                             self._cliente.get("identificacion"))
        else:
            tk.Label(self._frame_contenido,
                     text="No se encontraron datos.",
                     bg=COLORES["fondo"], fg=COLORES["texto"]).pack(pady=20)

    def _mis_datos(self):
        self._marcar_activo("mis_datos")
        self._limpiar()
        if self._cliente:
            identificacion = self._cliente.get("identificacion", "")
            dialogo = DialogoCliente(self, "Mis datos", identificacion=identificacion)
            ## Espera a que el diálogo se cierre antes de continuar
            self.wait_window(dialogo)
            ## Refresca los datos del cliente en caso de que haya editado su información
            self._cliente = self._cargar_cliente()
        else:
            tk.Label(self._frame_contenido,
                     text="No se encontraron datos del cliente.",
                     bg=COLORES["fondo"], fg=COLORES["texto"]).pack(pady=20)

    def _acerca(self):
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