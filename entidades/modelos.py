## Entidad ModeloImagen
class ModeloImagen:

    def __init__(self, marca="", modelo="", ruta_imagen="", _id=None):
        self._id         = _id
        self.marca       = marca
        self.modelo      = modelo
        self.ruta_imagen = ruta_imagen

    @property
    def marca(self):
        return self._marca

    @marca.setter
    def marca(self, valor):
        if not valor or not valor.strip():
            raise ValueError("La marca es obligatoria.")
        self._marca = valor.strip()

    @property
    def modelo(self):
        return self._modelo

    @modelo.setter
    def modelo(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El modelo es obligatorio.")
        self._modelo = valor.strip()

    @property
    def ruta_imagen(self):
        return self._ruta_imagen

    @ruta_imagen.setter
    def ruta_imagen(self, valor):
        self._ruta_imagen = valor.strip() if valor else ""

    def a_dict(self):
        return {
            "marca":       self._marca,
            "modelo":      self._modelo,
            "ruta_imagen": self._ruta_imagen,
        }

    def __str__(self):
        return f"{self._marca} {self._modelo}"


## Entidad Alquiler
class Alquiler:

    ESTADOS = ["Pendiente", "En préstamo", "Devuelto", "Cancelado"]

    def __init__(self, id_cliente="", id_vehiculo="", fecha_inicio=None,
                 fecha_devolucion_planificada=None, cantidad_dias=1,
                 costo_diario=0.0, costo_base=0.0, impuesto=0.0,
                 seguro_diario=0.0, costo_seguro=0.0, total=0.0,
                 estado="Pendiente", id_alquiler=None):
        self.id_alquiler                  = id_alquiler
        self.id_cliente                   = id_cliente
        self.id_vehiculo                  = id_vehiculo
        self.fecha_inicio                 = fecha_inicio
        self.fecha_devolucion_planificada = fecha_devolucion_planificada
        self.cantidad_dias                = cantidad_dias
        self.costo_diario                 = costo_diario
        self.costo_base                   = costo_base
        self.impuesto                     = impuesto
        self.seguro_diario                = seguro_diario
        self.costo_seguro                 = costo_seguro
        self.total                        = total
        self.estado                       = estado

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor not in self.ESTADOS:
            raise ValueError(f"Estado inválido: {valor}")
        self._estado = valor

    @property
    def cantidad_dias(self):
        return self._cantidad_dias

    @cantidad_dias.setter
    def cantidad_dias(self, valor):
        cantidad = int(valor)
        if cantidad < 1:
            raise ValueError("La cantidad de días debe ser al menos 1.")
        self._cantidad_dias = cantidad

    def a_tuple_insercion(self):
        return (
            self.id_cliente, self.id_vehiculo,
            self.fecha_inicio, self.fecha_devolucion_planificada,
            self._cantidad_dias, self.costo_diario, self.costo_base,
            self.impuesto, self.seguro_diario, self.costo_seguro,
            self.total, self._estado,
        )

    def __str__(self):
        return f"Alquiler #{self.id_alquiler} - {self.id_cliente} | {self._estado}"


## Entidad Devolucion
class Devolucion:

    def __init__(self, id_alquiler=0, fecha_devolucion_real=None,
                 dias_atraso=0, monto_penalizacion=0.0,
                 tiene_danio=False, total_devolucion=0.0, id_devolucion=None):
        self.id_devolucion         = id_devolucion
        self.id_alquiler           = id_alquiler
        self.fecha_devolucion_real = fecha_devolucion_real
        self.dias_atraso           = dias_atraso
        self.monto_penalizacion    = monto_penalizacion
        self.tiene_danio           = tiene_danio
        self.total_devolucion      = total_devolucion

    def a_tuple_insercion(self):
        return (
            self.id_alquiler, self.fecha_devolucion_real,
            self.dias_atraso, self.monto_penalizacion,
            1 if self.tiene_danio else 0,
            self.total_devolucion,
        )

    def __str__(self):
        return f"Devolución #{self.id_devolucion} - Alquiler #{self.id_alquiler}"


## Entidad Danio
class Danio:

    def __init__(self, id_devolucion=0, descripcion="", costo_danio=0.0, id_danio=None):
        self.id_danio      = id_danio
        self.id_devolucion = id_devolucion
        self.descripcion   = descripcion
        self.costo_danio   = costo_danio

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("La descripción del daño es obligatoria.")
        self._descripcion = str(valor).strip()

    @property
    def costo_danio(self):
        return self._costo_danio

    @costo_danio.setter
    def costo_danio(self, valor):
        costo = float(valor)
        if costo < 0:
            raise ValueError("El costo del daño no puede ser negativo.")
        self._costo_danio = costo

    def a_tuple_insercion(self):
        return (self.id_devolucion, self._descripcion, self._costo_danio)

    def __str__(self):
        return f"Daño #{self.id_danio}: {self._descripcion} - ₡{self._costo_danio:,.2f}"