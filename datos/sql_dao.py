from config.conexion_sql import ConexionSQL
from entidades.modelos import Alquiler, Devolucion, Danio

## DAO Alquiler (SQL Server)
class AlquilerDAO:

    def __init__(self):
        self._sql = ConexionSQL.obtener_instancia()

    def insertar(self, alquiler):
        try:
            cursor = self._sql.obtener_cursor()
            sql = """
                INSERT INTO Alquiler (id_cliente, id_vehiculo, fecha_inicio,
                    fecha_devolucion_planificada, cantidad_dias, costo_diario,
                    costo_base, impuesto, seguro_diario, costo_seguro, total, estado)
                OUTPUT INSERTED.id_alquiler
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, alquiler.a_tuple_insercion())
            fila = cursor.fetchone()
            self._sql.confirmar()
            return fila[0] if fila else None
        except Exception:
            self._sql.revertir()
            raise

    def actualizar_estado(self, id_alquiler, nuevo_estado):
        try:
            cursor = self._sql.obtener_cursor()
            cursor.execute(
                "UPDATE Alquiler SET estado = ? WHERE id_alquiler = ?",
                (nuevo_estado, id_alquiler)
            )
            self._sql.confirmar()
        except Exception:
            self._sql.revertir()
            raise

    def buscar_por_id(self, id_alquiler):
        cursor = self._sql.obtener_cursor()
        cursor.execute("SELECT * FROM Alquiler WHERE id_alquiler = ?", (id_alquiler,))
        return self._fila_a_alquiler(cursor.fetchone())

    def obtener_por_cliente(self, id_cliente):
        cursor = self._sql.obtener_cursor()
        cursor.execute(
            "SELECT * FROM Alquiler WHERE id_cliente = ? ORDER BY fecha_inicio DESC",
            (id_cliente,)
        )
        return [self._fila_a_alquiler(f) for f in cursor.fetchall()]

    def obtener_pendientes_en_prestamo(self):
        cursor = self._sql.obtener_cursor()
        cursor.execute(
            "SELECT * FROM Alquiler WHERE estado IN ('Pendiente','En préstamo') ORDER BY fecha_inicio"
        )
        return [self._fila_a_alquiler(f) for f in cursor.fetchall()]

    def obtener_todos(self):
        cursor = self._sql.obtener_cursor()
        cursor.execute("SELECT * FROM Alquiler ORDER BY fecha_registro DESC")
        return [self._fila_a_alquiler(f) for f in cursor.fetchall()]

    def vehiculo_tiene_alquiler_activo(self, id_vehiculo):
        cursor = self._sql.obtener_cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Alquiler WHERE id_vehiculo = ? AND estado IN ('Pendiente','En préstamo')",
            (id_vehiculo,)
        )
        fila = cursor.fetchone()
        if not fila:
            return False
        return fila[0] > 0

    def vehiculo_tiene_reserva_en_fechas(self, id_vehiculo, fecha_inicio, fecha_fin):
        cursor = self._sql.obtener_cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM Alquiler
            WHERE id_vehiculo = ?
              AND estado IN ('Pendiente','En préstamo')
              AND NOT (fecha_devolucion_planificada < ? OR fecha_inicio > ?)
        """, (id_vehiculo, fecha_inicio, fecha_fin))
        fila = cursor.fetchone()
        if not fila:
            return False
        return fila[0] > 0

    def obtener_alquileres_por_periodo(self, fecha_inicio, fecha_fin):
        cursor = self._sql.obtener_cursor()
        cursor.execute("""
            SELECT * FROM Alquiler
            WHERE fecha_inicio BETWEEN ? AND ?
            ORDER BY fecha_inicio
        """, (fecha_inicio, fecha_fin))
        return [self._fila_a_alquiler(f) for f in cursor.fetchall()]

    def _fila_a_alquiler(self, fila):
        if not fila:
            return None
        try:
            alquiler_objeto = Alquiler()
            alquiler_objeto.id_alquiler                  = fila[0]
            alquiler_objeto.id_cliente                   = fila[1]
            alquiler_objeto.id_vehiculo                  = fila[2]
            alquiler_objeto.fecha_inicio                 = fila[3]
            alquiler_objeto.fecha_devolucion_planificada = fila[4]
            alquiler_objeto.cantidad_dias                = int(fila[5])
            alquiler_objeto.costo_diario                 = float(fila[6])
            alquiler_objeto.costo_base                   = float(fila[7])
            alquiler_objeto.impuesto                     = float(fila[8])
            alquiler_objeto.seguro_diario                = float(fila[9])
            alquiler_objeto.costo_seguro                 = float(fila[10])
            alquiler_objeto.total                        = float(fila[11])
            alquiler_objeto.estado                       = fila[12]
            return alquiler_objeto
        except (TypeError, ValueError, IndexError):
            return None


