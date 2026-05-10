import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config.rutas import IMAGENES_DIR, ruta_relativa
from interfaz.estilos import (COLORES, FUENTES, boton_exito,
                               boton_primario, boton_secundario,
                               centrar_ventana)
from negocio.entidades_negocio import VehiculoNegocio

## Módulo de mantenimiento de imágenes por modelo
class MantenimientoImagenes(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["fondo"])
        self.pack(fill="both", expand=True)
        self._negocio = VehiculoNegocio()
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        tk.Label(self, text="Imágenes por Modelo de Vehículo", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["titulo"]).pack(anchor="w", pady=(0, 10))
        tk.Frame(self, bg=COLORES["acento"], height=2).pack(fill="x", pady=(0, 12))

        bar = tk.Frame(self, bg=COLORES["fondo"])
        bar.pack(fill="x", pady=(0, 10))

        boton_exito(bar,    "🖼 Asignar imagen", self._asignar, ancho=18).pack(side="left", padx=(0, 6))
        boton_primario(bar, "✏ Editar ruta",     self._editar,  ancho=16).pack(side="left", padx=6)

        tk.Label(bar, text="Buscar:", bg=COLORES["fondo"],
                 fg=COLORES["texto"], font=FUENTES["normal"]).pack(side="right", padx=(10, 4))
        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *a: self._filtrar())
        tk.Entry(bar, textvariable=self._var_busqueda, font=FUENTES["normal"],
                 bg=COLORES["blanco"], relief="solid", bd=1, width=22).pack(side="right", ipady=4)

        cols  = ("Marca", "Modelo", "Ruta de imagen")
        self._tabla = ttk.Treeview(self, columns=cols, show="headings", height=18)
        anchos = [140, 160, 460]
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
        self._todos = self._negocio.obtener_todas_imagenes()
        self._poblar(self._todos)

    def _poblar(self, lista):
        self._tabla.delete(*self._tabla.get_children())
        for i, m in enumerate(lista):
            tag = "par" if i % 2 == 0 else "impar"
            self._tabla.insert("", "end", values=(
                m.marca, m.modelo, m.ruta_imagen or "(sin imagen)"
            ), tags=(tag,))

    def _filtrar(self):
        texto = self._var_busqueda.get().strip().lower()
        if not texto:
            self._poblar(self._todos)
        else:
            filtrados = [m for m in self._todos
                         if texto in m.marca.lower()
                         or texto in m.modelo.lower()]
            self._poblar(filtrados)

    def _seleccionado(self):
        sel = self._tabla.selection()
        if not sel:
            messagebox.showinfo("Selección", "Seleccione un modelo de la tabla.", parent=self)
            return None, None
        vals = self._tabla.item(sel[0])["values"]
        return str(vals[0]), str(vals[1])

    def _asignar(self):
        dialogo = DialogoImagen(self, "Asignar imagen")
        self.wait_window(dialogo)
        self._cargar_tabla()

    def _editar(self):
        marca, modelo = self._seleccionado()
        if not marca:
            return
        dialogo = DialogoImagen(self, "Editar imagen", marca=marca, modelo=modelo)
        self.wait_window(dialogo)
        self._cargar_tabla()


