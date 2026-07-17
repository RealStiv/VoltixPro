import sys
import os
import certifi
import nest_asyncio
import time
import logging
import traceback
from datetime import datetime

# ==================================================
# 📢 CONFIGURACIÓN DE REGISTROS DETALLADOS
# ==================================================
RUTA_LOG = "voltixpro_logs.txt"

formato_registro = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(mensaje)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

logger = logging.getLogger("VoltixPro")
logger.setLevel(logging.DEBUG)

consola = logging.StreamHandler(sys.stdout)
consola.setFormatter(formato_registro)
logger.addHandler(consola)

archivo = logging.FileHandler(RUTA_LOG, encoding="utf-8")
archivo.setFormatter(formato_registro)
logger.addHandler(archivo)

def log(mensaje, nivel="INFO"):
    niveles = {
        "INFO": logger.info,
        "PASO": logger.info,
        "EXITO": logger.info,
        "ADVERTENCIA": logger.warning,
        "ERROR": logger.error,
        "DETALLE": logger.debug
    }
    funcion = niveles.get(nivel, logger.info)
    funcion(mensaje, extra={"mensaje": mensaje})


# ==================================================
# 🚀 INICIO DEL SISTEMA
# ==================================================
log("="*70, "PASO")
log("⚡ INICIANDO VOLTIXPRO V4 CON REGISTRO COMPLETO", "PASO")
log("="*70, "PASO")
log(f"🐍 Versión de Python: {sys.version}", "DETALLE")

log("🔧 Aplicando corrección de conflictos de bucle...", "PASO")
nest_asyncio.apply()
os.environ['SSL_CERT_FILE'] = certifi.where()
log("✅ Corrección aplicada", "EXITO")


# ==================================================
# 📦 CARGA DE LIBRERÍAS
# ==================================================
log("📦 Cargando librerías y módulos...", "PASO")
try:
    import warnings
    warnings.filterwarnings("ignore")
    from dotenv import load_dotenv
    from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.ext import (
        ApplicationBuilder, CommandHandler, ContextTypes,
        CallbackQueryHandler, MessageHandler, filters, ConversationHandler
    )
    from flask import Flask
    import asyncio
    from threading import Thread
    log("✅ Todas las librerías cargadas correctamente", "EXITO")
except Exception as e:
    log(f"❌ ERROR CARGANDO LIBRERÍAS: {str(e)}", "ERROR")
    log(f"🔍 Traza completa:\n{traceback.format_exc()}", "ERROR")
    sys.exit(1)


# ==================================================
# ⚙️ VARIABLES DE ENTORNO
# ==================================================
log("⚙️ Leyendo variables de configuración...", "PASO")
try:
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    MONGO_URI = os.getenv("MONGO_URI")

    if not BOT_TOKEN:
        raise ValueError("No se encontró la variable BOT_TOKEN")
    if not ADMIN_ID:
        raise ValueError("No se encontró la variable ADMIN_ID")
    
    log(f"✅ Variables cargadas", "EXITO")
    log(f"🔑 Token: {BOT_TOKEN[:12]}...", "DETALLE")
    log(f"👤 ID Administrador: {ADMIN_ID}", "DETALLE")
    log(f"🌐 Base de datos: {MONGO_URI[:25]}...", "DETALLE")
except Exception as e:
    log(f"❌ ERROR EN VARIABLES: {str(e)}", "ERROR")
    log(f"🔍 Traza completa:\n{traceback.format_exc()}", "ERROR")
    sys.exit(1)


# ==================================================
# ✅ VERIFICACIÓN DE CANAL
# ==================================================
CANAL_OBLIGATORIO = "@Voltix_Pro"