## DAO Devolucion (SQL Server)
class DevolucionDAO:

    def __init__(self):
        self._sql = ConexionSQL.obtener_instancia()

    def insertar(self, devolucion):
        try:
            cursor = self._sql.obtener_cursor()
            sql = """
                INSERT INTO Devolucion (id_alquiler, fecha_devolucion_real,
                    dias_atraso, monto_penalizacion, tiene_danio, total_devolucion)
                OUTPUT INSERTED.id_devolucion
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, devolucion.a_tuple_insercion())
            fila = cursor.fetchone()
            self._sql.confirmar()
            return fila[0] if fila else None
        except Exception:
            self._sql.revertir()
            raise

    def buscar_por_alquiler(self, id_alquiler):
        cursor = self._sql.obtener_cursor()
        cursor.execute("SELECT * FROM Devolucion WHERE id_alquiler = ?", (id_alquiler,))
        return self._fila_a_devolucion(cursor.fetchone())

    def _fila_a_devolucion(self, fila):
        if not fila:
            return None
        try:
            devolucion_objeto = Devolucion()
            devolucion_objeto.id_devolucion         = fila[0]
            devolucion_objeto.id_alquiler           = fila[1]
            devolucion_objeto.fecha_devolucion_real = fila[2]
            devolucion_objeto.dias_atraso           = fila[3]
            devolucion_objeto.monto_penalizacion    = float(fila[4])
            devolucion_objeto.tiene_danio           = bool(fila[5])
            devolucion_objeto.total_devolucion      = float(fila[6])
            return devolucion_objeto
        except (TypeError, ValueError, IndexError):
            return None


## DAO Danio (SQL Server)
class DanioDAO:

    def __init__(self):
        self._sql = ConexionSQL.obtener_instancia()

    def insertar(self, danio):
        try:
            cursor = self._sql.obtener_cursor()
            sql = """
                INSERT INTO Danio (id_devolucion, descripcion, costo_danio)
                OUTPUT INSERTED.id_danio
                VALUES (?, ?, ?)
            """
            cursor.execute(sql, danio.a_tuple_insercion())
            fila = cursor.fetchone()
            self._sql.confirmar()
            return fila[0] if fila else None
        except Exception:
            self._sql.revertir()
            raise

    def obtener_por_devolucion(self, id_devolucion):
        cursor = self._sql.obtener_cursor()
        cursor.execute("SELECT * FROM Danio WHERE id_devolucion = ?", (id_devolucion,))
        return [self._fila_a_danio(f) for f in cursor.fetchall()]

    def _fila_a_danio(self, fila):
        if not fila:
            return None
        try:
            danio_objeto = Danio()
            danio_objeto.id_danio      = fila[0]
            danio_objeto.id_devolucion = fila[1]
            danio_objeto.descripcion   = fila[2]
            danio_objeto.costo_danio   = float(fila[3])
            return danio_objeto
        except (TypeError, ValueError, IndexError):
            return None