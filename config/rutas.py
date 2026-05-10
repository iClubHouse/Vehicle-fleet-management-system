import os

## Rutas base del proyecto
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGENES_DIR  = os.path.join(BASE_DIR, "assets", "imagenes")
LOGO_PATH     = os.path.join(BASE_DIR, "assets", "imagenes", "logo", "logo.png")

def ruta_imagen(nombre_archivo):
    if not nombre_archivo:
        return ""
    if os.path.isabs(nombre_archivo):
        return nombre_archivo
    return os.path.join(BASE_DIR, nombre_archivo)

def ruta_relativa(ruta_absoluta):
    ## Convierte ruta absoluta a relativa desde BASE_DIR
    try:
        return os.path.relpath(ruta_absoluta, BASE_DIR)
    except ValueError:
        return ruta_absoluta