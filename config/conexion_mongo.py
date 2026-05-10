from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

## Conexión singleton a MongoDB
class ConexionMongo:
    _instancia = None
    _cliente   = None
    _db        = None

    HOST      = "YOUR_MONGO_CONNECTION_STRING"
    NOMBRE_DB = "AutoTrustDB"

    @classmethod
    def obtener_instancia(cls):
        if cls._instancia is None:
            cls._instancia = ConexionMongo()
        return cls._instancia

    def __init__(self):
        try:
            self._cliente = MongoClient(self.HOST, serverSelectionTimeoutMS=5000)
            self._cliente.admin.command("ping")
            self._db = self._cliente[self.NOMBRE_DB]
        except ConnectionFailure as e:
            raise ConnectionError(f"No se pudo conectar a MongoDB: {e}")

    def obtener_db(self):
        return self._db

    def cerrar(self):
        if self._cliente:
            self._cliente.close()
            ConexionMongo._instancia = None
