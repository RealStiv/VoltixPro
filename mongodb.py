from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config

try:
    cliente = MongoClient(Config.MONGO_URI)
    cliente.admin.command("ping")
    print("✅ CONEXIÓN A MONGODB EXITOSA")
except ConnectionFailure:
    print("❌ ERROR: NO SE PUDO CONECTAR A LA BASE DE DATOS")
    raise

db = cliente[Config.NOMBRE_BASE_DATOS]

# TODAS CON NOMBRES IGUALES EN TODOS LOS ARCHIVOS
coleccion_usuarios = db["usuarios"]
coleccion_facturas = db["facturas"]
coleccion_paneles = db["paneles"]
coleccion_servicios = db["servicios"]
coleccion_categorias = db["categorias"]
coleccion_pedidos = db["pedidos"]
coleccion_configuracion = db["configuracion"]

# ÍNDICES PARA EVITAR DUPLICADOS Y VELOCIDAD
coleccion_usuarios.create_index("user_id", unique=True)
coleccion_categorias.create_index("nombre", unique=True)
coleccion_configuracion.create_index("tipo", unique=True)
