from datos.mongo_dao import ClienteDAO, FuncionarioDAO, UsuarioDAO
from datos.vehiculo_dao import VehiculoDAO, ModeloImagenDAO
from datos.sql_dao import AlquilerDAO
from entidades.usuario import Usuario
from entidades.cliente import Cliente

## Negocio Clientes
class ClienteNegocio:

    def __init__(self):
        self._dao          = ClienteDAO()
        self._usuario_dao  = UsuarioDAO()
        self._alquiler_dao = AlquilerDAO()

    def registrar(self, cliente, usuario, contrasena):
        if self._dao.existe_identificacion(cliente.identificacion):
            raise ValueError("Ya existe un cliente registrado con esa identificación.")
        if self._dao.existe_correo(cliente.correo):
            raise ValueError("El correo ya está registrado.")
        if self._usuario_dao.existe_usuario(usuario):
            raise ValueError("El nombre de usuario ya está en uso.")
        
        ## Validar que sea mayor de edad
        if not cliente.es_mayor_de_edad(18):
            raise ValueError(
                f"El cliente debe ser mayor de 18 años para poder alquilar vehículos. "
                f"Edad actual: {cliente.calcular_edad()} años.")
        
        Usuario.validar_contrasena_nueva(contrasena)
        id_perfil = self._dao.insertar(cliente)
        usuario_nuevo = Usuario(nombre_usuario=usuario, contrasena=contrasena,
                                activo=True, tipo="cliente", id_perfil=id_perfil)
        self._usuario_dao.insertar(usuario_nuevo)

    def actualizar(self, identificacion, datos):
        if "correo" in datos and datos["correo"]:
            if self._dao.existe_correo(datos["correo"], excluir_id=identificacion):
                raise ValueError("El correo ya está registrado por otro cliente.")
        cliente_actual = self._dao.buscar_por_id(identificacion)
        if not cliente_actual:
            raise ValueError("Cliente no encontrado.")
        cliente_actualizado = Cliente(
            identificacion=identificacion,
            nombre=datos.get("nombre", cliente_actual.nombre),
            primer_apellido=datos.get("primer_apellido", cliente_actual.primer_apellido),
            segundo_apellido=datos.get("segundo_apellido", ""),
            fecha_nacimiento=datos.get("fecha_nacimiento") or None,
            telefono=datos.get("telefono", cliente_actual.telefono),
            correo=datos.get("correo", cliente_actual.correo),
            tipo_pago=datos.get("tipo_pago", cliente_actual.tipo_pago),
            datos_tarjeta=datos.get("datos_tarjeta", ""),
            nacionalidad=datos.get("nacionalidad", "Costarricense"),
        )
        
        ## Validar que siga siendo mayor de edad
        if not cliente_actualizado.es_mayor_de_edad(18):
            raise ValueError(
                f"El cliente debe ser mayor de 18 años para poder alquilar vehículos. "
                f"Edad actual: {cliente_actualizado.calcular_edad()} años.")
        
        self._dao.actualizar(identificacion, datos)

    def desactivar(self, identificacion):
        alquileres_activos = [alquiler for alquiler in self._alquiler_dao.obtener_por_cliente(identificacion)
                              if alquiler.estado in ("Pendiente", "En préstamo")]
        if alquileres_activos:
            raise ValueError("No se puede desactivar: el cliente tiene alquileres activos.")
        self._dao.eliminar_logico(identificacion)
        cliente = self._dao.buscar_por_id(identificacion)
        if cliente and cliente._id:
            usuario = self._usuario_dao.buscar_por_perfil(cliente._id)
            if usuario:
                self._usuario_dao.desactivar(usuario.nombre_usuario)

    def reactivar(self, identificacion):
        self._dao.actualizar(identificacion, {"activo": True})
        cliente = self._dao.buscar_por_id(identificacion)
        if cliente and cliente._id:
            usuario = self._usuario_dao.buscar_por_perfil(cliente._id)
            if usuario:
                self._usuario_dao.activar(usuario.nombre_usuario)

    def existe_identificacion(self, identificacion):
        return self._dao.existe_identificacion(identificacion)

    def obtener_todos(self):
        return self._dao.obtener_todos()

    def obtener_activos(self):
        return self._dao.obtener_activos()

    def buscar(self, identificacion):
        return self._dao.buscar_por_id(identificacion)


## Negocio Funcionarios
class FuncionarioNegocio:

    def __init__(self):
        self._dao         = FuncionarioDAO()
        self._usuario_dao = UsuarioDAO()

    def registrar(self, funcionario, usuario, contrasena):
        if self._dao.existe_identificacion(funcionario.identificacion):
            raise ValueError("Ya existe un funcionario registrado con esa identificación.")
        if self._usuario_dao.existe_usuario(usuario):
            raise ValueError("El nombre de usuario ya está en uso.")
        Usuario.validar_contrasena_nueva(contrasena)
        id_perfil = self._dao.insertar(funcionario)
        usuario_nuevo = Usuario(nombre_usuario=usuario, contrasena=contrasena,
                                activo=True, tipo="funcionario", id_perfil=id_perfil)
        self._usuario_dao.insertar(usuario_nuevo)

    def actualizar(self, identificacion, datos):
        self._dao.actualizar(identificacion, datos)

    def cambiar_estado(self, identificacion, estado):
        self._dao.cambiar_estado(identificacion, estado)

    def existe_identificacion(self, identificacion):
        return self._dao.existe_identificacion(identificacion)

    def obtener_todos(self):
        return self._dao.obtener_todos()

    def buscar(self, identificacion):
        return self._dao.buscar_por_id(identificacion)


## Negocio Vehiculos
class VehiculoNegocio:

    def __init__(self):
        self._dao          = VehiculoDAO()
        self._imagen_dao   = ModeloImagenDAO()
        self._alquiler_dao = AlquilerDAO()

    def registrar(self, vehiculo):
        if self._dao.existe_placa(vehiculo.numero_placa):
            raise ValueError("Ya existe un vehículo con esa placa.")
        if self._dao.existe_motor(vehiculo.numero_motor):
            raise ValueError("Ya existe un vehículo con ese número de motor.")
        return self._dao.insertar(vehiculo)

    def actualizar(self, placa, datos):
        self._dao.actualizar(placa, datos)

    def desactivar(self, placa):
        if self._alquiler_dao.vehiculo_tiene_alquiler_activo(placa):
            raise ValueError("No se puede desactivar: el vehículo tiene un alquiler activo.")
        self._dao.eliminar_logico(placa)

    def reactivar(self, placa):
        if self._alquiler_dao.vehiculo_tiene_alquiler_activo(placa):
            raise ValueError("No se puede reactivar: el vehículo tiene un alquiler activo.")
        self._dao.actualizar_disponibilidad(placa, True)

    def obtener_todos(self):
        return self._dao.obtener_todos()

    def obtener_disponibles(self):
        return self._dao.obtener_disponibles()

    def buscar(self, placa):
        return self._dao.buscar_por_placa(placa)

    def obtener_imagen(self, marca, modelo):
        return self._imagen_dao.buscar(marca, modelo)

    def guardar_imagen(self, marca, modelo, ruta):
        self._imagen_dao.actualizar(marca, modelo, ruta)

    def obtener_todas_imagenes(self):
        return self._imagen_dao.obtener_todos()