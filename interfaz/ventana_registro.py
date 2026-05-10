import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from interfaz.estilos import (COLORES, FUENTES, boton_primario,
                               boton_secundario, centrar_ventana)
from entidades.cliente import Cliente
from negocio.entidades_negocio import ClienteNegocio

## Ventana Registro de Cliente
class VentanaRegistro(tk.Toplevel):

    NACIONALIDADES = ["Costarricense", "Estadounidense", "Canadiense",
                      "Colombiano", "Nicaragüense", "Panameño", "Otro"]

    ## Regex: mínimo 8 chars, 1 mayúscula, 1 minúscula, 1 dígito, 1 especial
    _RE_CONTRASENA = re.compile(
        r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$'
    )
    _RE_CORREO = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

    def __init__(self, master):
        super().__init__(master)
        self.title("AutoTrust - Registro de Cliente")
        self.configure(bg=COLORES["fondo"])
        self.resizable(False, False)
        self._construir()
        centrar_ventana(self, 500, 680)
        self.grab_set()

    def _construir(self):
        encabezado = tk.Frame(self, bg=COLORES["primario"], pady=14)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text="AutoTrust S.A.", bg=COLORES["primario"],
                 fg="#5DADE2", font=FUENTES["logo"]).pack()
        tk.Label(encabezado, text="Registro de nuevo cliente",
                 bg=COLORES["primario"], fg=COLORES["blanco"],
                 font=FUENTES["subtitulo"]).pack(pady=(2, 0))

        canvas = tk.Canvas(self, bg=COLORES["fondo"], highlightthickness=0)
        scroll = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        frame = tk.Frame(canvas, bg=COLORES["fondo"], padx=30, pady=20)
        ventana_id = canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(ventana_id, width=e.width))

        self._campos = {}
        self._crear_formulario(frame)

    def _campo(self, parent, etiqueta, clave, tipo="entry", opciones=None):
        fila = tk.Frame(parent, bg=COLORES["fondo"])
        fila.pack(fill="x", pady=4)
        tk.Label(fila, text=etiqueta, bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["etiqueta"],
                 width=22, anchor="w").pack(side="left")

        if tipo == "entry":
            widget = tk.Entry(fila, font=FUENTES["normal"], bg=COLORES["blanco"],
                              relief="solid", bd=1,
                              highlightthickness=1,
                              highlightcolor=COLORES["acento"])
            widget.pack(side="left", fill="x", expand=True, ipady=5)

        elif tipo == "combo":
            widget = tk.StringVar(value=opciones[0])
            combo = tk.OptionMenu(fila, widget, *opciones)
            combo.config(font=FUENTES["normal"], bg=COLORES["blanco"],
                         relief="solid", bd=1, width=18)
            combo.pack(side="left", fill="x", expand=True)

        elif tipo == "password":
            widget = tk.Entry(fila, font=FUENTES["normal"], bg=COLORES["blanco"],
                              relief="solid", bd=1, show="*",
                              highlightthickness=1,
                              highlightcolor=COLORES["acento"])
            widget.pack(side="left", fill="x", expand=True, ipady=5)

        self._campos[clave] = widget

    def _crear_formulario(self, frame):
        def titulo(texto):
            tk.Label(frame, text=texto, bg=COLORES["fondo"],
                     fg=COLORES["secundario"],
                     font=FUENTES["negrita"]).pack(anchor="w", pady=(12, 2))
            tk.Frame(frame, bg=COLORES["acento"], height=1).pack(fill="x", pady=(0, 6))

        titulo("Datos personales")
        self._campo(frame, "Identificación *",               "identificacion")
        self._campo(frame, "Nacionalidad",                    "nacionalidad",
                    "combo", self.NACIONALIDADES)
        self._campo(frame, "Nombre *",                        "nombre")
        self._campo(frame, "Primer apellido *",               "primer_apellido")
        self._campo(frame, "Segundo apellido",                "segundo_apellido")
        self._campo(frame, "Fecha nacimiento (AAAA-MM-DD) *", "fecha_nacimiento")

        titulo("Contacto")
        self._campo(frame, "Teléfono *",           "telefono")
        self._campo(frame, "Correo electrónico *", "correo")

        titulo("Pago")
        self._campo(frame, "Tipo de pago",     "tipo_pago",
                    "combo", ["efectivo", "tarjeta"])
        self._campo(frame, "Datos de tarjeta", "datos_tarjeta")

        titulo("Cuenta de acceso")
        self._campo(frame, "Usuario *",    "usuario")
        self._campo(frame, "Contraseña *", "contrasena", "password")

        tk.Label(frame,
                 text="  Mínimo 8 caracteres, 1 mayúscula, 1 minúscula, "
                      "1 número y 1 carácter especial.",
                 bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                 font=FUENTES["mini"], wraplength=400,
                 justify="left").pack(anchor="w", padx=2)

        contenedor_botones = tk.Frame(frame, bg=COLORES["fondo"])
        contenedor_botones.pack(fill="x", pady=16)
        boton_primario(contenedor_botones,   "Registrarse", self._registrar, ancho=20).pack(
            side="left", padx=4)
        boton_secundario(contenedor_botones, "Cancelar",    self.destroy,    ancho=20).pack(
            side="left", padx=4)

    def _get(self, clave):
        widget = self._campos[clave]
        if isinstance(widget, tk.StringVar):
            return widget.get()
        return widget.get().strip()

    def _validar(self):
        identificacion   = self._get("identificacion")
        nombre           = self._get("nombre")
        primer_apellido  = self._get("primer_apellido")
        segundo_apellido = self._get("segundo_apellido")
        fecha_nacimiento = self._get("fecha_nacimiento")
        telefono         = self._get("telefono")
        correo           = self._get("correo")
        tipo_pago        = self._get("tipo_pago")
        datos_tarjeta    = self._get("datos_tarjeta")
        usuario          = self._get("usuario")
        contrasena       = self._get("contrasena")

        if not identificacion:
            raise ValueError("La identificación es obligatoria.")

        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if re.search(r'\d', nombre):
            raise ValueError("El nombre no puede contener números.")
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', nombre):
            raise ValueError("El nombre debe contener al menos una letra.")

        if not primer_apellido:
            raise ValueError("El primer apellido es obligatorio.")
        if re.search(r'\d', primer_apellido):
            raise ValueError("El primer apellido no puede contener números.")
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', primer_apellido):
            raise ValueError("El primer apellido debe contener al menos una letra.")

        if segundo_apellido:
            if re.search(r'\d', segundo_apellido):
                raise ValueError("El segundo apellido no puede contener números.")
            if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', segundo_apellido):
                raise ValueError("El segundo apellido debe contener al menos una letra.")

        if not fecha_nacimiento:
            raise ValueError("La fecha de nacimiento es obligatoria.")
        try:
            datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        except ValueError:
            raise ValueError("La fecha de nacimiento debe tener el formato AAAA-MM-DD.")

        if not telefono:
            raise ValueError("El teléfono es obligatorio.")
        solo_digitos = re.sub(r'[\s\-\+\(\)]', '', telefono)
        if not solo_digitos.isdigit():
            raise ValueError("El teléfono solo puede contener números.")
        if len(solo_digitos) < 7:
            raise ValueError("El teléfono debe tener al menos 7 dígitos.")

        if not correo:
            raise ValueError("El correo electrónico es obligatorio.")
        if not self._RE_CORREO.match(correo):
            raise ValueError("El correo electrónico no tiene un formato válido.")

        if tipo_pago == "tarjeta" and not datos_tarjeta:
            raise ValueError(
                "Debe ingresar los datos de tarjeta al seleccionar ese método de pago.")

        if not usuario:
            raise ValueError("El nombre de usuario es obligatorio.")

        if not contrasena:
            raise ValueError("La contraseña es obligatoria.")
        if not self._RE_CONTRASENA.match(contrasena):
            raise ValueError(
                "La contraseña debe tener mínimo 8 caracteres, "
                "al menos 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial.")

    def _registrar(self):
        try:
            self._validar()

            cliente = Cliente(
                identificacion=self._get("identificacion"),
                nacionalidad=self._get("nacionalidad"),
                nombre=self._get("nombre"),
                primer_apellido=self._get("primer_apellido"),
                segundo_apellido=self._get("segundo_apellido"),
                fecha_nacimiento=self._get("fecha_nacimiento") or None,
                telefono=self._get("telefono"),
                correo=self._get("correo"),
                tipo_pago=self._get("tipo_pago"),
                datos_tarjeta=self._get("datos_tarjeta"),
            )

            if not cliente.es_mayor_de_edad(18):
                raise ValueError(
                    f"Debe ser mayor de 18 años para registrarse. "
                    f"Su edad actual es {cliente.calcular_edad()} años.")

            ClienteNegocio().registrar(
                cliente,
                self._get("usuario"),
                self._get("contrasena"),
            )

            messagebox.showinfo(
                "Éxito",
                "Registro completado. ¡Ya puede iniciar sesión!",
                parent=self)
            self.destroy()

        except ValueError as error:
            messagebox.showwarning("Datos inválidos", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)