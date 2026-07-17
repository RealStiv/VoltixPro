import random
import string
from mongodb import coleccion_usuarios, coleccion_configuracion

def generar_codigo_referido(longitud=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=longitud))

async def asignar_codigo_referido(usuario_id: int):
    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    if usuario and usuario.get("codigo_referido"):
        return usuario["codigo_referido"]
    
    codigo = generar_codigo_referido()
    while coleccion_usuarios.find_one({"codigo_referido": codigo}):
        codigo = generar_codigo_referido()
    
    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"codigo_referido": codigo}},
        upsert=True
    )
    return codigo

async def verificar_referido(usuario_id: int, codigo: str):
    ya_tiene = coleccion_usuarios.find_one({"user_id": usuario_id}).get("referido_por")
    if ya_tiene:
        return False, "Ya fuiste registrado por un referido anteriormente"
    
    dueño = coleccion_usuarios.find_one({"codigo_referido": codigo.upper()})
    if not dueño:
        return False, "Código de referido no válido"
    if dueño["user_id"] == usuario_id:
        return False, "No puedes usar tu propio código"
    
    recompensa = coleccion_configuracion.find_one({"clave": "recompensa_referido"})["valor"]
    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"referido_por": codigo}}
    )
    coleccion_usuarios.update_one(
        {"user_id": dueño["user_id"]},
        {"$inc": {"saldo_referidos": recompensa, "saldo": recompensa}}
    )
    return True, f"✅ Registrado correctamente. {dueño['nombre']} recibió ${recompensa} de regalo"
