from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
from config import Config
from mongodb import coleccion_paneles

async def agregar_panel_smm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permiso para usar esta función.")
        return

    texto_completo = " ".join(context.args)
    partes = [p.strip() for p in texto_completo.split("|")]

    if len(partes) != 4:
        await update.message.reply_text(
            "⚠️ **FORMATO INCORRECTO**\n\n✅ Usa exactamente así:\n`/agregarpanel NOMBRE | URL | API_KEY | PORCENTAJE`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver a Paneles", callback_data="ad_panel")]
            ])
        )
        return

    nombre, url, api_key, porcentaje = partes
    try:
        porcentaje = float(porcentaje)
    except:
        await update.message.reply_text(
            "❌ El porcentaje solo puede ser un número, sin símbolos.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver a Paneles", callback_data="ad_panel")]
            ])
        )
        return

    coleccion_paneles.insert_one({
        "nombre": nombre,
        "url": url,
        "api_key": api_key,
        "porcentaje_ganancia": porcentaje,
        "activo": True,
        "creado_en": datetime.now()
    })

    await update.message.reply_text(
        f"✅ **PANEL AGREGADO CORRECTAMENTE**\n\n📌 Nombre: {nombre}\n🔗 URL: {url}\n📈 Ganancia: {porcentaje}%",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Agregar otro", callback_data="pan_agregar")],
            [InlineKeyboardButton("📋 Ver lista completa", callback_data="pan_lista")],
            [InlineKeyboardButton("🔙 Menú Administrador", callback_data="menu_admin")]
        ])
    )

async def listar_paneles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    paneles = list(coleccion_paneles.find({"activo": True}))
    if not paneles:
        texto = "❌ No hay paneles activos registrados aún."
    else:
        texto = "📋 **LISTA DE PANELES ACTIVOS:**\n\n"
        for idx, p in enumerate(paneles, 1):
            texto += f"{idx}. {p['nombre']}\n🔗 {p['url']}\n📈 Ganancia: {p['porcentaje_ganancia']}%\n\n"
    
    await update.callback_query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Agregar nuevo", callback_data="pan_agregar")],
            [InlineKeyboardButton("🔙 Volver", callback_data="ad_panel")]
        ])
    )

async def editar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "✏️ **EDITAR PANEL**\n\nEscribe el comando así:\n`/editarpanel ID | CAMPO | NUEVO_VALOR`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Volver", callback_data="ad_panel")]
        ])
    )

async def eliminar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "❌ **ELIMINAR PANEL**\n\nEscribe el comando así:\n`/borrarpanel ID_DEL_PANEL`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Volver", callback_data="ad_panel")]
        ])
    )
