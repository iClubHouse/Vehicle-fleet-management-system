import tkinter as tk
from interfaz.estilos import aplicar_tema
from interfaz.ventana_login import VentanaLogin
##Punto de entrada de la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    aplicar_tema(root)
    VentanaLogin(root)
    root.mainloop()