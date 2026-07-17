from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

preguntas = [
    {
        "pregunta": "¿Cómo funciona el sistema de niveles?",
        "respuesta": "Sube de nivel según lo que gastes: Bronce → Plata → Oro → Diamante. Cada uno te da mayor descuento."
    },
    {
        "pregunta": "¿Cuánto tarda en llegar el servicio?",
        "respuesta": "Depende del proveedor: entre 5 minutos y 24 horas. Verás el tiempo estimado en cada uno."
    },
    {
        "pregunta": "¿Puedo pedir reembolso?",
        "respuesta": "Solo si el servicio no se entregó o falló totalmente. Envíanos tu número de pedido."
    }
]

async def ver_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = "❓ **PREGUNTAS FRECUENTES**\n\n"
    botones = []
    for idx, p in enumerate(preguntas):
        botones.append([InlineKeyboardButton(p["pregunta"][:30]+"...", callback_data=f"faq_{idx}")])
    botones.append([InlineKeyboardButton("📩 Contactar soporte", callback_data="soporte_contactar")])
    botones.append([InlineKeyboardButton("🔙 Volver al perfil", callback_data="menu_perfil")])

    await update.callback_query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(botones))

async def perfil_completo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from modulos.niveles_limites import calcular_nivel_usuario
    usuario = coleccion_usuarios.find_one({"user_id": update.effective_user.id})
    nivel, descuento = await calcular_nivel_usuario(update.effective_user.id)
    
    texto = f"""👤 TU PERFIL

🆔 ID: `{usuario['user_id']}`
🏅 Nivel: {nivel.upper()}
📉 Descuento: {descuento}%
💵 Saldo: ${usuario['saldo']:.2f}
💸 Total gastado: ${usuario.get('gasto_total',0):.2f}
🎫 Tu código de referido: `{usuario.get('codigo_referido')}`
💰 Ganado por referidos: ${usuario.get('saldo_referidos',0):.2f}
💱 Moneda: {usuario.get('moneda','USD')}
"""
    botones = [
        [InlineKeyboardButton("🎁 Referidos", callback_data="ref_menu")],
        [InlineKeyboardButton("💱 Cambiar moneda", callback_data="conf_moneda")],
        [InlineKeyboardButton("❓ Ayuda y FAQ", callback_data="faq_menu")],
        [InlineKeyboardButton("🔙 Menú principal", callback_data="ad_salir")]
    ]
    await update.callback_query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(botones))
