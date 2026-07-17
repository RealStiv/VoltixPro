import requests
from faker import Faker
from telegram import Update
from telegram.ext import ContextTypes

fake = Faker("es_ES")

async def generar_dorks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dorks = [
        "site:*.smm-panel.com 'api' 'servicios' 'precios' 'ilimitado'",
        "site:instagram.com 'comprar seguidores' 'reales' 'seguros' 'sin caer'",
        "site:tiktok.com 'vistas' 'me gusta' 'seguidores activos'",
        "site:github.com 'panel smm' 'python' 'codigo completo' 'gratis'",
        "site:*.pastebin.com 'bin' 'cc' 'smm' 'servicios' 'precios'",
        "site:*.blogspot.com 'comprar likes' 'instagram' 'barato' 'entrega rapida'"
    ]
    await update.message.reply_text("🔍 <b>DORKS GENERADOS:</b>\n\n" + "\n".join(dorks), parse_mode="HTML")

async def validar_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args[0]) < 6 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Uso correcto: /bin 123456")
        return
    
    bin_num = context.args[0][:6]
    try:
        respuesta = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        
        texto = f"""💳 <b>VALIDACIÓN DE BIN: {bin_num}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏦 Banco emisor: {datos.get('bank', {}).get('name', 'Desconocido')}
🌍 País: {datos.get('country', {}).get('name', 'Desconocido')}
🔢 Tipo de tarjeta: {datos.get('type', 'Desconocido')}
🔄 Red de pago: {datos.get('scheme', 'Desconocido')}
💳 Es prepago: {datos.get('prepaid', 'No')}
"""
        await update.message.reply_text(texto, parse_mode="HTML")
    except Exception as e:
        print(f"Error validando BIN: {e}")
        await update.message.reply_text("❌ BIN inválido, servicio ocupado o error de conexión")

async def generar_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cantidad = int(context.args[0]) if context.args and context.args[0].isdigit() else 5
    except:
        cantidad = 5
    cantidad = max(1, min(cantidad, 20))
    
    tarjetas = []
    for _ in range(cantidad):
        tarjetas.append(f"{fake.credit_card_number()}|{fake.credit_card_expire()}|{fake.credit_card_security_code()}")
    
    await update.message.reply_text("💳 <b>TARJETAS DE PRUEBA GENERADAS:</b>\n\n" + "\n".join(tarjetas), parse_mode="HTML")
