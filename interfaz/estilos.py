import tkinter as tk
from tkinter import ttk

# Paleta de colores
COLORES = {
    # Fondos
    "fondo":         "#F4F7FA",
    "fondo_panel":   "#FFFFFF",
    "fondo_sidebar": "#0F2235",
    "fondo_topbar":  "#0F2235",
    "fondo_card":    "#FFFFFF",

    # Marca
    "primario":      "#0F2235",
    "secundario":    "#1A5276",
    "acento":        "#2E86C1",
    "acento_hover":  "#1A6EA8",
    "acento_light":  "#EBF5FB",

    # Texto
    "texto":         "#1A252F",
    "texto_suave":   "#7F8C8D",
    "texto_sidebar": "#BDC3C7",
    "texto_blanco":  "#FFFFFF",

    # Semánticos
    "exito":             "#1E8449",
    "exito_hover":       "#145A32",
    "exito_light":       "#EAFAF1",
    "peligro":           "#C0392B",
    "peligro_hover":     "#922B21",
    "peligro_light":     "#FDEDEC",
    "advertencia":       "#D4AC0D",
    "advertencia_light": "#FEF9E7",
    "info_light":        "#EBF5FB",

    # UI
    "borde":          "#E5E9ED",
    "borde_suave":    "#F0F3F5",
    "sombra":         "#00000015",
    "tabla_par":      "#F8FAFC",
    "tabla_impar":    "#FFFFFF",
    "tabla_hover":    "#EBF5FB",
    "header_tabla":   "#1A5276",
    "blanco":         "#FFFFFF",
    "input_bg":       "#FAFBFC",

    # Sidebar
    "sidebar_hover":     "#1A3A52",
    "sidebar_activo":    "#2E86C1",
    "sidebar_separador": "#1A3A52",
}

# Fuentes
FUENTES = {
    "logo":      ("Segoe UI", 20, "bold"),
    "titulo":    ("Segoe UI", 16, "bold"),
    "subtitulo": ("Segoe UI", 13, "bold"),
    "normal":    ("Segoe UI", 10),
    "negrita":   ("Segoe UI", 10, "bold"),
    "pequena":   ("Segoe UI", 9),
    "mini":      ("Segoe UI", 8),
    "etiqueta":  ("Segoe UI", 10),
    "campo":     ("Segoe UI", 10),
    "boton":     ("Segoe UI", 10, "bold"),
    "icono":     ("Segoe UI", 14),
}

# Tema TTK
def aplicar_tema(root):
    """
    Aplica el tema visual a los widgets TTK.
    Debe llamarse SOLO desde __init__ de una ventana Toplevel/Tk,
    nunca a nivel de módulo ni en imports.
    """
    try:
        estilo = ttk.Style(root)
        estilo.theme_use("clam")

        # Treeview
        estilo.configure("Treeview",
            background=COLORES["fondo_panel"],
            fieldbackground=COLORES["fondo_panel"],
            foreground=COLORES["texto"],
            font=FUENTES["normal"],
            rowheight=30,
            relief="flat",
            borderwidth=0,
        )
        estilo.configure("Treeview.Heading",
            background=COLORES["header_tabla"],
            foreground=COLORES["blanco"],
            font=FUENTES["negrita"],
            relief="flat",
            padding=(10, 8),
        )
        estilo.map("Treeview",
            background=[("selected", COLORES["acento"])],
            foreground=[("selected", COLORES["blanco"])],
        )
        estilo.map("Treeview.Heading",
            background=[("active", COLORES["secundario"])],
            relief=[("active", "flat")],
        )

        # Scrollbar
        estilo.configure("TScrollbar",
            background=COLORES["borde"],
            troughcolor=COLORES["fondo"],
            arrowcolor=COLORES["texto_suave"],
            width=8,
        )

        # Notebook (pestañas)
        estilo.configure("TNotebook",
            background=COLORES["fondo"],
            borderwidth=0,
        )
        estilo.configure("TNotebook.Tab",
            font=FUENTES["negrita"],
            padding=[14, 7],
            background=COLORES["borde"],
            foreground=COLORES["texto_suave"],
        )
        estilo.map("TNotebook.Tab",
            background=[("selected", COLORES["acento"])],
            foreground=[("selected", COLORES["blanco"])],
            expand=[("selected", [1, 1, 1, 0])],
        )

        # Combobox
        estilo.configure("TCombobox",
            fieldbackground=COLORES["input_bg"],
            foreground=COLORES["texto"],
            font=FUENTES["campo"],
            padding=5,
        )
    except Exception as e:
        print(f"[AVISO] No se pudo aplicar el tema visual: {e}")


