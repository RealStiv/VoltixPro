from telegram import Update, InputFile
from telegram.ext import ContextTypes
from config import Config
from mongodb import coleccion_configuracion, coleccion_usuarios
from modulos.auditoria import registrar_accion

async def obtener_ajuste(clave: str, defecto=None):
    dato = coleccion_configuracion.find_one({"clave": clave})
    return dato["valor"] if dato else defecto

async def cambiar_ajuste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso: /cambiar NOMBRE_BOT Tu Nuevo Nombre")
        return

    clave = context.args[0]
    valor = " ".join(context.args[1:])

    claves_permitidas = [
        "nombre_bot", "emoji_principal", "mensaje_bienvenida",
        "pie_pagina", "reglas"
    ]

    if clave not in claves_permitidas:
        return await update.message.reply_text("Opciones válidas:\n" + "\n".join(claves_permitidas))

    coleccion_configuracion.update_one(
        {"clave": clave},
        {"$set": {"valor": valor}},
        upsert=True
    )
    await registrar_accion(admin_id, "Modificó apariencia", f"{clave}: {valor}")
    await update.message.reply_text(f"✅ Cambiado correctamente: {clave}")

async def bienvenida_personalizada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = await obtener_ajuste("nombre_bot", "VOLTIXPRO")
    emoji = await obtener_ajuste("emoji_principal", "⚡")
    mensaje = await obtener_ajuste("mensaje_bienvenida")
    foto_id = await obtener_ajuste("foto_bienvenida")
    reglas = await obtener_ajuste("reglas")
    pie = await obtener_ajuste("pie_pagina")

    texto_final = f"""{emoji} **{nombre} V4**

{mensaje}

📋 Reglas básicas:
{reglas}

{pie}
"""
    if foto_id:
        await update.message.reply_photo(photo=foto_id, caption=texto_final, parse_mode="Markdown")
    else:
        await update.message.reply_text(texto_final, parse_mode="Markdown")

async def subir_foto_bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        coleccion_configuracion.update_one({"clave": "foto_bienvenida"}, {"$set": {"valor": file_id}})
        await registrar_accion(update.effective_user.id, "Cambió foto de bienvenida", "")
        await update.message.reply_text("✅ Foto guardada y se mostrará siempre al inicio")
