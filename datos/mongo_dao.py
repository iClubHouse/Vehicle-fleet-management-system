from bson import ObjectId
from config.conexion_mongo import ConexionMongo
from entidades.cliente import Cliente
from entidades.funcionario import Funcionario
from entidades.usuario import Usuario

## DAO Clientes (MongoDB)
class ClienteDAO:

    def __init__(self):
        db = ConexionMongo.obtener_instancia().obtener_db()
        self._col = db["clientes"]

    def insertar(self, cliente):
        resultado = self._col.insert_one(cliente.a_dict())
        return resultado.inserted_id

    def actualizar(self, identificacion, datos):
        self._col.update_one({"identificacion": identificacion}, {"$set": datos})

    def eliminar_logico(self, identificacion):
        self._col.update_one({"identificacion": identificacion}, {"$set": {"activo": False}})

    def eliminar(self, identificacion):
        self._col.delete_one({"identificacion": identificacion})

    def buscar_por_id(self, identificacion):
        doc = self._col.find_one({"identificacion": identificacion})
        return self._doc_a_cliente(doc) if doc else None

    def buscar_por_correo(self, correo):
        doc = self._col.find_one({"correo": correo})
        return self._doc_a_cliente(doc) if doc else None

    def obtener_todos(self):
        ## Itera con protección individual: un documento corrupto no rompe la lista completa
        result = []
        for d in self._col.find().sort("nombre", 1):
            try:
                result.append(self._doc_a_cliente(d))
            except Exception:
                pass
        return result

    def obtener_activos(self):
        result = []
        for d in self._col.find({"activo": True}).sort("nombre", 1):
            try:
                result.append(self._doc_a_cliente(d))
            except Exception:
                pass
        return result

    def existe_identificacion(self, identificacion):
        return self._col.count_documents({"identificacion": identificacion}) > 0

    def existe_correo(self, correo, excluir_id=None):
        filtro = {"correo": correo}
        if excluir_id:
            filtro["identificacion"] = {"$ne": excluir_id}
        return self._col.count_documents(filtro) > 0

    def _doc_a_cliente(self, doc):
        return Cliente(
            identificacion=doc.get("identificacion", ""),
            nacionalidad=doc.get("nacionalidad", ""),
            nombre=doc.get("nombre", ""),
            primer_apellido=doc.get("primer_apellido", ""),
            segundo_apellido=doc.get("segundo_apellido", ""),
            fecha_nacimiento=doc.get("fecha_nacimiento"),
            telefono=doc.get("telefono", ""),
            correo=doc.get("correo", ""),
            tipo_pago=doc.get("tipo_pago", "efectivo"),
            datos_tarjeta=doc.get("datos_tarjeta", ""),
            activo=doc.get("activo", True),
            _id=doc.get("_id"),
        )


## DAO Funcionarios (MongoDB)
class FuncionarioDAO:

    def __init__(self):
        db = ConexionMongo.obtener_instancia().obtener_db()
        self._col = db["funcionarios"]

    def insertar(self, funcionario):
        resultado = self._col.insert_one(funcionario.a_dict())
        return resultado.inserted_id

    def actualizar(self, identificacion, datos):
        self._col.update_one({"identificacion": identificacion}, {"$set": datos})

    def eliminar(self, identificacion):
        self._col.delete_one({"identificacion": identificacion})

    def cambiar_estado(self, identificacion, estado):
        self._col.update_one({"identificacion": identificacion}, {"$set": {"estado": estado}})

    def buscar_por_id(self, identificacion):
        doc = self._col.find_one({"identificacion": identificacion})
        return self._doc_a_funcionario(doc) if doc else None

    def buscar_por_object_id(self, oid):
        doc = self._col.find_one({"_id": oid})
        return self._doc_a_funcionario(doc) if doc else None

    def obtener_todos(self):
        return [self._doc_a_funcionario(d) for d in self._col.find().sort("nombre", 1)]

    def existe_identificacion(self, identificacion):
        return self._col.count_documents({"identificacion": identificacion}) > 0

    def _doc_a_funcionario(self, doc):
        return Funcionario(
            identificacion=doc.get("identificacion", ""),
            nacionalidad=doc.get("nacionalidad", ""),
            nombre=doc.get("nombre", ""),
            primer_apellido=doc.get("primer_apellido", ""),
            segundo_apellido=doc.get("segundo_apellido", ""),
            fecha_nacimiento=doc.get("fecha_nacimiento"),
            telefono=doc.get("telefono", ""),
            direccion=doc.get("direccion", ""),
            fecha_ingreso=doc.get("fecha_ingreso"),
            estado=doc.get("estado", "Activo"),
            _id=doc.get("_id"),
        )


## DAO Usuarios (MongoDB)
class UsuarioDAO:

    def __init__(self):
        db = ConexionMongo.obtener_instancia().obtener_db()
        self._col = db["usuarios"]

    def insertar(self, usuario):
        resultado = self._col.insert_one(usuario.a_dict())
        return resultado.inserted_id

    def actualizar_contrasena(self, nombre_usuario, nueva):
        self._col.update_one({"nombre_usuario": nombre_usuario}, {"$set": {"contrasena": nueva}})

    def desactivar(self, nombre_usuario):
        self._col.update_one({"nombre_usuario": nombre_usuario}, {"$set": {"activo": False}})

    def activar(self, nombre_usuario):
        self._col.update_one({"nombre_usuario": nombre_usuario}, {"$set": {"activo": True}})

    def eliminar(self, nombre_usuario):
        self._col.delete_one({"nombre_usuario": nombre_usuario})

    def autenticar(self, nombre_usuario, contrasena):
        doc = self._col.find_one({
            "nombre_usuario": nombre_usuario,
            "contrasena":     contrasena,
            "activo":         True,
        })
        return self._doc_a_usuario(doc) if doc else None

    def buscar_por_perfil(self, id_perfil):
        doc = self._col.find_one({"id_perfil": id_perfil})
        return self._doc_a_usuario(doc) if doc else None

    def existe_usuario(self, nombre_usuario):
        return self._col.count_documents({"nombre_usuario": nombre_usuario}) > 0

    def _doc_a_usuario(self, doc):
        return Usuario(
            nombre_usuario=doc.get("nombre_usuario", ""),
            contrasena=doc.get("contrasena", ""),
            activo=doc.get("activo", True),
            tipo=doc.get("tipo", "cliente"),
            id_perfil=doc.get("id_perfil"),
            _id=doc.get("_id"),
        )