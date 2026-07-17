from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    MessageHandler, filters
)
from datetime import datetime
from config import Config
from texto import t
from facturas import crear_factura_completa, plantilla_factura
from mongodb import coleccion_facturas, coleccion_usuarios
from interfaces.botones import botones_factura

ESPERANDO_MONTO = 1
ESPERANDO_COMPROBANTE = 2

def obtener_conv_pagos():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 Recargar Saldo$"), iniciar_recarga)],
        states={
            ESPERANDO_MONTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_monto)],
            ESPERANDO_COMPROBANTE: [MessageHandler(filters.ALL & ~filters.COMMAND, recibir_comprobante)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancelar)],
        allow_reentry=True
    )

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operación cancelada")
    context.user_data.clear()
    return ConversationHandler.END

async def iniciar_recarga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t("recarga_instruccion"), parse_mode="HTML")
    await update.message.reply_text("✍️ Escribe el monto que deseas recargar:")
    return ESPERANDO_MONTO

async def recibir_monto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        monto = float(update.message.text.strip())
        if monto < Config.MONTO_MINIMO:
            await update.message.reply_text(f"❌ El monto mínimo es {Config.SIMBOLO}{Config.MONTO_MINIMO:.2f}")
            return ESPERANDO_MONTO
        context.user_data["monto_recarga"] = monto
        await update.message.reply_text("📷 Ahora envía la foto del comprobante o archivo TXT/PDF:")
        return ESPERANDO_COMPROBANTE
    except:
        await update.message.reply_text("❌ Escribe un valor numérico válido")
        return ESPERANDO_MONTO

async def recibir_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    monto = context.user_data.get("monto_recarga")
    
    if not monto:
        await update.message.reply_text("❌ No se encontró el monto de recarga")
        return ConversationHandler.END

    # Obtener archivo
    archivo = None
    if update.message.photo:
        archivo = update.message.photo[-1].file_id
    elif update.message.document:
        archivo = update.message.document.file_id
    elif update.message.text:
        archivo = update.message.text.strip()
    else:
        await update.message.reply_text("❌ Debes enviar una foto, archivo o texto del comprobante")
        return ConversationHandler.END
    
    # Crear y guardar factura
    factura = crear_factura_completa({"monto": monto, "archivo": archivo}, usuario)
    coleccion_facturas.insert_one(factura)
    
    # Enviar a administrador
    botones = botones_factura(factura["numero"])
    await context.bot.send_message(Config.ADMIN_ID, plantilla_factura(factura), parse_mode="HTML", reply_markup=botones)
    
    if archivo and not archivo.startswith("http"):
        if update.message.photo:
            await context.bot.send_photo(Config.ADMIN_ID, archivo)
        elif update.message.document:
            await context.bot.send_document(Config.ADMIN_ID, archivo)
    else:
        await context.bot.send_message(Config.ADMIN_ID, f"📝 Comprobante/Referencia:\n{archivo}")
    
    # Confirmar al usuario
    await update.message.reply_text(f"✅ Comprobante recibido\n🧾 Número de factura: <code>{factura['numero']}</code>\nEn revisión...", parse_mode="HTML")
    context.user_data.clear()
    return ConversationHandler.END

async def procesar_factura(update: Update, context: ContextTypes.DEFAULT_TYPE, numero: str = None, aprobar = None, monto = None):
    query = update.callback_query
    if not numero:
        datos = query.data.split("_")
        numero = datos[2]
        aprobar = datos[1] == "ok"
    
    factura = coleccion_facturas.find_one({"numero": numero})
    if not factura:
        await query.answer("❌ Factura no encontrada", show_alert=True)
        return
    
    if aprobar:
        # Aprobar recarga
        usuario = coleccion_usuarios.find_one({"user_id": factura["user_id"]})
        saldo_actual = usuario.get("saldo", 0.0)
        nuevo_saldo = saldo_actual + factura["monto"]
        coleccion_usuarios.update_one({"user_id": factura["user_id"]}, {"$set": {"saldo": nuevo_saldo}})
        coleccion_facturas.update_one({"numero": numero}, {"$set": {"estado": "APROBADO", "procesado_en": datetime.now()}})
        
        await query.edit_message_text(f"✅ <b>FACTURA {numero} APROBADA</b>\nSaldo agregado correctamente", parse_mode="HTML")
        await context.bot.send_message(factura["user_id"], t("pago_aprobado", saldo=nuevo_saldo, simbolo=Config.SIMBOLO), parse_mode="HTML")
    
    else:
        # Rechazar recarga
        coleccion_facturas.update_one({"numero": numero}, {"$set": {"estado": "RECHAZADO", "procesado_en": datetime.now()}})
        await query.edit_message_text(f"❌ <b>FACTURA {numero} RECHAZADA</b>", parse_mode="HTML")
        await context.bot.send_message(factura["user_id"], t("pago_rechazado", motivo="Comprobante no válido o datos incorrectos"), parse_mode="HTML")
