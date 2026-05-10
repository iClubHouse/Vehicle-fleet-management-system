import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from datetime import datetime
from interfaz.estilos import (
    COLORES, FUENTES,
    boton_primario, boton_secundario,
    centrar_ventana, entry_moderno, divisor
)
from config.rutas import LOGO_PATH
from datos.mongo_dao import UsuarioDAO
from interfaz.menu_cliente import MenuCliente
from interfaz.menu_funcionario import MenuFuncionario
from interfaz.ventana_registro import VentanaRegistro

class VentanaLogin(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self._master       = master
        self._imagen_logo  = None
        self.title("AutoTrust S.A.")
        self.resizable(False, False)
        self.configure(bg=COLORES["primario"])
        self._construir()
        centrar_ventana(self, 860, 540)
        self.protocol("WM_DELETE_WINDOW", self._salir)

    def _construir(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self._panel_izquierdo()
        self._panel_derecho()

    def _panel_izquierdo(self):
        panel = tk.Frame(self, bg=COLORES["primario"])
        panel.place(x=0, y=0, relwidth=0.46, relheight=1)

        contenedor_central = tk.Frame(panel, bg=COLORES["primario"])
        contenedor_central.place(relx=0.5, rely=0.5, anchor="center")

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
                    contenedor_central,
                    image=self._imagen_logo,
                    bg=COLORES["primario"]
                ).pack(pady=(0, 14))
            except Exception:
                self._imagen_logo = None

        
        tk.Frame(contenedor_central, bg="#1A3A52", height=2, width=160).pack(pady=18)

        tk.Label(
            contenedor_central,
            text="Gestión de Flotilla Vehicular",
            bg=COLORES["primario"],
            fg=COLORES["texto_sidebar"],
            font=FUENTES["normal"],
            wraplength=200,
            justify="center"
        ).pack()

        tk.Label(
            panel,
            text="v1.0.0  ·  2026",
            bg=COLORES["primario"],
            fg="#1A3A52",
            font=FUENTES["mini"]
        ).place(relx=0.5, rely=0.97, anchor="s")

    def _panel_derecho(self):
        panel = tk.Frame(self, bg=COLORES["fondo"])
        panel.place(relx=0.46, y=0, relwidth=0.54, relheight=1)

        tarjeta = tk.Frame(
            panel,
            bg=COLORES["fondo_panel"],
            highlightthickness=1,
            highlightbackground=COLORES["borde"]
        )
        tarjeta.place(relx=0.5, rely=0.5, anchor="center", width=320)

        cabecera = tk.Frame(tarjeta, bg=COLORES["acento"], pady=18)
        cabecera.pack(fill="x")

        tk.Label(
            cabecera,
            text="Iniciar Sesión",
            bg=COLORES["acento"],
            fg=COLORES["blanco"],
            font=FUENTES["subtitulo"]
        ).pack()

        tk.Label(
            cabecera,
            text="Bienvenido de nuevo",
            bg=COLORES["acento"],
            fg="#D6EAF8",
            font=FUENTES["mini"]
        ).pack(pady=(2, 0))

        cuerpo = tk.Frame(tarjeta, bg=COLORES["fondo_panel"], padx=28, pady=24)
        cuerpo.pack(fill="x")

        tk.Label(
            cuerpo,
            text="Usuario",
            bg=COLORES["fondo_panel"],
            fg=COLORES["texto_suave"],
            font=FUENTES["pequena"]
        ).pack(anchor="w")

        self._entry_usuario = entry_moderno(cuerpo)
        self._entry_usuario.pack(fill="x", ipady=7, pady=(3, 14))

        tk.Label(
            cuerpo,
            text="Contraseña",
            bg=COLORES["fondo_panel"],
            fg=COLORES["texto_suave"],
            font=FUENTES["pequena"]
        ).pack(anchor="w")

        fila_contrasena = tk.Frame(
            cuerpo,
            bg=COLORES["fondo_panel"],
            highlightthickness=1,
            highlightbackground=COLORES["borde"],
            highlightcolor=COLORES["acento"]
        )
        fila_contrasena.pack(fill="x", pady=(3, 20))

        self._var_mostrar_contrasena = tk.BooleanVar(value=False)

        self._entry_contrasena = tk.Entry(
            fila_contrasena,
            font=FUENTES["campo"],
            bg=COLORES["input_bg"],
            fg=COLORES["texto"],
            relief="flat",
            bd=0,
            show="*",
            insertbackground=COLORES["acento"]
        )
        self._entry_contrasena.pack(side="left", fill="x", expand=True, ipady=7, padx=(8, 0))

        self._btn_ojo = tk.Button(
            fila_contrasena,
            text="👁",
            bg=COLORES["input_bg"],
            fg=COLORES["texto_suave"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 11),
            command=self._toggle_contrasena,
            activebackground=COLORES["input_bg"]
        )
        self._btn_ojo.pack(side="right", padx=6)

        self._entry_usuario.bind("<Return>", lambda e: self._entry_contrasena.focus())
        self._entry_contrasena.bind("<Return>", lambda e: self._ingresar())

        btn_ingresar = tk.Button(
            cuerpo,
            text="  Ingresar  →",
            command=self._ingresar,
            bg=COLORES["acento"],
            fg=COLORES["blanco"],
            font=FUENTES["boton"],
            relief="flat",
            cursor="hand2",
            pady=10,
            bd=0,
            activebackground=COLORES["acento_hover"],
            activeforeground=COLORES["blanco"]
        )
        btn_ingresar.pack(fill="x")
        btn_ingresar.bind("<Enter>", lambda e: btn_ingresar.config(bg=COLORES["acento_hover"]))
        btn_ingresar.bind("<Leave>", lambda e: btn_ingresar.config(bg=COLORES["acento"]))

        separador_frame = tk.Frame(cuerpo, bg=COLORES["fondo_panel"])
        separador_frame.pack(fill="x", pady=16)
        tk.Frame(separador_frame, bg=COLORES["borde"], height=1).pack(side="left", fill="x", expand=True)
        tk.Label(
            separador_frame,
            text="  o  ",
            bg=COLORES["fondo_panel"],
            fg=COLORES["texto_suave"],
            font=FUENTES["mini"]
        ).pack(side="left")
        tk.Frame(separador_frame, bg=COLORES["borde"], height=1).pack(side="left", fill="x", expand=True)

        tk.Label(
            cuerpo,
            text="¿Cliente nuevo?",
            bg=COLORES["fondo_panel"],
            fg=COLORES["texto_suave"],
            font=FUENTES["pequena"]
        ).pack()

        btn_registro = tk.Button(
            cuerpo,
            text="Crear cuenta",
            command=self._abrir_registro,
            bg=COLORES["fondo_panel"],
            fg=COLORES["acento"],
            font=FUENTES["boton"],
            relief="flat",
            cursor="hand2",
            pady=8,
            bd=0,
            activebackground=COLORES["acento_light"],
            activeforeground=COLORES["acento"]
        )
        btn_registro.pack(fill="x", pady=(4, 0))
        btn_registro.bind("<Enter>", lambda e: btn_registro.config(bg=COLORES["acento_light"]))
        btn_registro.bind("<Leave>", lambda e: btn_registro.config(bg=COLORES["fondo_panel"]))

        self._entry_usuario.focus()

    def _toggle_contrasena(self):
        if self._var_mostrar_contrasena.get():
            self._entry_contrasena.config(show="*")
            self._btn_ojo.config(text="👁")
            self._var_mostrar_contrasena.set(False)
        else:
            self._entry_contrasena.config(show="")
            self._btn_ojo.config(text="🙈")
            self._var_mostrar_contrasena.set(True)

    def _ingresar(self):
        nombre_usuario = self._entry_usuario.get().strip()
        contrasena     = self._entry_contrasena.get()

        if not nombre_usuario or not contrasena:
            messagebox.showwarning(
                "Campos requeridos",
                "Ingrese usuario y contraseña.",
                parent=self
            )
            return

        try:
            usuario = UsuarioDAO().autenticar(nombre_usuario, contrasena)
        except Exception as error_conexion:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar a la base de datos.\n{error_conexion}",
                parent=self
            )
            return

        if not usuario:
            messagebox.showerror(
                "Acceso denegado",
                "Usuario o contraseña incorrectos.",
                parent=self
            )
            self._entry_contrasena.delete(0, tk.END)
            return

        try:
            self._abrir_menu(usuario)
        except Exception as error_apertura:
            messagebox.showerror(
                "Error al abrir el sistema",
                f"Ocurrió un error inesperado:\n{type(error_apertura).__name__}: {error_apertura}",
                parent=self
            )

    def _abrir_menu(self, usuario):
        if usuario.es_funcionario():
            MenuFuncionario(self._master, self, usuario)
        else:
            MenuCliente(self._master, self, usuario)
        self.withdraw()

    def _abrir_registro(self):
        VentanaRegistro(self)

    def _salir(self):
        self._master.destroy()