from datetime import datetime
from mongodb import coleccion_auditoria

async def registrar_accion(usuario_id: int, nombre_accion: str, detalles: str = ""):
    coleccion_auditoria.insert_one({
        "usuario_id": usuario_id,
        "accion": nombre_accion,
        "detalles": detalles,
        "fecha": datetime.now()
    })

async def ver_historial(update, context):
    from config import Config
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.callback_query.answer("❌ Sin permiso", show_alert=True)
        return

    registros = list(coleccion_auditoria.find({}).sort("fecha", -1).limit(20))
    if not registros:
        texto = "📜 Aún no hay registros de actividad."
    else:
        texto = "📜 **ÚLTIMAS ACCIONES REALIZADAS:**\n\n"
        for r in registros:
            fecha = r["fecha"].strftime("%d/%m %H:%M")
            texto += f"[{fecha}] ID {r['usuario_id']}: {r['accion']}\n{r['detalles']}\n\n"

    await update.callback_query.edit_message_text(
        texto, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Volver", callback_data="acc_menu")
        ]])
    )