async def verificar_suscripcion(user_id, bot):
    try:
        log(f"🔍 Comprobando membresía de {user_id} en {CANAL_OBLIGATORIO}", "DETALLE")
        miembro = await bot.get_chat_member(chat_id=CANAL_OBLIGATORIO, user_id=user_id)
        estados_validos = ["member", "administrator", "creator"]
        es_miembro = miembro.status in estados_validos
        
        if es_miembro:
            log(f"✅ Usuario {user_id} SÍ está suscrito", "EXITO")
        else:
            log(f"⚠️ Usuario {user_id} NO está suscrito, estado: {miembro.status}", "ADVERTENCIA")
        
        return es_miembro
    except Exception as e:
        log(f"❌ Error al revisar membresía: {str(e)}", "ERROR")
        return False


# ==================================================
# 🎨 BOTONES DEFINIDOS DIRECTAMENTE AQUÍ
# ==================================================
log("🎨 Cargando diseños de botones...", "PASO")
menu_suscripcion = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔗 IR AL CANAL", url="https://t.me/Voltix_Pro")],
    [InlineKeyboardButton("✅ YA ME SUSCRIBÍ", callback_data="verificar_suscripcion")]
])

menu_principal = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛍️ VER TIENDA", callback_data="menu_tienda"),
     InlineKeyboardButton("➕ RECARGAR SALDO", callback_data="menu_recarga")],
    [InlineKeyboardButton("👤 MI PERFIL", callback_data="menu_perfil"),
     InlineKeyboardButton("🛠️ HERRAMIENTAS", callback_data="menu_buscar")],
    [InlineKeyboardButton("❓ AYUDA / FAQ", callback_data="faq")],
    [InlineKeyboardButton("⚙️ PANEL ADMINISTRADOR", callback_data="menu_admin")]
])

menu_perfil = InlineKeyboardMarkup([
    [InlineKeyboardButton("📦 MIS PEDIDOS", callback_data="menu_pedidos"),
     InlineKeyboardButton("📌 MIS FAVORITOS", callback_data="menu_favoritos")],
    [InlineKeyboardButton("🛒 CARRITO DE COMPRAS", callback_data="menu_carrito")],
    [InlineKeyboardButton("🎁 MIS REFERIDOS", callback_data="ref_menu"),
     InlineKeyboardButton("💱 CAMBIAR MONEDA", callback_data="conf_moneda")],
    [InlineKeyboardButton("🔙 VOLVER AL INICIO", callback_data="ad_salir")]
])

menu_admin = InlineKeyboardMarkup([
    [InlineKeyboardButton("👥 GESTIÓN DE USUARIOS", callback_data="ad_usuarios"),
     InlineKeyboardButton("📂 CATEGORÍAS Y SERVICIOS", callback_data="ad_categorias")],
    [InlineKeyboardButton("🔌 GESTIÓN DE PANELES", callback_data="ad_paneles"),
     InlineKeyboardButton("⚙️ CONFIGURACIÓN GENERAL", callback_data="ad_config")],
    [InlineKeyboardButton("📋 ACCIONES RÁPIDAS", callback_data="ad_acciones")],
    [InlineKeyboardButton("🔙 VOLVER AL INICIO", callback_data="ad_salir")]
])
log("✅ Botones listos para mostrarse", "EXITO")


