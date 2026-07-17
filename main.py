import sys
import os
import certifi
import traceback
os.environ['SSL_CERT_FILE'] = certifi.where()

print("="*60)
print("📢 PASO 1: INICIANDO SCRIPT")
print(f"🐍 VERSIÓN DE PYTHON: {sys.version}")
print("="*60)

try:
    print("📢 PASO 2: CARGANDO LIBRERÍAS...")
    import warnings
    warnings.filterwarnings("ignore")
    from dotenv import load_dotenv
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
    from flask import Flask
    import asyncio
    from threading import Thread
    print("✅ PASO 2: TODAS LAS LIBRERÍAS CARGADAS")
except Exception as e:
    print(f"❌ ERROR EN PASO 2: NO SE PUDO CARGAR LIBRERÍAS")
    print(f"📝 DETALLE: {str(e)}")
    print(f"🔍 TRAZA COMPLETA:\n{traceback.format_exc()}")
    sys.exit(1)

print("="*60)
print("📢 PASO 3: LEYENDO VARIABLES DE ENTORNO...")
try:
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    MONGO_URI = os.getenv("MONGO_URI")

    if not BOT_TOKEN:
        raise ValueError("Falta la variable BOT_TOKEN")
    if not ADMIN_ID:
        raise ValueError("Falta la variable ADMIN_ID")
    
    print(f"✅ PASO 3: VARIABLES CARGADAS")
    print(f"🔑 TOKEN: {BOT_TOKEN[:10]}...")
    print(f"👤 ADMIN ID: {ADMIN_ID}")
except Exception as e:
    print(f"❌ ERROR EN PASO 3: VARIABLES")
    print(f"📝 DETALLE: {str(e)}")
    print(f"🔍 TRAZA COMPLETA:\n{traceback.format_exc()}")
    sys.exit(1)

print("="*60)
print("📢 PASO 4: CARGANDO TUS MÓDULOS Y ARCHIVOS...")
try:
    from config import Config
    from mongodb import iniciar_configuracion
    print("✅ PASO 4: MÓDULOS PRINCIPALES CARGADOS")
except Exception as e:
    print(f"❌ ERROR EN PASO 4: FALTA ARCHIVO O ESTÁ MAL ESCRITO")
    print(f"📝 DETALLE: {str(e)}")
    print(f"🔍 TRAZA COMPLETA:\n{traceback.format_exc()}")
    print("💡 Revisa que config.py y mongodb.py existan y no tengan errores")
    sys.exit(1)

print("="*60)
print("📢 PASO 5: CONFIGURANDO SERVIDOR WEB...")
try:
    PUERTO = int(os.getenv("PORT", 8080))
    servidor = Flask(__name__)

    @servidor.route('/')
    def estado():
        return "✅ VOLTIXPRO | DIAGNÓSTICO ACTIVO"

    def arrancar_web():
        servidor.run(host="0.0.0.0", port=PUERTO, use_reloader=False)
    print("✅ PASO 5: SERVIDOR LISTO")
except Exception as e:
    print(f"❌ ERROR EN PASO 5: FLASK")
    print(f"📝 DETALLE: {str(e)}")
    print(f"🔍 TRAZA COMPLETA:\n{traceback.format_exc()}")
    sys.exit(1)

print("="*60)
print("📢 PASO 6: DEFINIENDO FUNCIÓN PRUEBA...")
async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📩 MENSAJE RECIBIDO DE: {update.effective_user.id}")
    await update.message.reply_text(f"""✅ TODO FUNCIONA PERFECTO!
👤 Tu ID: {update.effective_user.id}
🔑 Token: {BOT_TOKEN[:10]}...
⚡ Ya estamos conectados correctamente""")
print("✅ PASO 6: FUNCIÓN DE RESPUESTA LISTA")

print("="*60)
print("📢 PASO 7: CONECTANDO A TELEGRAM...")
async def ejecutar_bot():
    try:
        print("🔍 Probando conexión a base de datos...")
        await iniciar_configuracion()
        print("✅ BASE DE DATOS CONECTADA")

        bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", inicio))

        await bot_app.bot.delete_webhook(drop_pending_updates=True)
        print("✅ WEBHOOK LIMPIO")

        print("="*60)
        print("🎉 🚀 BOT TOTALMENTE LISTO Y ESCUCHANDO")
        print("="*60)

        await bot_app.run_polling(drop_pending_updates=True, close_loop=False)

    except Exception as e:
        print(f"❌ ERROR EN CONEXIÓN O EJECUCIÓN")
        print(f"📝 DETALLE: {str(e)}")
        print(f"🔍 TRAZA COMPLETA:\n{traceback.format_exc()}")

if __name__ == "__main__":
    try:
        Thread(target=arrancar_web, daemon=True).start()
        asyncio.run(ejecutar_bot())
    except Exception as e:
        print(f"❌ ERROR GENERAL DEL SISTEMA")
        print(f"📝 DETALLE: {str(e)}")
        print(f"🔍 TRAZA COMPLETA:\n{traceback.format_exc()}")
