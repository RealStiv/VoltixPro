import base64

def generar_enlace_categoria(bot_username: str, nombre_categoria: str):
    codificado = base64.b64encode(nombre_categoria.encode()).decode()
    return f"https://t.me/{bot_username}?start=cat_{codificado}"

def generar_enlace_servicio(bot_username: str, id_servicio: str):
    return f"https://t.me/{bot_username}?start=srv_{id_servicio}"