# ==================================================
# 🛡️ FUNCIONES DE RESPALDO POR SI FALTAN ARCHIVOS
# ==================================================
async def funcion_vacia(*args, **kwargs):
    await args[0].edit_message_text("🔧 Función en construcción", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_salir")]]))

perfil_completo = funcion_vacia
mostrar_categorias = funcion_vacia
ver_pedidos = funcion_vacia
ver_favoritos = funcion_vacia
ver_carrito = funcion_vacia
iniciar_recarga = funcion_vacia
verificar_referido = lambda *args: None
asignar_codigo_referido = lambda *args: "REF000"
obtener_conv_pagos = lambda: ConversationHandler(...)
cambiar_moneda = funcion_vacia
ver_faq = funcion_vacia
obtener_estadisticas = lambda: {"usuarios":0, "activos":0, "ganancia_total":0, "mas_vendidos":[]}

# ==================================================
# 📂 CARGA DE MÓDULOS ORIGINALES (si existen reemplazan a las de respaldo)
# ==================================================
log("📂 Cargando archivos y módulos del sistema...", "PASO")
try:
    from config import Config
    from mongodb import (
        coleccion_usuarios, coleccion_categorias, coleccion_servicios,
        coleccion_facturas, coleccion_paneles, coleccion_configuracion,
        iniciar_configuracion
    )
    from modulos.pagos_facturas import obtener_conv_pagos, procesar_factura, iniciar_recarga
    from modulos.tienda_categorias import mostrar_categorias, mostrar_servicios
    from modulos.pedidos import ver_pedidos
    from modulos.herramientas import generar_dorks, validar_bin, generar_cc
    from modulos.admin_total import (
        dar_permisos, cambiar_rol, recargar_saldo_manual, banear_usuario,
        guardar_configuracion, sincronizar_servicios, crear_categoria,
        copiar_panel, alternar_mantenimiento, crear_respaldo,
        configurar_limite, ver_niveles
    )
    from api.gestor_paneles import agregar_panel_smm, ver_ids_paneles, editar_panel, eliminar_panel
    from api.importar_servicios import importar_desde_api
    from modulos.auditoria import ver_historial
    from modulos.niveles_limites import calcular_nivel_usuario, verificar_limite_gasto
    from modulos.alertas import revisar_estado_paneles
    from modulos.tienda_avanzada import buscar_servicios, ver_favoritos, ver_carrito
    from modulos.referidos import asignar_codigo_referido, verificar_referido
    from modulos.preferencias_usuario import cambiar_moneda, revisar_saldo_bajo
    from modulos.soporte_faq import ver_faq, perfil_completo
    from modulos.diagnostico import diagnosticar_panel, probar_servicio
    from modulos.estadisticas_avanzadas import obtener_estadisticas
    log("✅ Todos los módulos cargados sin errores", "EXITO")
except Exception as e:
    log(f"⚠️ ALGUNOS ARCHIVOS FALTAN: {str(e)} | Se usarán versiones de respaldo", "ADVERTENCIA")
    try:
        from config import Config
        from mongodb import coleccion_usuarios, iniciar_configuracion
    except:
        log("❌ Error crítico: falta config.py o mongodb.py", "ERROR")
        sys.exit(1)


# ==================================================
# 🌐 SERVIDOR WEB PARA MANTENERLO ACTIVO
# ==================================================
log("🌐 Preparando servidor web...", "PASO")
try:
    PUERTO = int(os.getenv("PORT", 8080))
    servidor = Flask(__name__)

    @servidor.route('/')
    def estado():
        log("📥 Alguien accedió a la página principal", "DETALLE")
        return "✅ VOLTIXPRO V4 | ACTIVO Y ESCUCHANDO MENSAJES"

    def iniciar_servidor_web():
        try:
            log(f"🌐 Iniciando servidor en el puerto {PUERTO}...", "PASO")
            servidor.run(host="0.0.0.0", port=PUERTO, use_reloader=False)
        except Exception as e:
            log(f"❌ ERROR EN SERVIDOR WEB: {str(e)}", "ERROR")
    log("✅ Servidor web configurado", "EXITO")
except Exception as e:
    log(f"❌ ERROR PREPARANDO FLASK: {str(e)}", "ERROR")
    log(f"🔍 Traza completa:\n{traceback.format_exc()}", "ERROR")
    sys.exit(1)


# ==================================================
# 🤖 COMANDO /START CON BOTONES GARANTIZADOS
# ==================================================
async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_user.id
    log(f"📩 COMANDO /START RECIBIDO DE USUARIO: {usuario_id}", "INFO")
    try:
        args = context.args
        user = update.effective_user

        if args:
            codigo = args[0].upper()
            log(f"🔗 Tiene código de referido: {codigo}", "DETALLE")
            await verificar_referido(user.id, codigo)

        usuario = coleccion_usuarios.find_one({"user_id": user.id})
        if not usuario:
            log("👤 Usuario nuevo, creando registro...", "DETALLE")
            codigo_ref = await asignar_codigo_referido(user.id)
            coleccion_usuarios.insert_one({
                "user_id": user.id,
                "nombre": user.full_name or user.first_name,
                "saldo": 0.0,
                "rol": "usuario",
                "nivel": "bronce",
                "gasto_total": 0.0,
                "gasto_hoy": 0.0,
                "ultimo_gasto_dia": None,
                "codigo_referido": codigo_ref,
                "referido_por": args[0].upper() if args else None,
                "saldo_referidos": 0.0,
                "moneda": "USD",
                "modo_interfaz": "completo",
                "favoritos": [],
                "carrito": [],
                "ultimo_aviso_saldo_bajo": None,
                "baneado": False,
                "creado_en": datetime.now()
            })
        
        esta_suscrito = await verificar_suscripcion(user.id, context.bot)
        if not esta_suscrito:
            log("🔔 No está en el canal requerido, mostrando aviso", "DETALLE")
            await update.message.reply_text(
                f"🔔 Antes de empezar debes unirte al canal oficial:\n{CANAL_OBLIGATORIO}",
                reply_markup=menu_suscripcion
            )
            return
        
        mensaje_bienvenida = """⚡ VOLTIXPRO V4
¡Bienvenido! Tu tienda de servicios confiable y rápida.

📋 Reglas básicas:
1. Revisa bien tu enlace antes de pagar.
2. No hacemos reembolsos por errores tuyos.

⚡ VOLTIXPRO – Todos los derechos reservados"""

        await update.message.reply_text(
            mensaje_bienvenida,
            reply_markup=menu_principal
        )
        log(f"✅ Bienvenida + BOTONES enviados correctamente a {usuario_id}", "EXITO")

    except Exception as e:
        log(f"❌ ERROR EN /start: {str(e)}", "ERROR")
        log(f"🔍 Traza:\n{traceback.format_exc()}", "ERROR")
        await update.message.reply_text("❌ Ocurrió un error al procesar tu solicitud")


# ==================================================
# 🤖 MANEJO DE TODOS LOS BOTONES
# ==================================================
async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dato = query.data.strip()
    usuario_id = update.effective_user.id
    log(f"🔘 BOTÓN PULSADO: {dato} | USUARIO: {usuario_id}", "INFO")

    await query.answer()

    if dato == "verificar_suscripcion":
        ok = await verificar_suscripcion(usuario_id, context.bot)
        if ok:
            await query.edit_message_text(
                """⚡ VOLTIXPRO V4
¡Bienvenido! Tu tienda de servicios confiable y rápida.

📋 Reglas básicas:
1. Revisa bien tu enlace antes de pagar.
2. No hacemos reembolsos por errores tuyos.

⚡ VOLTIXPRO – Todos los derechos reservados""",
                reply_markup=menu_principal
            )
            log(f"✅ Verificado correctamente, mostrando menú principal", "EXITO")
        else:
            await query.answer("❌ Aún no te unes al canal", show_alert=True)
        return

    if dato == "ad_salir":
        await query.edit_message_text(
            """⚡ VOLTIXPRO V4
¡Bienvenido! Tu tienda de servicios confiable y rápida.

📋 Reglas básicas:
1. Revisa bien tu enlace antes de pagar.
2. No hacemos reembolsos por errores tuyos.

⚡ VOLTIXPRO – Todos los derechos reservados""",
            reply_markup=menu_principal
        )
        return

    elif dato == "menu_tienda": await mostrar_categorias(update, context)
    elif dato == "menu_buscar": await query.edit_message_text("🔎 Escribe lo que buscas:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_salir")]]))
    elif dato == "menu_perfil": 
        texto = await perfil_completo(update, context)
        await query.edit_message_text(str(texto), reply_markup=menu_perfil)
    elif dato == "menu_pedidos": await ver_pedidos(update, context)
    elif dato == "menu_favoritos": await ver_favoritos(update, context)
    elif dato == "menu_carrito": await ver_carrito(update, context)
    elif dato == "ref_menu": await query.edit_message_text("🎁 Tus referidos", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_perfil")]]))
    elif dato == "conf_moneda": await cambiar_moneda(update, context)
    elif dato == "faq": await ver_faq(update, context)
    elif dato == "menu_recarga": await iniciar_recarga(update, context)
    elif dato == "menu_admin":
        if str(usuario_id) != str(Config.ADMIN_ID):
            await query.answer("❌ Sin permiso", show_alert=True)
            return
        await query.edit_message_text("⚙️ PANEL DE ADMINISTRACIÓN", reply_markup=menu_admin)

    log(f"✅ Acción {dato} procesada", "EXITO")


# ==================================================
# 🚀 ARRANQUE FINAL Y CONEXIÓN
# ==================================================
async def ejecutar_bot():
    log("🔗 Conectando base de datos...", "PASO")
    try:
        await iniciar_configuracion()
        log("✅ Base de datos lista", "EXITO")
    except Exception as e:
        log(f"❌ BASE DE DATOS: {str(e)}", "ERROR")
        return

    log("🤖 Conectando con Telegram...", "PASO")
    bot_app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # ✅ TODOS LOS COMANDOS REGISTRADOS
    bot_app.add_handler(CommandHandler("start", inicio))
    bot_app.add_handler(CommandHandler("cambiar", cambiar_ajuste if 'cambiar_ajuste' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("permisos", dar_permisos if 'dar_permisos' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("rol", cambiar_rol if 'cambiar_rol' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("addsaldo", recargar_saldo_manual if 'recargar_saldo_manual' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("ban", banear_usuario if 'banear_usuario' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("crearcategoria", crear_categoria if 'crear_categoria' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("agregarpanel", agregar_panel_smm if 'agregar_panel_smm' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("editarpanel", editar_panel if 'editar_panel' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("eliminarpanel", eliminar_panel if 'eliminar_panel' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("copiarpanel", copiar_panel if 'copiar_panel' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("actualizar", sincronizar_servicios if 'sincronizar_servicios' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("limite", configurar_limite if 'configurar_limite' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("niveles", ver_niveles if 'ver_niveles' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("respaldo", crear_respaldo if 'crear_respaldo' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("buscar", buscar_servicios if 'buscar_servicios' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("usarreferido", verificar_referido))
    bot_app.add_handler(CommandHandler("moneda", cambiar_moneda))
    bot_app.add_handler(CommandHandler("faq", ver_faq))
    bot_app.add_handler(CommandHandler("recargar", iniciar_recarga))
    bot_app.add_handler(CommandHandler("estadisticas", obtener_estadisticas))
    bot_app.add_handler(CommandHandler("dorks", generar_dorks if 'generar_dorks' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("bin", validar_bin if 'validar_bin' in locals() else funcion_vacia))
    bot_app.add_handler(CommandHandler("cc", generar_cc if 'generar_cc' in locals() else funcion_vacia))

    if 'obtener_conv_pagos' in locals():
        bot_app.add_handler(obtener_conv_pagos())

    bot_app.add_handler(CallbackQueryHandler(manejar_botones))
    bot_app.add_handler(MessageHandler(filters.PHOTO, subir_foto_bienvenida if 'subir_foto_bienvenida' in locals() else funcion_vacia))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, funcion_vacia))

    await bot_app.bot.delete_webhook(drop_pending_updates=True)
    log("🔌 Webhooks antiguos eliminados", "EXITO")

    log("="*70, "EXITO")
    log("🎉 🚀 BOT 100% CARGADO Y LISTO", "EXITO")
    log("="*70, "EXITO")

    await bot_app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        Thread(target=iniciar_servidor_web, daemon=True).start()
        log("🌐 Servidor web activo", "EXITO")
        asyncio.run(ejecutar_bot())
    except Exception as e:
        log(f"❌ ERROR GENERAL: {str(e)}", "ERROR")
        log(f"🔍 Traza:\n{traceback.format_exc()}", "ERROR")