## Diálogo para asignar/editar imagen de modelo
class DialogoImagen(tk.Toplevel):

    def __init__(self, parent, titulo, marca=None, modelo=None):
        super().__init__(parent)
        self.title(f"AutoTrust - {titulo}")
        self.configure(bg=COLORES["fondo"])
        self.resizable(False, False)
        self._marca   = marca
        self._modelo  = modelo
        self._negocio = VehiculoNegocio()
        self._campos  = {}
        self._construir()
        centrar_ventana(self, 520, 340)
        self.grab_set()
        if marca and modelo:
            self._cargar_datos()

    def _construir(self):
        hdr = tk.Frame(self, bg=COLORES["primario"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title().replace("AutoTrust - ", ""),
                 bg=COLORES["primario"], fg=COLORES["blanco"],
                 font=FUENTES["subtitulo"]).pack()

        contenido = tk.Frame(self, bg=COLORES["fondo"], padx=24, pady=16)
        contenido.pack(fill="both", expand=True)

        def fila(etiqueta, clave, estado="normal"):
            fila_contenedor = tk.Frame(contenido, bg=COLORES["fondo"])
            fila_contenedor.pack(fill="x", pady=6)
            tk.Label(fila_contenedor, text=etiqueta, bg=COLORES["fondo"], fg=COLORES["texto"],
                     font=FUENTES["etiqueta"], width=14, anchor="w").pack(side="left")
            campo_entrada = tk.Entry(fila_contenedor, font=FUENTES["normal"], bg=COLORES["blanco"],
                                     relief="solid", bd=1, state=estado)
            campo_entrada.pack(side="left", fill="x", expand=True, ipady=5)
            self._campos[clave] = campo_entrada

        fila("Marca *",  "marca",  estado="disabled" if self._marca  else "normal")
        fila("Modelo *", "modelo", estado="disabled" if self._modelo else "normal")

        ## Fila ruta con botón explorar
        fila_ruta = tk.Frame(contenido, bg=COLORES["fondo"])
        fila_ruta.pack(fill="x", pady=6)
        tk.Label(fila_ruta, text="Ruta imagen", bg=COLORES["fondo"], fg=COLORES["texto"],
                 font=FUENTES["etiqueta"], width=14, anchor="w").pack(side="left")
        self._campos["ruta"] = tk.Entry(fila_ruta, font=FUENTES["normal"],
                                        bg=COLORES["blanco"], relief="solid", bd=1)
        self._campos["ruta"].pack(side="left", fill="x", expand=True, ipady=5)
        boton_secundario(fila_ruta, "📂", self._explorar, ancho=3).pack(side="left", padx=(6, 0))

        ## Etiqueta informativa de carpeta
        tk.Label(contenido,
                 text=f"📁  Carpeta del proyecto: assets/imagenes/",
                 bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                 font=FUENTES["mini"]).pack(anchor="w", pady=(0, 4))

        btn = tk.Frame(contenido, bg=COLORES["fondo"])
        btn.pack(fill="x", pady=10)
        boton_exito(btn,     "💾 Guardar", self._guardar, ancho=16).pack(side="left", padx=4)
        boton_secundario(btn,"Cancelar",   self.destroy,  ancho=16).pack(side="left", padx=4)

    def _explorar(self):
      
        ## Crear la carpeta si no existe aún
        os.makedirs(IMAGENES_DIR, exist_ok=True)
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar imagen",
            initialdir=IMAGENES_DIR,
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if ruta:
            self._campos["ruta"].delete(0, tk.END)
            self._campos["ruta"].insert(0, ruta_relativa(ruta))

    def _get(self, clave):
        return self._campos[clave].get().strip()

    def _cargar_datos(self):
        mi = self._negocio.obtener_imagen(self._marca, self._modelo)
        self._campos["marca"].config(state="normal")
        self._campos["marca"].insert(0, self._marca)
        self._campos["marca"].config(state="disabled")
        self._campos["modelo"].config(state="normal")
        self._campos["modelo"].insert(0, self._modelo)
        self._campos["modelo"].config(state="disabled")
        if mi and mi.ruta_imagen:
            self._campos["ruta"].insert(0, mi.ruta_imagen)

    def _guardar(self):
        try:
            marca  = self._marca  or self._get("marca")
            modelo = self._modelo or self._get("modelo")
            ruta   = self._get("ruta")
            if not marca:
                raise ValueError("La marca es obligatoria.")
            if not modelo:
                raise ValueError("El modelo es obligatorio.")
            self._negocio.guardar_imagen(marca, modelo, ruta)
            messagebox.showinfo("Guardado", "Imagen guardada correctamente.", parent=self)
            self.destroy()
        except ValueError as e:
            messagebox.showwarning("Validación", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)