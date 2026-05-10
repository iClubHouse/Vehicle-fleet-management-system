import pyodbc

## Conexión
class ConexionSQL:
    _instancia = None

    CADENA = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=YOUR_SERVER;"
        "DATABASE=YOUR_DATABASE;"
        "Trusted_Connection=yes;"
    )

    @classmethod
    def obtener_instancia(cls):
       
        if cls._instancia is not None:
            return cls._instancia
        try:
            obj = object.__new__(cls)           
            obj._conexion = pyodbc.connect(cls.CADENA, timeout=10)
            obj._conexion.autocommit = False
            cls._instancia = obj
            return cls._instancia
        except pyodbc.Error as e:
            raise ConnectionError(
                f"No se pudo conectar a SQL Server (LocalDB).\n"
                f"Verifique que el servicio esté activo.\n\nDetalle: {e}"
            )

    def __init__(self):
        
        pass

    def obtener_conexion(self):
        return self._conexion

    def obtener_cursor(self):
        ## Reconexión automática si la conexión fue cerrada por inactividad
        try:
            self._conexion.cursor().execute("SELECT 1")
        except Exception:
            try:
                self._conexion = pyodbc.connect(self.CADENA, timeout=10)
                self._conexion.autocommit = False
            except pyodbc.Error as e:
                ConexionSQL._instancia = None
                raise ConnectionError(f"Error al reconectar a SQL Server.\n{e}")
        return self._conexion.cursor()

    def confirmar(self):
        self._conexion.commit()

    def revertir(self):
        self._conexion.rollback()

    def cerrar(self):
        if hasattr(self, "_conexion") and self._conexion:
            self._conexion.close()
        ConexionSQL._instancia = None