# Botones modernos
def _crear_boton(parent, texto, comando, bg, fg, bg_hover, ancho=18, alto=1):
    btn = tk.Button(
        parent, text=texto, command=comando,
        bg=bg, fg=fg,
        font=FUENTES["boton"],
        width=ancho, height=alto,
        relief="flat", cursor="hand2",
        pady=7, padx=4,
        activebackground=bg_hover,
        activeforeground=fg,
        bd=0,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=bg_hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def boton_primario(parent, texto, comando, ancho=18):
    return _crear_boton(parent, texto, comando,
        COLORES["acento"], COLORES["blanco"], COLORES["acento_hover"], ancho)

def boton_exito(parent, texto, comando, ancho=18):
    return _crear_boton(parent, texto, comando,
        COLORES["exito"], COLORES["blanco"], COLORES["exito_hover"], ancho)

def boton_peligro(parent, texto, comando, ancho=18):
    return _crear_boton(parent, texto, comando,
        COLORES["peligro"], COLORES["blanco"], COLORES["peligro_hover"], ancho)

def boton_secundario(parent, texto, comando, ancho=18):
    return _crear_boton(parent, texto, comando,
        COLORES["borde"], COLORES["texto"], "#BDC3C7", ancho)

def boton_ghost(parent, texto, comando, ancho=18):
    btn = tk.Button(
        parent, text=texto, command=comando,
        bg=COLORES["fondo_sidebar"], fg=COLORES["texto_sidebar"],
        font=FUENTES["normal"],
        width=ancho, relief="flat", cursor="hand2",
        pady=8, padx=12, anchor="w",
        activebackground=COLORES["sidebar_hover"],
        activeforeground=COLORES["blanco"],
        bd=0,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=COLORES["sidebar_hover"], fg=COLORES["blanco"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLORES["fondo_sidebar"], fg=COLORES["texto_sidebar"]))
    return btn


# Entry estilizado
def entry_moderno(parent, font=None, width=None, show=None, **kwargs):
    opts = dict(
        bg=COLORES["input_bg"],
        fg=COLORES["texto"],
        font=font or FUENTES["campo"],
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=COLORES["borde"],
        highlightcolor=COLORES["acento"],
        insertbackground=COLORES["acento"],
    )
    if width: opts["width"] = width
    if show:  opts["show"]  = show
    opts.update(kwargs)
    return tk.Entry(parent, **opts)


# Card con borde suave
def crear_card(parent, padx=20, pady=16, **kwargs):
    sombra = tk.Frame(parent, bg=COLORES["borde"], **kwargs)
    card   = tk.Frame(sombra, bg=COLORES["fondo_card"], padx=padx, pady=pady)
    card.pack(padx=1, pady=1, fill="both", expand=True)
    return sombra, card


# Divisor
def divisor(parent, color=None, grosor=1, pady=8):
    tk.Frame(parent, bg=color or COLORES["borde"], height=grosor).pack(fill="x", pady=pady)


# Badge de estado
def badge(parent, texto, tipo="info"):
    colores_badge = {
        "exito":       (COLORES["exito_light"],       COLORES["exito"]),
        "peligro":     (COLORES["peligro_light"],     COLORES["peligro"]),
        "advertencia": (COLORES["advertencia_light"], COLORES["advertencia"]),
        "info":        (COLORES["info_light"],         COLORES["acento"]),
        "neutro":      (COLORES["borde_suave"],        COLORES["texto_suave"]),
    }
    bg, fg = colores_badge.get(tipo, colores_badge["info"])
    return tk.Label(parent, text=f"  {texto}  ",
                    bg=bg, fg=fg, font=FUENTES["pequena"],
                    relief="flat", padx=4, pady=2)


# Topbar (barra superior)
def crear_topbar(parent, titulo="", usuario="", subtitulo=""):
    bar = tk.Frame(parent, bg=COLORES["fondo_topbar"], height=58)
    bar.pack(fill="x")
    bar.pack_propagate(False)

    izq = tk.Frame(bar, bg=COLORES["fondo_topbar"])
    izq.pack(side="left", padx=20, fill="y")
    tk.Label(izq, text="AutoTrust", bg=COLORES["fondo_topbar"],
             fg="#5DADE2", font=FUENTES["logo"]).pack(side="left")
    if titulo:
        tk.Frame(izq, bg="#1A3A52", width=1).pack(side="left", fill="y", padx=16, pady=12)
        tk.Label(izq, text=titulo, bg=COLORES["fondo_topbar"],
                 fg=COLORES["texto_sidebar"], font=FUENTES["pequena"]).pack(side="left")

    if usuario:
        der = tk.Frame(bar, bg=COLORES["fondo_topbar"])
        der.pack(side="right", padx=20, fill="y")
        tk.Label(der, text="●", bg=COLORES["fondo_topbar"],
                 fg=COLORES["exito"], font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))
        tk.Label(der, text=usuario, bg=COLORES["fondo_topbar"],
                 fg=COLORES["texto_blanco"], font=FUENTES["pequena"]).pack(side="left")
    return bar


