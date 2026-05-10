import re
from datetime import date, datetime

## Entidad Cliente
class Cliente:

    def __init__(self, identificacion="", nacionalidad="", nombre="",
                 primer_apellido="", segundo_apellido="", fecha_nacimiento=None,
                 telefono="", correo="", tipo_pago="efectivo", datos_tarjeta="",
                 activo=True, _id=None):
        self._id             = _id
        self.identificacion  = identificacion
        self.nacionalidad    = nacionalidad
        self.nombre          = nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido= segundo_apellido
        self.fecha_nacimiento= fecha_nacimiento
        self.telefono        = telefono
        self.correo          = correo
        self.tipo_pago       = tipo_pago
        self.datos_tarjeta   = datos_tarjeta
        self._activo         = activo

    @property
    def identificacion(self):
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("La identificación es obligatoria.")
        self._identificacion = str(valor).strip()

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre es obligatorio.")
        nombre_limpio = valor.strip()
        if re.search(r'\d', nombre_limpio):
            raise ValueError("El nombre no puede contener números.")
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', nombre_limpio):
            raise ValueError("El nombre debe contener al menos una letra.")
        self._nombre = nombre_limpio.title()

    @property
    def primer_apellido(self):
        return self._primer_apellido

    @primer_apellido.setter
    def primer_apellido(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El primer apellido es obligatorio.")
        apellido_limpio = valor.strip()
        if re.search(r'\d', apellido_limpio):
            raise ValueError("El primer apellido no puede contener números.")
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', apellido_limpio):
            raise ValueError("El primer apellido debe contener al menos una letra.")
        self._primer_apellido = apellido_limpio.title()

    @property
    def segundo_apellido(self):
        return self._segundo_apellido

    @segundo_apellido.setter
    def segundo_apellido(self, valor):
        if not valor or not str(valor).strip():
            self._segundo_apellido = ""
            return
        apellido_limpio = valor.strip()
        if re.search(r'\d', apellido_limpio):
            raise ValueError("El segundo apellido no puede contener números.")
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', apellido_limpio):
            raise ValueError("El segundo apellido debe contener al menos una letra.")
        self._segundo_apellido = apellido_limpio.title()

    @property
    def nacionalidad(self):
        return self._nacionalidad

    @nacionalidad.setter
    def nacionalidad(self, valor):
        self._nacionalidad = valor.strip() if valor else "Costarricense"

    @property
    def fecha_nacimiento(self):
        return self._fecha_nacimiento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor):
        ## Acepta None o cadena vacía → sin fecha
        if valor is None:
            self._fecha_nacimiento = None
            return
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor or valor == "None":
                self._fecha_nacimiento = None
                return
            try:
                valor = datetime.strptime(valor[:10], "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("La fecha de nacimiento debe tener el formato AAAA-MM-DD.")
        ## Convierte datetime a date si viene de MongoDB (campo Date nativo)
        if isinstance(valor, datetime):
            valor = valor.date()
        if not isinstance(valor, date):
            raise ValueError("Fecha de nacimiento inválida.")
        self._fecha_nacimiento = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El teléfono es obligatorio.")
        telefono_limpio = valor.strip()
        ## Elimina separadores válidos y verifica que sean solo dígitos
        solo_digitos = re.sub(r'[\s\-\+\(\)]', '', telefono_limpio)
        if not solo_digitos.isdigit():
            raise ValueError("El teléfono solo puede contener números.")
        if len(solo_digitos) < 7:
            raise ValueError("El teléfono debe tener al menos 7 dígitos.")
        self._telefono = telefono_limpio

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if valor and not re.match(r"[^@]+@[^@]+\.[^@]+", valor):
            raise ValueError("El correo electrónico no es válido.")
        self._correo = valor.strip().lower() if valor else ""

    @property
    def tipo_pago(self):
        return self._tipo_pago

    @tipo_pago.setter
    def tipo_pago(self, valor):
        opciones = ["efectivo", "tarjeta"]
        if valor not in opciones:
            raise ValueError(f"Tipo de pago debe ser: {', '.join(opciones)}.")
        self._tipo_pago = valor

    @property
    def datos_tarjeta(self):
        return self._datos_tarjeta

    @datos_tarjeta.setter
    def datos_tarjeta(self, valor):
        self._datos_tarjeta = valor.strip() if valor else ""

    @property
    def activo(self):
        return self._activo

    @activo.setter
    def activo(self, valor):
        self._activo = bool(valor)

    def nombre_completo(self):
        return f"{self._nombre} {self._primer_apellido} {self._segundo_apellido}".strip()

    def calcular_edad(self):
        if not self._fecha_nacimiento:
            return 0
        hoy = date.today()
        fn  = self._fecha_nacimiento
        return hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))

    def es_mayor_de_edad(self, edad_minima=18):
        return self.calcular_edad() >= edad_minima

    def a_dict(self):
        return {
            "identificacion":   self._identificacion,
            "nacionalidad":     self._nacionalidad,
            "nombre":           self._nombre,
            "primer_apellido":  self._primer_apellido,
            "segundo_apellido": self._segundo_apellido,
            "fecha_nacimiento": str(self._fecha_nacimiento) if self._fecha_nacimiento else "",
            "telefono":         self._telefono,
            "correo":           self._correo,
            "tipo_pago":        self._tipo_pago,
            "datos_tarjeta":    self._datos_tarjeta,
            "activo":           self._activo,
        }

    def __str__(self):
        return f"{self.nombre_completo()} ({self._identificacion})"