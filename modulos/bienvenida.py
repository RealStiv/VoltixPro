from texto import t

async def generar_mensaje_bienvenida(usuario: dict):
    mensaje = t("bienvenida")
    if usuario.get("rol") == "vip":
        mensaje += "\n🌟 <b>NOTA:</b> Eres usuario VIP, tienes precios especiales y soporte prioritario."
    elif usuario.get("rol") == "admin":
        mensaje += "\n🔐 <b>NOTA:</b> Tienes acceso completo al panel de administración."
    return mensaje
