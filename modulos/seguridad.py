import hashlib
from config import Config
from mongodb import coleccion_configuracion

async def establecer_clave_admin(update, nueva_clave: str):
    clave_hash = hashlib.sha256(nueva_clave.encode()).hexdigest()
    coleccion_configuracion.update_one(
        {"clave": "clave_admin_seguridad"},
        {"$set": {"valor": clave_hash}},
        upsert=True
    )
    return True

async def verificar_clave_admin(update, clave_introducida: str):
    dato = coleccion_configuracion.find_one({"clave": "clave_admin_seguridad"})
    if not dato or not dato["valor"]:
        return True
    clave_hash = hashlib.sha256(clave_introducida.encode()).hexdigest()
    return dato["valor"] == clave_hash
