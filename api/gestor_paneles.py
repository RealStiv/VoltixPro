from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
from bson import ObjectId

from config import Config
from mongodb import coleccion_paneles
from modulos.auditoria import registrar_accion
from texto import t
from interfaces.botones import menu_panel


async def agregar_panel_smm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.message.reply_text(await t("acceso_denegado"))
        return

    texto_completo = " ".join(context.args)
    partes = [p.strip() for p in texto_completo.split("|")]

    if len(partes) != 4:
        await update.message.reply_text(
            "⚠️ **FORMATO INCORRECTO**\n\n✅ Usa exactamente así:\n`/agregarpanel NOMBRE | URL | API_KEY | PORCENTAJE`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver a Paneles", callback_data="ad_paneles")]
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
                [InlineKeyboardButton("🔙 Volver a Paneles", callback_data="ad_paneles")]
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

    await registrar_accion(user_id, "Agregó panel", nombre)
    await update.message.reply_text(
        f"✅ **PANEL AGREGADO CORRECTAMENTE**\n\n📌 Nombre: {nombre}\n🔗 URL: {url}\n📈 Ganancia: {porcentaje}%",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Agregar otro", callback_data="pan_agregar")],
            [InlineKeyboardButton("📋 Ver lista con ID", callback_data="pan_ver_ids")],
            [InlineKeyboardButton("🔙 Menú Administrador", callback_data="menu_admin")]
        ])
    )


async def ver_ids_paneles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.callback_query.answer(await t("acceso_denegado"), show_alert=True)
        return

    paneles = list(coleccion_paneles.find({}))
    if not paneles:
        texto = "❌ No hay paneles registrados aún."
    else:
        texto = "📋 **LISTA DE PANELES (CON SU ID)**\n\n"
        for p in paneles:
            texto += f"🔹 {p['nombre']}\n🆔 ID: `{p['_id']}`\n🔗 {p['url']}\n📈 Ganancia: {p['porcentaje_ganancia']}%\n✅ Activo: {'Sí' if p['activo'] else 'No'}\n\n"
    
    await update.callback_query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Agregar nuevo", callback_data="pan_agregar")],
            [InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]
        ])
    )


async def editar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.callback_query.answer(await t("acceso_denegado"), show_alert=True)
        return

    if not context.args:
        await update.callback_query.edit_message_text(
            "✏️ **EDITAR PANEL**\n\nEscribe el comando así:\n`/editarpanel ID | CAMPO | NUEVO_VALOR`\n\nCampos permitidos: nombre, url, api_key, porcentaje_ganancia, activo",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]
            ])
        )
        return

    texto_completo = " ".join(context.args)
    partes = [p.strip() for p in texto_completo.split("|")]

    if len(partes) != 3:
        await update.message.reply_text("❌ Formato incorrecto, usa: `/editarpanel ID | CAMPO | NUEVO_VALOR`")
        return

    try:
        id_panel = ObjectId(partes[0])
    except:
        await update.message.reply_text("❌ El ID no es válido")
        return

    campo = partes[1].lower()
    nuevo_valor = partes[2]
    campos_permitidos = ["nombre", "url", "api_key", "porcentaje_ganancia", "activo"]

    if campo not in campos_permitidos:
        await update.message.reply_text(f"❌ Campo inválido. Usa uno: {', '.join(campos_permitidos)}")
        return

    if campo == "porcentaje_ganancia":
        try:
            nuevo_valor = float(nuevo_valor)
        except:
            await update.message.reply_text("❌ El porcentaje debe ser un número")
            return

    if campo == "activo":
        nuevo_valor = nuevo_valor.lower() in ["si", "sí", "true", "1"]

    panel = coleccion_paneles.find_one({"_id": id_panel})
    if not panel:
        await update.message.reply_text("❌ No existe ese panel")
        return

    coleccion_paneles.update_one({"_id": id_panel}, {"$set": {campo: nuevo_valor}})
    await registrar_accion(user_id, "Editó panel", f"{panel['nombre']} → {campo} modificado")
    await update.message.reply_text(f"✅ Panel «{panel['nombre']}» actualizado correctamente")


async def eliminar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.callback_query.answer(await t("acceso_denegado"), show_alert=True)
        return

    if not context.args:
        await update.callback_query.edit_message_text(
            "❌ **ELIMINAR PANEL**\n\nEscribe el comando así:\n`/eliminarpanel ID_DEL_PANEL`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]
            ])
        )
        return

    try:
        id_panel = ObjectId(context.args[0])
    except:
        await update.message.reply_text("❌ El ID no es válido")
        return

    panel = coleccion_paneles.find_one({"_id": id_panel})
    if not panel:
        await update.message.reply_text("❌ Panel no encontrado")
        return

    nombre_eliminado = panel["nombre"]
    coleccion_paneles.delete_one({"_id": id_panel})
    await registrar_accion(user_id, "Eliminó panel", nombre_eliminado)
    await update.message.reply_text(f"✅ Panel «{nombre_eliminado}» eliminado permanentemente")
