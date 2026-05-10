from config.conexion_mongo import ConexionMongo
from entidades.vehiculo import Vehiculo
from entidades.modelos import ModeloImagen

## Mapas de normalización para campos con variantes conocidas en la base de datos
_NORMALIZAR_TIPO = {
    "automovil":  "Automóvil",
    "automóvil":  "Automóvil",
    "suv":        "SUV",
    "pick-up":    "Pick-up",
    "pick up":    "Pick-up",
    "pickup":     "Pick-up",
    "van":        "VAN",
}

_NORMALIZAR_TRANSMISION = {
    "automatico":  "Automático",
    "automático":  "Automático",
    "manual":      "Manual",
}

_NORMALIZAR_COMBUSTIBLE = {
    "gasolina": "Gasolina",
    "diesel":   "Diésel",
    "diésel":   "Diésel",
    "electrico":"Eléctrico",
    "eléctrico":"Eléctrico",
}

def _normalizar(valor, mapa, por_defecto):
    ## Busca el valor en el mapa usando clave en minúsculas; retorna por defecto si no encuentra
    if not valor:
        return por_defecto
    return mapa.get(str(valor).strip().lower(), valor)


## DAO Vehiculos (MongoDB)
class VehiculoDAO:

    def __init__(self):
        base_datos = ConexionMongo.obtener_instancia().obtener_db()
        self._col  = base_datos["vehiculos"]

    def insertar(self, vehiculo):
        resultado = self._col.insert_one(vehiculo.a_dict())
        return resultado.inserted_id

    def actualizar(self, placa, datos):
        self._col.update_one({"numero_placa": placa}, {"$set": datos})

    def eliminar_logico(self, placa):
        self._col.update_one({"numero_placa": placa}, {"$set": {"disponible": False}})

    def eliminar(self, placa):
        self._col.delete_one({"numero_placa": placa})

    def buscar_por_placa(self, placa):
        doc = self._col.find_one({"numero_placa": placa.upper()})
        return self._doc_a_vehiculo(doc) if doc else None

    def obtener_todos(self):
        return [self._doc_a_vehiculo(d) for d in self._col.find().sort("marca", 1)]

    def obtener_disponibles(self):
        return [self._doc_a_vehiculo(d)
                for d in self._col.find({"disponible": True}).sort("marca", 1)]

    def buscar_por_tipo(self, tipo):
        return [self._doc_a_vehiculo(d)
                for d in self._col.find({"disponible": True, "tipo": tipo})]

    def actualizar_disponibilidad(self, placa, disponible):
        self._col.update_one({"numero_placa": placa}, {"$set": {"disponible": disponible}})

    def existe_placa(self, placa, excluir=None):
        if excluir:
            filtro = {"$and": [
                {"numero_placa": placa.upper()},
                {"numero_placa": {"$ne": excluir.upper()}}
            ]}
        else:
            filtro = {"numero_placa": placa.upper()}
        return self._col.count_documents(filtro) > 0

    def existe_motor(self, motor):
        return self._col.count_documents({"numero_motor": motor}) > 0

    def _doc_a_vehiculo(self, doc):
        tipo       = _normalizar(doc.get("tipo"),       _NORMALIZAR_TIPO,        "Automóvil")
        transmision= _normalizar(doc.get("transmision"),_NORMALIZAR_TRANSMISION, "Automático")
        combustible= _normalizar(doc.get("combustible"),_NORMALIZAR_COMBUSTIBLE, "Gasolina")

        return Vehiculo(
            numero_placa      = doc.get("numero_placa", ""),
            marca             = doc.get("marca", ""),
            modelo            = doc.get("modelo", ""),
            tipo              = tipo,
            transmision       = transmision,
            combustible       = combustible,
            color             = doc.get("color", ""),
            cantidad_pasajeros= doc.get("cantidad_pasajeros", 5),
            cantidad_maletas  = doc.get("cantidad_maletas", 2),
            costo_diario      = doc.get("costo_diario", 0.0),
            numero_motor      = doc.get("numero_motor", ""),
            disponible        = doc.get("disponible", True),
            _id               = doc.get("_id"),
        )


## DAO ModeloImagen (MongoDB)
class ModeloImagenDAO:

    def __init__(self):
        base_datos = ConexionMongo.obtener_instancia().obtener_db()
        self._col  = base_datos["modelos_imagen"]

    def insertar(self, modelo_imagen):
        resultado = self._col.insert_one(modelo_imagen.a_dict())
        return resultado.inserted_id

    def actualizar(self, marca, modelo, nueva_ruta):
        self._col.update_one(
            {"marca": marca, "modelo": modelo},
            {"$set": {"ruta_imagen": nueva_ruta}},
            upsert=True,
        )

    def eliminar(self, marca, modelo):
        self._col.delete_one({"marca": marca, "modelo": modelo})

    def buscar(self, marca, modelo):
        doc = self._col.find_one({"marca": marca, "modelo": modelo})
        return self._doc_a_modelo(doc) if doc else None

    def obtener_todos(self):
        return [self._doc_a_modelo(d)
                for d in self._col.find().sort([("marca", 1), ("modelo", 1)])]

    def _doc_a_modelo(self, doc):
        return ModeloImagen(
            marca       = doc.get("marca", ""),
            modelo      = doc.get("modelo", ""),
            ruta_imagen = doc.get("ruta_imagen", ""),
            _id         = doc.get("_id"),
        )