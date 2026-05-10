import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from interfaz.estilos import (
    COLORES, FUENTES,
    boton_primario, boton_peligro, boton_secundario, boton_exito,
    crear_header_pagina, crear_barra_busqueda, crear_tabla, centrar_ventana, entry_moderno
)
from negocio.entidades_negocio import ClienteNegocio
from entidades.cliente import Cliente

## MantenimientoClientes
class MantenimientoClientes(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True, padx=24, pady=20)
        self._negocio = ClienteNegocio()
        self._todos   = []
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        crear_header_pagina(self, "Clientes", "Gestión de clientes registrados")

        barra = tk.Frame(self, bg=COLORES["fondo"])
        barra.pack(fill="x", pady=(14, 10))

        boton_exito(barra,    "➕  Agregar",        self._agregar,        ancho=14).pack(side="left", padx=(0, 6))
        boton_primario(barra, "✏  Editar",          self._editar,         ancho=14).pack(side="left", padx=(0, 6))
        boton_peligro(barra,  "🔒  Cambiar estado", self._cambiar_estado, ancho=16).pack(side="left")

        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *a: self._filtrar())
        crear_barra_busqueda(barra, self._var_busqueda,
                             "Buscar por ID, nombre o correo...").pack(side="right")

        columnas = ("ID", "Nombre completo", "Teléfono", "Correo", "Pago", "Estado")
        anchos   = [120, 220, 110, 210, 90, 80]
        contenedor, self._tabla = crear_tabla(self, columnas, anchos, height=20)
        contenedor.pack(fill="both", expand=True)
        self._tabla.bind("<Double-1>", lambda e: self._editar())

    def _cargar_tabla(self):
        self._todos = self._negocio.obtener_todos()
        self._poblar(self._todos)

    def _poblar(self, lista):
        self._tabla.delete(*self._tabla.get_children())
        for indice, cliente in enumerate(lista):
            estado   = "Activo" if cliente.activo else "Inactivo"
            etiqueta = "par" if indice % 2 == 0 else "impar"
            self._tabla.insert("", "end", tags=(etiqueta,), values=(
                cliente.identificacion, cliente.nombre_completo(),
                cliente.telefono, cliente.correo, cliente.tipo_pago, estado
            ))

    def _filtrar(self):
        texto = self._var_busqueda.get().strip().lower()
        if not texto:
            self._poblar(self._todos)
            return
        self._poblar([cliente for cliente in self._todos
                      if texto in cliente.identificacion.lower()
                      or texto in cliente.nombre_completo().lower()
                      or texto in cliente.correo.lower()])

    def _obtener_id_seleccionado(self):
        seleccion = self._tabla.selection()
        if not seleccion:
            messagebox.showinfo("Selección", "Seleccione un cliente.", parent=self)
            return None
        return self._tabla.item(seleccion[0])["values"][0]

    def _cliente_seleccionado(self):
        identificacion = self._obtener_id_seleccionado()
        if not identificacion:
            return None
        return self._negocio.buscar(str(identificacion))

    def _agregar(self):
        dialogo = DialogoCliente(self, "Agregar cliente", modo_funcionario=True)
        self.wait_window(dialogo)
        self._cargar_tabla()

    def _editar(self):
        identificacion = self._obtener_id_seleccionado()
        if not identificacion:
            return
        dialogo = DialogoCliente(self, "Editar cliente", identificacion=str(identificacion))
        self.wait_window(dialogo)
        self._cargar_tabla()

    def _cambiar_estado(self):
        cliente = self._cliente_seleccionado()
        if not cliente:
            return
        estado_nuevo = "Inactivo" if cliente.activo else "Activo"
        if not messagebox.askyesno("Confirmar",
                f"¿Cambiar estado de {cliente.nombre_completo()} a '{estado_nuevo}'?",
                parent=self):
            return
        try:
            if cliente.activo:
                self._negocio.desactivar(cliente.identificacion)
            else:
                self._negocio.reactivar(cliente.identificacion)
            messagebox.showinfo("Listo", f"Estado cambiado a '{estado_nuevo}'.", parent=self)
            self._cargar_tabla()
        except ValueError as error:
            messagebox.showwarning("No permitido", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Error", str(error), parent=self)


## DialogoCliente
class DialogoCliente(tk.Toplevel):

    NACIONALIDADES = ["Costarricense", "Estadounidense", "Canadiense",
                      "Colombiano", "Nicaragüense", "Panameño", "Otro"]

    _RE_CORREO = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

    def __init__(self, parent, titulo, identificacion=None, modo_funcionario=False):
        super().__init__(parent)
        self.title(f"AutoTrust — {titulo}")
        self.configure(bg=COLORES["fondo"])
        self.resizable(False, False)
        self._identificacion   = identificacion
        self._modo_funcionario = modo_funcionario
        self._negocio          = ClienteNegocio()
        self._campos           = {}
        self._id_verificado    = False
        self._construir()
        centrar_ventana(self, 540, 600)
        self.grab_set()
        if identificacion:
            self._cargar_datos()

    def _construir(self):
        cabecera = tk.Frame(self, bg=COLORES["acento"], pady=14) 
        cabecera.pack(fill="x")
        tk.Label(cabecera, text=self.title().replace("AutoTrust — ", ""),
                 bg=COLORES["acento"], fg=COLORES["blanco"],
                 font=FUENTES["subtitulo"]).pack()

        pie = tk.Frame(self, bg=COLORES["fondo"], pady=10)
        pie.pack(side="bottom", fill="x", padx=28)
        boton_exito(pie,      "💾  Guardar", self._guardar, ancho=16).pack(side="left", padx=(0, 8))
        boton_secundario(pie, "Cancelar",    self.destroy,  ancho=14).pack(side="left")

        canvas = tk.Canvas(self, bg=COLORES["fondo"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        cuerpo = tk.Frame(canvas, bg=COLORES["fondo"], padx=28, pady=18)
        ventana_id = canvas.create_window((0, 0), window=cuerpo, anchor="nw")
        cuerpo.bind("<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(ventana_id, width=e.width))

        def seccion(texto_seccion):
            tk.Label(cuerpo, text=texto_seccion, bg=COLORES["fondo"],
                     fg=COLORES["acento"], font=FUENTES["negrita"]).pack(
                         anchor="w", pady=(12, 4))
            tk.Frame(cuerpo, bg=COLORES["borde"], height=1).pack(fill="x", pady=(0, 6))

        def fila(etiqueta, clave, tipo="entry", opciones=None, show=None):
            contenedor_fila = tk.Frame(cuerpo, bg=COLORES["fondo"])
            contenedor_fila.pack(fill="x", pady=3)
            tk.Label(contenedor_fila, text=etiqueta, bg=COLORES["fondo"],
                     fg=COLORES["texto_suave"], font=FUENTES["pequena"],
                     width=26, anchor="w").pack(side="left")
            if tipo == "entry":
                widget = entry_moderno(contenedor_fila, show=show)
                widget.pack(side="left", fill="x", expand=True, ipady=6)
            elif tipo == "combo":
                widget = tk.StringVar(value=opciones[0])
                combo  = tk.OptionMenu(contenedor_fila, widget, *opciones)
                combo.config(bg=COLORES["input_bg"], relief="flat",
                             font=FUENTES["campo"], bd=1,
                             highlightthickness=1,
                             highlightbackground=COLORES["borde"])
                combo.pack(side="left", fill="x", expand=True)
            self._campos[clave] = widget

        seccion("Datos personales")

        if not self._identificacion:
            self._construir_fila_identificacion(cuerpo)
        else:
            contenedor_id = tk.Frame(cuerpo, bg=COLORES["fondo"])
            contenedor_id.pack(fill="x", pady=3)
            tk.Label(contenedor_id, text="Identificación", bg=COLORES["fondo"],
                     fg=COLORES["texto_suave"], font=FUENTES["pequena"],
                     width=26, anchor="w").pack(side="left")
            entry_id = entry_moderno(contenedor_id)
            entry_id.pack(side="left", fill="x", expand=True, ipady=6)
            entry_id.config(state="disabled")
            self._campos["identificacion"] = entry_id

        fila("Nacionalidad",                    "nacionalidad",    "combo", self.NACIONALIDADES)
        fila("Nombre *",                        "nombre")
        fila("Primer apellido *",               "primer_apellido")
        ## Segundo apellido es opcional
        fila("Segundo apellido",                "segundo_apellido")
        fila("Fecha nacimiento (AAAA-MM-DD) *", "fecha_nacimiento")

        seccion("Contacto y pago")
        fila("Teléfono *",       "telefono")
        fila("Correo *",         "correo")
        fila("Tipo de pago",     "tipo_pago",    "combo", ["efectivo", "tarjeta"])
        fila("Datos de tarjeta", "datos_tarjeta")

        if not self._identificacion:
            seccion("Cuenta de acceso")
            fila("Usuario *", "usuario")

            contenedor_contrasena = tk.Frame(cuerpo, bg=COLORES["fondo"])
            contenedor_contrasena.pack(fill="x", pady=3)
            tk.Label(contenedor_contrasena, text="Contraseña *", bg=COLORES["fondo"],
                     fg=COLORES["texto_suave"], font=FUENTES["pequena"],
                     width=26, anchor="w").pack(side="left")
            widget_contrasena = entry_moderno(contenedor_contrasena, show="*")
            widget_contrasena.pack(side="left", fill="x", expand=True, ipady=6)
            self._campos["contrasena"] = widget_contrasena

            tk.Label(cuerpo,
                     text="  Contraseña: mínimo 8 caracteres, 1 mayúscula, "
                          "1 minúscula, 1 número y 1 carácter especial.",
                     bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                     font=FUENTES["mini"], wraplength=460,
                     justify="left").pack(anchor="w", padx=2)

    def _construir_fila_identificacion(self, cuerpo):
        contenedor_id = tk.Frame(cuerpo, bg=COLORES["fondo"])
        contenedor_id.pack(fill="x", pady=3)
        tk.Label(contenedor_id, text="Identificación *", bg=COLORES["fondo"],
                 fg=COLORES["texto_suave"], font=FUENTES["pequena"],
                 width=26, anchor="w").pack(side="left")
        entry_id = entry_moderno(contenedor_id)
        entry_id.pack(side="left", fill="x", expand=True, ipady=6)
        boton_primario(contenedor_id, "Verificar",
                       self._verificar_identificacion, ancho=10).pack(side="left", padx=(8, 0))
        self._campos["identificacion"] = entry_id

        entry_id.bind("<KeyRelease>", lambda e: self._resetear_verificacion())

        self._etiqueta_estado_id = tk.Label(cuerpo, text="",
                                            bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                                            font=FUENTES["pequena"])
        self._etiqueta_estado_id.pack(anchor="w", padx=4, pady=(0, 2))

    def _verificar_identificacion(self):
        identificacion = self._obtener_valor("identificacion").strip()

        if not identificacion:
            messagebox.showwarning("Requerido", "Ingrese la identificación.", parent=self)
            return
        if len(identificacion) < 5:
            self._etiqueta_estado_id.config(
                text="✖ La identificación debe tener al menos 5 caracteres.",
                fg=COLORES["peligro"])
            self._id_verificado = False
            return
        if not any(caracter.isdigit() for caracter in identificacion):
            self._etiqueta_estado_id.config(
                text="✖ La identificación debe contener al menos un número.",
                fg=COLORES["peligro"])
            self._id_verificado = False
            return

        if self._negocio.existe_identificacion(identificacion):
            self._etiqueta_estado_id.config(
                text="✖ Esta identificación ya está registrada en el sistema.",
                fg=COLORES["peligro"])
            self._id_verificado = False
        else:
            self._etiqueta_estado_id.config(
                text="✔ Identificación disponible.",
                fg=COLORES["exito"])
            self._id_verificado = True

    def _resetear_verificacion(self):
        self._id_verificado = False
        self._etiqueta_estado_id.config(text="", fg=COLORES["texto_suave"])

    def _obtener_valor(self, clave):
        widget = self._campos.get(clave)
        if widget is None:
            return ""
        return widget.get() if isinstance(widget, tk.StringVar) else widget.get().strip()

    ## ── Validaciones individuales ─────────────────────────────────

    def _validar_nombre(self, valor, etiqueta):
        if not valor:
            messagebox.showwarning("Validación", f"{etiqueta} es obligatorio/a.", parent=self)
            return False
        if re.search(r'\d', valor):
            messagebox.showwarning("Validación", f"{etiqueta} no puede contener números.", parent=self)
            return False
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', valor):
            messagebox.showwarning("Validación",
                f"{etiqueta} debe contener al menos una letra.", parent=self)
            return False
        return True

    def _validar_segundo_apellido(self, valor):
        ## Solo se valida el formato si el campo tiene contenido; es opcional
        if not valor:
            return True
        if re.search(r'\d', valor):
            messagebox.showwarning("Validación",
                "El segundo apellido no puede contener números.", parent=self)
            return False
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', valor):
            messagebox.showwarning("Validación",
                "El segundo apellido debe contener al menos una letra.", parent=self)
            return False
        return True

    def _validar_fecha_nacimiento(self, fecha):
        if not fecha:
            messagebox.showwarning("Validación",
                "La fecha de nacimiento es obligatoria.", parent=self)
            return False
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
            return True
        except ValueError:
            messagebox.showwarning("Validación",
                "La fecha de nacimiento debe tener el formato AAAA-MM-DD.", parent=self)
            return False

    def _validar_telefono(self, telefono):
        if not telefono:
            messagebox.showwarning("Validación", "El teléfono es obligatorio.", parent=self)
            return False
        solo_digitos = re.sub(r'[\s\-\+\(\)]', '', telefono)
        if not solo_digitos.isdigit():
            messagebox.showwarning("Validación",
                "El teléfono solo puede contener números.", parent=self)
            return False
        if len(solo_digitos) < 7:
            messagebox.showwarning("Validación",
                "El teléfono debe tener al menos 7 dígitos.", parent=self)
            return False
        return True

    def _validar_correo(self, correo):
        if not correo:
            messagebox.showwarning("Validación",
                "El correo electrónico es obligatorio.", parent=self)
            return False
        if not self._RE_CORREO.match(correo):
            messagebox.showwarning("Validación",
                "El correo electrónico no tiene un formato válido.", parent=self)
            return False
        return True

    def _validar_campos_comunes(self):
        if not self._validar_nombre(self._obtener_valor("nombre"), "El nombre"):
            return False
        if not self._validar_nombre(self._obtener_valor("primer_apellido"), "El primer apellido"):
            return False
        ## Segundo apellido es opcional, solo valida formato si tiene contenido
        if not self._validar_segundo_apellido(self._obtener_valor("segundo_apellido")):
            return False
        if not self._validar_fecha_nacimiento(self._obtener_valor("fecha_nacimiento")):
            return False
        if not self._validar_telefono(self._obtener_valor("telefono")):
            return False
        if not self._validar_correo(self._obtener_valor("correo")):
            return False
        return True

    ## ─────────────────────────────────────────────────────────────

    def _cargar_datos(self):
        cliente = self._negocio.buscar(self._identificacion)
        if not cliente:
            return
        mapeo = {
            "nombre":           cliente.nombre,
            "primer_apellido":  cliente.primer_apellido,
            "segundo_apellido": cliente.segundo_apellido,
            "fecha_nacimiento": str(cliente.fecha_nacimiento) if cliente.fecha_nacimiento else "",
            "telefono":         cliente.telefono,
            "correo":           cliente.correo,
            "datos_tarjeta":    cliente.datos_tarjeta,
        }
        for clave, valor in mapeo.items():
            widget = self._campos.get(clave)
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, valor)
        if isinstance(self._campos.get("nacionalidad"), tk.StringVar):
            self._campos["nacionalidad"].set(cliente.nacionalidad)
        if isinstance(self._campos.get("tipo_pago"), tk.StringVar):
            self._campos["tipo_pago"].set(cliente.tipo_pago)

    def _guardar(self):
        try:
            es_edicion = self._identificacion is not None

            if not es_edicion:
                if not self._id_verificado:
                    messagebox.showwarning("Requerido",
                        "Primero verifique la identificación antes de guardar.",
                        parent=self)
                    return
                if not self._validar_campos_comunes():
                    return
                if not self._obtener_valor("usuario"):
                    messagebox.showwarning("Validación",
                        "El nombre de usuario es obligatorio.", parent=self)
                    return
                if not self._obtener_valor("contrasena"):
                    messagebox.showwarning("Validación",
                        "La contraseña es obligatoria.", parent=self)
                    return

                cliente_nuevo = Cliente(
                    identificacion=self._obtener_valor("identificacion"),
                    nacionalidad=self._obtener_valor("nacionalidad"),
                    nombre=self._obtener_valor("nombre"),
                    primer_apellido=self._obtener_valor("primer_apellido"),
                    segundo_apellido=self._obtener_valor("segundo_apellido"),
                    fecha_nacimiento=self._obtener_valor("fecha_nacimiento"),
                    telefono=self._obtener_valor("telefono"),
                    correo=self._obtener_valor("correo"),
                    tipo_pago=self._obtener_valor("tipo_pago"),
                    datos_tarjeta=self._obtener_valor("datos_tarjeta"),
                )
                
                ## Validar que sea mayor de edad
                if not cliente_nuevo.es_mayor_de_edad(18):
                    raise ValueError(
                        f"El cliente debe ser mayor de 18 años para poder alquilar vehículos. "
                        f"Edad actual: {cliente_nuevo.calcular_edad()} años.")
                
                self._negocio.registrar(
                    cliente_nuevo,
                    self._obtener_valor("usuario"),
                    self._obtener_valor("contrasena"),
                )

            else:
                if not self._validar_campos_comunes():
                    return

                datos_actualizados = {
                    clave: self._obtener_valor(clave) for clave in [
                        "nombre", "primer_apellido", "segundo_apellido",
                        "fecha_nacimiento", "telefono", "correo",
                        "tipo_pago", "datos_tarjeta", "nacionalidad"
                    ]
                }
                cliente_actualizado = Cliente(
                    identificacion=self._identificacion,
                    nombre=datos_actualizados["nombre"],
                    primer_apellido=datos_actualizados["primer_apellido"],
                    segundo_apellido=datos_actualizados["segundo_apellido"],
                    fecha_nacimiento=datos_actualizados["fecha_nacimiento"],
                    telefono=datos_actualizados["telefono"],
                    correo=datos_actualizados["correo"],
                    tipo_pago=datos_actualizados["tipo_pago"],
                    datos_tarjeta=datos_actualizados["datos_tarjeta"],
                    nacionalidad=datos_actualizados["nacionalidad"],
                )
                
                ## Validar que siga siendo mayor de edad
                if not cliente_actualizado.es_mayor_de_edad(18):
                    raise ValueError(
                        f"El cliente debe ser mayor de 18 años para poder alquilar vehículos. "
                        f"Edad actual: {cliente_actualizado.calcular_edad()} años.")
                
                self._negocio.actualizar(self._identificacion, datos_actualizados)

            messagebox.showinfo("Guardado", "Datos guardados correctamente.", parent=self)
            self.destroy()

        except ValueError as error_validacion:
            messagebox.showwarning("Validación", str(error_validacion), parent=self)
        except Exception as error_general:
            messagebox.showerror("Error", str(error_general), parent=self)