# Header de página
def crear_header_pagina(parent, titulo, subtitulo=""):
    frame = tk.Frame(parent, bg=COLORES["fondo"])
    frame.pack(fill="x", pady=(0, 4))
    tk.Label(frame, text=titulo,
             bg=COLORES["fondo"], fg=COLORES["texto"],
             font=FUENTES["titulo"]).pack(anchor="w")
    if subtitulo:
        tk.Label(frame, text=subtitulo,
                 bg=COLORES["fondo"], fg=COLORES["texto_suave"],
                 font=FUENTES["pequena"]).pack(anchor="w", pady=(1, 0))
    tk.Frame(frame, bg=COLORES["acento"], height=3).pack(fill="x", pady=(8, 0))
    return frame


# Barra de búsqueda
def crear_barra_busqueda(parent, var_busqueda, placeholder="Buscar..."):
    contenedor = tk.Frame(parent,
                          bg=COLORES["blanco"],
                          highlightthickness=1,
                          highlightbackground=COLORES["borde"],
                          highlightcolor=COLORES["acento"])
    tk.Label(contenedor, text="🔍", bg=COLORES["blanco"],
             font=FUENTES["pequena"], fg=COLORES["texto_suave"]).pack(side="left", padx=(8, 2))
    tk.Entry(contenedor,
             textvariable=var_busqueda,
             font=FUENTES["campo"],
             bg=COLORES["blanco"],
             fg=COLORES["texto"],
             relief="flat", bd=0,
             insertbackground=COLORES["acento"],
             width=22).pack(side="left", ipady=6, padx=(0, 8))
    return contenedor


# Alias de compatibilidad
def crear_header(parent, titulo, subtitulo=""):
    return crear_topbar(parent, titulo=titulo, subtitulo=subtitulo)


# Centrar ventana
def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    pos_x = (ventana.winfo_screenwidth()  // 2) - (ancho // 2)
    pos_y = (ventana.winfo_screenheight() // 2) - (alto  // 2)
    ventana.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")


# Tabla moderna
def crear_tabla(parent, columnas, anchos, height=18, show="headings"):
    contenedor = tk.Frame(parent,
                          bg=COLORES["fondo_panel"],
                          highlightthickness=1,
                          highlightbackground=COLORES["borde"])
    tabla = ttk.Treeview(contenedor, columns=columnas, show=show, height=height)
    for col, ancho in zip(columnas, anchos):
        tabla.heading(col, text=col, anchor="center")
        tabla.column(col, width=ancho, anchor="center", minwidth=60)

    tabla.tag_configure("par",      background=COLORES["tabla_par"])
    tabla.tag_configure("impar",    background=COLORES["tabla_impar"])
    tabla.tag_configure("activo",   background=COLORES["exito_light"],
                                    foreground=COLORES["exito"])
    tabla.tag_configure("inactivo", background=COLORES["peligro_light"],
                                    foreground=COLORES["peligro"])

    scroll = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    tabla.pack(fill="both", expand=True)

    return contenedor, tabla