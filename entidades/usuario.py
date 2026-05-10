import re

## Entidad Usuario
class Usuario:

    TIPOS = ["funcionario", "cliente"]

    ## Regex: mínimo 8 chars, 1 mayúscula, 1 minúscula, 1 dígito, 1 especial
    _RE_CONTRASENA = re.compile(
        r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$'
    )

    def __init__(self, nombre_usuario="", contrasena="", activo=True,
                 tipo="cliente", id_perfil=None, _id=None):
        self._id            = _id
        self.nombre_usuario = nombre_usuario
        self._activo        = activo
        self.tipo           = tipo
        self._id_perfil     = id_perfil
        ## Asignación directa: no revalida contraseñas ya guardadas en BD
        self._contrasena    = contrasena

    @staticmethod
    def validar_contrasena_nueva(valor):
        """Aplica la política completa. Llamar antes de registrar o cambiar contraseña."""
        if not valor or not Usuario._RE_CONTRASENA.match(valor):
            raise ValueError(
                "La contraseña debe tener mínimo 8 caracteres, "
                "al menos 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial.")

    @property
    def nombre_usuario(self):
        return self._nombre_usuario

    @nombre_usuario.setter
    def nombre_usuario(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre de usuario es obligatorio.")
        self._nombre_usuario = valor.strip()

    @property
    def contrasena(self):
        return self._contrasena

    @contrasena.setter
    def contrasena(self, valor):
        if not valor or len(valor) < 3:
            raise ValueError("La contraseña debe tener al menos 3 caracteres.")
        self._contrasena = valor

    @property
    def activo(self):
        return self._activo

    @activo.setter
    def activo(self, valor):
        self._activo = bool(valor)

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if valor not in self.TIPOS:
            raise ValueError(f"Tipo debe ser: {', '.join(self.TIPOS)}.")
        self._tipo = valor

    @property
    def id_perfil(self):
        return self._id_perfil

    @id_perfil.setter
    def id_perfil(self, valor):
        self._id_perfil = valor

    def es_funcionario(self):
        return self._tipo == "funcionario"

    def a_dict(self):
        return {
            "nombre_usuario": self._nombre_usuario,
            "contrasena":     self._contrasena,
            "activo":         self._activo,
            "tipo":           self._tipo,
            "id_perfil":      self._id_perfil,
        }

    def __str__(self):
        return f"{self._nombre_usuario} ({self._tipo})"