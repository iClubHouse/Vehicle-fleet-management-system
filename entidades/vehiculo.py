## Entidad Vehiculo
class Vehiculo:

    TIPOS        = ["Automóvil", "SUV", "Pick-up", "VAN"]
    TRANSMISIONES = ["Manual", "Automático"]
    COMBUSTIBLES  = ["Gasolina", "Diésel", "Eléctrico"]

    def __init__(self, numero_placa="", marca="", modelo="", tipo="Automóvil",
                 transmision="Automático", combustible="Gasolina", color="",
                 cantidad_pasajeros=5, cantidad_maletas=2, costo_diario=0.0,
                 numero_motor="", disponible=True, _id=None):
        self._id               = _id
        self.numero_placa      = numero_placa
        self.marca             = marca
        self.modelo            = modelo
        self.tipo              = tipo
        self.transmision       = transmision
        self.combustible       = combustible
        self.color             = color
        self.cantidad_pasajeros= cantidad_pasajeros
        self.cantidad_maletas  = cantidad_maletas
        self.costo_diario      = costo_diario
        self.numero_motor      = numero_motor
        self._disponible       = disponible

    @property
    def numero_placa(self):
        return self._numero_placa

    @numero_placa.setter
    def numero_placa(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El número de placa es obligatorio.")
        self._numero_placa = valor.strip().upper()

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
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if valor not in self.TIPOS:
            raise ValueError(f"Tipo debe ser: {', '.join(self.TIPOS)}.")
        self._tipo = valor

    @property
    def transmision(self):
        return self._transmision

    @transmision.setter
    def transmision(self, valor):
        if valor not in self.TRANSMISIONES:
            raise ValueError(f"Transmisión debe ser: {', '.join(self.TRANSMISIONES)}.")
        self._transmision = valor

    @property
    def combustible(self):
        return self._combustible

    @combustible.setter
    def combustible(self, valor):
        if valor not in self.COMBUSTIBLES:
            raise ValueError(f"Combustible debe ser: {', '.join(self.COMBUSTIBLES)}.")
        self._combustible = valor

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, valor):
        self._color = valor.strip() if valor else ""

    @property
    def cantidad_pasajeros(self):
        return self._cantidad_pasajeros

    @cantidad_pasajeros.setter
    def cantidad_pasajeros(self, valor):
        cantidad = int(valor)
        if cantidad < 1 or cantidad > 20:
            raise ValueError("La cantidad de pasajeros debe estar entre 1 y 20.")
        self._cantidad_pasajeros = cantidad

    @property
    def cantidad_maletas(self):
        return self._cantidad_maletas

    @cantidad_maletas.setter
    def cantidad_maletas(self, valor):
        self._cantidad_maletas = int(valor)

    @property
    def costo_diario(self):
        return self._costo_diario

    @costo_diario.setter
    def costo_diario(self, valor):
        costo = float(valor)
        if costo <= 0:
            raise ValueError("El costo diario debe ser mayor a 0.")
        self._costo_diario = costo

    @property
    def numero_motor(self):
        return self._numero_motor

    @numero_motor.setter
    def numero_motor(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El número de motor es obligatorio.")
        self._numero_motor = valor.strip()

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    def descripcion(self):
        return f"{self._marca} {self._modelo} ({self._numero_placa})"

    def a_dict(self):
        return {
            "numero_placa":       self._numero_placa,
            "marca":              self._marca,
            "modelo":             self._modelo,
            "tipo":               self._tipo,
            "transmision":        self._transmision,
            "combustible":        self._combustible,
            "color":              self._color,
            "cantidad_pasajeros": self._cantidad_pasajeros,
            "cantidad_maletas":   self._cantidad_maletas,
            "costo_diario":       self._costo_diario,
            "numero_motor":       self._numero_motor,
            "disponible":         self._disponible,
        }

    def __str__(self):
        return self.descripcion()
