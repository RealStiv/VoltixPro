from telegram import Update
from telegram.ext import ContextTypes
from mongodb import coleccion_pedidos
from config import Config

async def ver_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pedidos = list(coleccion_pedidos.find({"user_id": user_id}).sort("fecha", -1).limit(10))
    
    if not pedidos:
        await update.message.reply_text("📦 No tienes pedidos realizados aún")
        return
    
    texto = "📦 <b>TUS ÚLTIMOS PEDIDOS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for p in pedidos:
        texto += f"""• Servicio: {p.get('nombre_servicio', 'Desconocido')}
  Cantidad: {p.get('cantidad', 0)}
  Total: {Config.SIMBOLO}{p.get('total', 0):.2f}
  Estado: <b>{p.get('estado', 'Procesando')}</b>
  Fecha: {p.get('fecha', 'Sin fecha')}\n\n"""
    
    await update.message.reply_text(texto, parse_mode="HTML")
