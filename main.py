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
        CallbackQueryHandler, MessageHandler, filters
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
# 📂 CARGA DE MÓDULOS Y BOTONES
# ==================================================
log("📂 Cargando archivos y módulos del sistema...", "PASO")
try:
    from config import Config
    from mongodb import (
        coleccion_usuarios, coleccion_categorias, coleccion_servicios,
        coleccion_facturas, coleccion_paneles, coleccion_configuracion,
        iniciar_configuracion
    )
    from interfaces.botones import (
        menu_suscripcion, menu_principal, menu_perfil, menu_admin,
        menu_panel, menu_acciones, menu_config, menu_usuarios,
        menu_categorias, botones_carrito, botones_factura
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
    from modulos.estadisticas import obtener_estadisticas
    from modulos.personalizacion import cambiar_ajuste, bienvenida_personalizada, subir_foto_bienvenida, obtener_ajuste
    log("✅ Todos los módulos cargados sin errores", "EXITO")
except Exception as e:
    log(f"❌ ERROR CARGANDO ARCHIVOS: {str(e)}", "ERROR")
    log(f"🔍 Revisa que existan y no tengan errores internos", "ADVERTENCIA")
    log(f"🔍 Traza completa:\n{traceback.format_exc()}", "ERROR")
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
# 🤖 COMANDO /START
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
        
        # ✅ VERIFICACIÓN DE SUSCRIPCIÓN
        esta_suscrito = await verificar_suscripcion(user.id, context.bot)
        if not esta_suscrito:
            log("🔔 No está en el canal requerido, mostrando aviso", "DETALLE")
            await update.message.reply_text(
                f"🔔 Antes de empezar debes unirte al canal oficial:\n{CANAL_OBLIGATORIO}",
                reply_markup=menu_suscripcion
            )
            return
        
        # ✅ MENÚ PRINCIPAL CON EL DISEÑO QUE PEDISTE
        await update.message.reply_text(
            """⚡ VOLTIXPRO V4
¡Bienvenido! Tu tienda de servicios confiable y rápida.

📋 Reglas básicas:
1. Revisa bien tu enlace antes de pagar.
2. No hacemos reembolsos por errores tuyos.

⚡ VOLTIXPRO – Todos los derechos reservados""",
            reply_markup=menu_principal
        )
        log(f"✅ Bienvenida enviada correctamente a {usuario_id}", "EXITO")

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

    # ✅ Verificación de suscripción al pulsar el botón
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

    # ✅ Volver al menú principal
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

    # 🛍️ TIENDA Y SERVICIOS
    elif dato == "menu_tienda":
        await mostrar_categorias(update, context)
    elif dato == "menu_buscar":
        await query.edit_message_text("🔎 Escribe lo que quieres buscar:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_salir")]]))
    
    # 👤 PERFIL Y LO QUE TIENE DENTRO
    elif dato == "menu_perfil":
        await perfil_completo(update, context)
    elif dato == "menu_pedidos":
        await ver_pedidos(update, context)
    elif dato == "menu_favoritos":
        await ver_favoritos(update, context)
    elif dato == "menu_carrito":
        await ver_carrito(update, context)
    elif dato == "ref_menu":
        await query.edit_message_text("🎁 Aquí verás tus referidos y ganancias", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_perfil")]]))
    elif dato == "conf_moneda":
        await cambiar_moneda(update, context)
    elif dato == "faq":
        await ver_faq(update, context)

    # 💰 RECARGAR SALDO
    elif dato == "menu_recarga":
        await iniciar_recarga(update, context)

    # ⚙️ SOLO ADMINISTRADOR
    elif dato == "menu_admin":
        if str(usuario_id) != str(Config.ADMIN_ID):
            await query.answer("❌ No tienes permiso para esto", show_alert=True)
            return
        await query.edit_message_text("⚙️ PANEL DE ADMINISTRACIÓN", reply_markup=menu_admin)
    elif dato == "ad_usuarios":
        await query.edit_message_text("👥 GESTIÓN DE USUARIOS", reply_markup=menu_usuarios)
    elif dato == "ad_categorias":
        await query.edit_message_text("📂 GESTIÓN DE CATEGORÍAS", reply_markup=menu_categorias)
    elif dato == "ad_paneles":
        await query.edit_message_text("🔌 GESTIÓN DE PANELES", reply_markup=menu_panel)
    elif dato == "ad_config":
        await query.edit_message_text("⚙️ CONFIGURACIÓN GENERAL", reply_markup=menu_config)
    elif dato == "ad_acciones":
        await query.edit_message_text("📋 ACCIONES RÁPIDAS", reply_markup=menu_acciones)

    # 📦 RESTO DE ACCIONES
    elif dato == "pan_agregar":
        await query.edit_message_text("➕ Escribe los datos del nuevo panel", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]]))
    elif dato == "pan_ver_ids":
        await ver_ids_paneles(update, context)
    elif dato == "pan_copiar":
        await copiar_panel(update, context)
    elif dato == "pan_editar":
        await editar_panel(update, context)
    elif dato == "pan_eliminar":
        await eliminar_panel(update, context)
    elif dato == "acc_aviso":
        await query.edit_message_text("📢 Escribe el aviso que quieres enviar a todos", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_acciones")]]))
    elif dato == "acc_historial":
        await ver_historial(update, context)
    elif dato == "acc_respaldo":
        await crear_respaldo(update, context)
    elif dato == "acc_mantenimiento":
        await alternar_mantenimiento(update, context)
    elif dato == "acc_stats":
        await ver_estadisticas_generales(update, context)
    elif dato == "acc_reiniciar":
        await sincronizar_servicios(update, context)
    elif dato == "conf_niveles":
        await ver_niveles(update, context)
    elif dato == "conf_limite":
        await configurar_limite(update, context)
    elif dato == "conf_referido":
        await query.edit_message_text("🎁 Configura la recompensa por referidos", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_config")]]))
    elif dato == "conf_saldobajo":
        await query.edit_message_text("🔔 Configura el aviso de saldo bajo", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_config")]]))
    elif dato == "conf_marca":
        await query.edit_message_text("🎨 Personaliza tu marca y mensajes", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_config")]]))
    elif dato == "usr_buscar":
        await query.edit_message_text("🔍 Escribe el ID o nombre del usuario", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))
    elif dato == "usr_sumar":
        await query.edit_message_text("➕ Escribe ID del usuario y monto a agregar", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))
    elif dato == "usr_quitar":
        await query.edit_message_text("🗑️ Escribe ID del usuario y monto a quitar", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))
    elif dato == "usr_bloquear":
        await query.edit_message_text("🚫 Escribe ID del usuario para bloquear/desbloquear", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))
    elif dato == "cat_crear":
        await query.edit_message_text("➕ Escribe el nombre de la nueva categoría", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_categorias")]]))
    elif dato == "cat_editar":
        await query.edit_message_text("✏️ Escribe nombre de categoría y nuevo contenido", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_categorias")]]))
    elif dato == "cat_eliminar":
        await query.edit_message_text("🗑️ Escribe el nombre de la categoría a eliminar", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_categorias")]]))
    elif dato == "carrito_pagar":
        await procesar_factura(update, context)
    elif dato == "carrito_vaciar":
        coleccion_usuarios.update_one({"user_id": usuario_id}, {"$set": {"carrito": []}})
        await query.answer("✅ Carrito vaciado", show_alert=True)
        await ver_carrito(update, context)
    elif dato == "pagado_confirmar":
        await query.edit_message_text("✅ Gracias, revisaremos tu pago pronto", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver al inicio", callback_data="ad_salir")]]))
    elif dato == "pagado_cancelar":
        await query.edit_message_text("❌ Pago cancelado", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver al inicio", callback_data="ad_salir")]]))

    log(f"✅ Acción {dato} procesada sin errores", "EXITO")


# ==================================================
# 🚀 ARRANQUE FINAL Y CONEXIÓN
# ==================================================
async def ejecutar_bot():
    log("🔗 Conectando y preparando base de datos...", "PASO")
    try:
        await iniciar_configuracion()
        log("✅ Base de datos conectada correctamente", "EXITO")
    except Exception as e:
        log(f"❌ ERROR DE BASE DE DATOS: {str(e)}", "ERROR")
        log(f"🔍 Traza:\n{traceback.format_exc()}", "ERROR")
        return

    log("🤖 Conectando con los servidores de Telegram...", "PASO")
    bot_app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # REGISTRO DE MANEJADORES
    bot_app.add_handler(CommandHandler("start", inicio))
    bot_app.add_handler(CallbackQueryHandler(manejar_botones))

    await bot_app.bot.delete_webhook(drop_pending_updates=True)
    log("🔌 Cualquier webhook antiguo eliminado", "EXITO")

    log("="*70, "EXITO")
    log("🎉 🚀 BOT TOTALMENTE CONECTADO Y ESCUCHANDO MENSAJES", "EXITO")
    log("="*70, "EXITO")

    await bot_app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        # ✅ Servidor web en segundo plano
        Thread(target=iniciar_servidor_web, daemon=True).start()
        log("🌐 Servidor web iniciado correctamente", "EXITO")

        # ✅ Bot en el hilo principal
        log("🤖 Iniciando conexión con Telegram...", "PASO")
        asyncio.run(ejecutar_bot())

    except Exception as e:
        log(f"❌ ERROR EN EL ARRANQUE GENERAL: {str(e)}", "ERROR")
        log(f"🔍 Traza completa:\n{traceback.format_exc()}", "ERROR")
