import re
from datetime import date, datetime

## Entidad Funcionario
class Funcionario:

    ESTADOS = ["Activo", "Inactivo"]

    def __init__(self, identificacion="", nacionalidad="", nombre="",
                 primer_apellido="", segundo_apellido="", fecha_nacimiento=None,
                 telefono="", direccion="", fecha_ingreso=None,
                 estado="Activo", _id=None):
        self._id              = _id
        self.identificacion   = identificacion
        self.nacionalidad     = nacionalidad
        self.nombre           = nombre
        self.primer_apellido  = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono         = telefono
        self.direccion        = direccion
        self.fecha_ingreso    = fecha_ingreso
        self.estado           = estado

    @property
    def identificacion(self):
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("La identificación es obligatoria.")
        valor_limpio = str(valor).strip().upper()
        ## Solo letras, números y guiones
        if not re.match(r'^[A-Z0-9\-]+$', valor_limpio):
            raise ValueError("La identificación solo puede contener letras, números y guiones.")
        ## Toda identificación debe tener al menos un número
        if not re.search(r'\d', valor_limpio):
            raise ValueError("La identificación debe contener al menos un número.")
        if len(valor_limpio) < 5:
            raise ValueError("La identificación debe tener al menos 5 caracteres.")
        self._identificacion = valor_limpio

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
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El teléfono es obligatorio.")
        ## Elimina separadores para contar solo dígitos
        solo_digitos = re.sub(r'[\s\-\+\(\)]', '', valor.strip())
        if not solo_digitos.isdigit():
            raise ValueError("El teléfono solo puede contener números.")
        if len(solo_digitos) < 8:
            raise ValueError("El teléfono debe tener al menos 8 dígitos.")
        self._telefono = valor.strip()

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        if not valor or not valor.strip():
            raise ValueError("La dirección es obligatoria.")
        if not re.search(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]', valor.strip()):
            raise ValueError("La dirección debe contener al menos una letra.")
        self._direccion = valor.strip()

    @property
    def fecha_nacimiento(self):
        return self._fecha_nacimiento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor):
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
        if isinstance(valor, datetime):
            valor = valor.date()
        if not isinstance(valor, date):
            raise ValueError("Fecha de nacimiento inválida.")
        hoy = date.today()
        edad = hoy.year - valor.year - ((hoy.month, hoy.day) < (valor.month, valor.day))
        if edad < 18:
            raise ValueError("El funcionario debe ser mayor de 18 años.")
        self._fecha_nacimiento = valor

    @property
    def fecha_ingreso(self):
        return self._fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor):
        if valor is None:
            self._fecha_ingreso = None
            return
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor or valor == "None":
                self._fecha_ingreso = None
                return
            try:
                valor = datetime.strptime(valor[:10], "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("La fecha de ingreso debe tener el formato AAAA-MM-DD.")
        if isinstance(valor, datetime):
            valor = valor.date()
        if not isinstance(valor, date):
            raise ValueError("Fecha de ingreso inválida.")
        self._fecha_ingreso = valor

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor not in self.ESTADOS:
            raise ValueError(f"Estado debe ser: {', '.join(self.ESTADOS)}.")
        self._estado = valor

    def nombre_completo(self):
        return f"{self._nombre} {self._primer_apellido} {self._segundo_apellido}".strip()

    def esta_activo(self):
        return self._estado == "Activo"

    def a_dict(self):
        return {
            "identificacion":   self._identificacion,
            "nacionalidad":     self._nacionalidad,
            "nombre":           self._nombre,
            "primer_apellido":  self._primer_apellido,
            "segundo_apellido": self._segundo_apellido,
            "fecha_nacimiento": str(self._fecha_nacimiento) if self._fecha_nacimiento else "",
            "telefono":         self._telefono,
            "direccion":        self._direccion,
            "fecha_ingreso":    str(self._fecha_ingreso) if self._fecha_ingreso else "",
            "estado":           self._estado,
        }

    def __str__(self):
        return f"{self.nombre_completo()} ({self._identificacion})"