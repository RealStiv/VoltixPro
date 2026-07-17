from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import Config
from mongodb import coleccion_categorias, coleccion_servicios
from margenes import calcular_precios
from texto import t

def clasificar_servicio(nombre_servicio: str) -> str:
    nombre = nombre_servicio.lower()
    if "instagram" in nombre: return "📸 Instagram"
    elif "tiktok" in nombre: return "🎵 TikTok"
    elif "youtube" in nombre: return "📺 YouTube"
    elif "facebook" in nombre: return "📘 Facebook"
    elif "twitter" in nombre or "x " in nombre: return "🐦 X / Twitter"
    elif "whatsapp" in nombre or "grupos" in nombre: return "💬 WhatsApp"
    elif "discord" in nombre: return "🎮 Discord"
    elif "telegram" in nombre or "canales" in nombre: return "✈️ Telegram"
    else: return "🌐 Otros Servicios"

async def mostrar_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categorias = list(coleccion_categorias.find({"activo": True}).sort("nombre", 1))
    if not categorias:
        await update.message.reply_text("❌ No hay categorías disponibles aún")
        return
    
    botones = []
    for cat in categorias:
        cantidad = coleccion_servicios.count_documents({"categoria": cat["nombre"], "activo": True})
        botones.append([InlineKeyboardButton(f"{cat['nombre']} ({cantidad})", callback_data=f"ver_cat_{cat['nombre']}")])
    
    botones.append([InlineKeyboardButton("🔙 VOLVER AL MENÚ", callback_data="ad_salir")])
    await update.message.reply_text(t("tienda_inicio"), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(botones))

async def mostrar_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE, categoria: str):
    query = update.callback_query
    servicios = list(coleccion_servicios.find({"categoria": categoria, "activo": True}).sort("nombre", 1))
    
    if not servicios:
        await query.edit_message_text("❌ No hay servicios en esta categoría")
        return
    
    botones = []
    for serv in servicios:
        precios = calcular_precios(serv["costo_proveedor"])
        botones.append([InlineKeyboardButton(
            f"{serv['nombre']} | {Config.SIMBOLO}{precios['precio_venta']:.3f}",
            callback_data=f"serv_{serv['id_externo']}"
        )])
    
    botones.append([InlineKeyboardButton("🔙 VOLVER A CATEGORÍAS", callback_data="ad_salir")])
    await query.edit_message_text(f"📂 <b>{categoria}</b>\nSelecciona un servicio:", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(botones))
