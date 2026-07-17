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

# Formato que verás en pantalla y archivo
formato_registro = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(mensaje)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

# Configurar que muestre todo
logger = logging.getLogger("VoltixPro")
logger.setLevel(logging.DEBUG)

# Mostrar en la terminal
consola = logging.StreamHandler(sys.stdout)
consola.setFormatter(formato_registro)
logger.addHandler(consola)

# Guardar también en archivo por si necesitas revisarlo
archivo = logging.FileHandler(RUTA_LOG, encoding="utf-8")
archivo.setFormatter(formato_registro)
logger.addHandler(archivo)

# Función corta para escribir registros
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

# Solución definitiva al error de bucle
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
    from telegram import Update
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
# 📂 CARGA DE TUS ARCHIVOS DEL SISTEMA
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
        menu_principal, menu_suscripcion, menu_admin, menu_usuarios,
        menu_categorias, menu_panel, menu_config, menu_acciones, menu_perfil
    )
    from modulos.acceso import verificar_suscripcion
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
    from modulos.soporte_faq import ver_faq
    from modulos.diagnostico import diagnosticar_panel, probar_servicio
    from modulos.estadisticas_avanzadas import obtener_estadisticas
    from modulos.personalizacion import cambiar_ajuste, bienvenida_personalizada, subir_foto_bienvenida, obtener_ajuste
    from datetime import datetime
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
# 🤖 FUNCIONES DEL BOT CON REGISTRO
# ==================================================
log("🤖 Definiendo funciones del bot...", "PASO")
esperando_respuesta = {}

async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_user.id
    log(f"📩 COMANDO /start RECIBIDO DE USUARIO: {usuario_id}", "INFO")
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
                "referido_por": None,
                "saldo_referidos": 0.0,
                "moneda": "USD",
                "modo_interfaz": "completo",
                "favoritos": [],
                "carrito": [],
                "ultimo_aviso_saldo_bajo": None,
                "baneado": False,
                "creado_en": datetime.now()
            })
        
        if not await verificar_suscripcion(update, context):
            canal = await obtener_ajuste("canal_obligatorio", "@Voltix_Pro")
            log("🔔 No está en el canal requerido, pidiendo unión", "DETALLE")
            await update.message.reply_text(
                f"🔔 Antes de empezar debes unirte al canal oficial:\n{canal}",
                reply_markup=menu_suscripcion
            )
            return
        
        await bienvenida_personalizada(update, context)
        log(f"✅ Bienvenida enviada correctamente a {usuario_id}", "EXITO")

    except Exception as e:
        log(f"❌ ERROR EN /start: {str(e)}", "ERROR")
        log(f"🔍 Traza:\n{traceback.format_exc()}", "ERROR")
        await update.message.reply_text("❌ Ocurrió un error al procesar tu solicitud")


async def recibir_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip()
    log(f"✏️ Datos de configuración de {user_id}: {texto}", "DETALLE")
    if user_id not in esperando_respuesta:
        log("⚠️ No se esperaba respuesta de este usuario", "ADVERTENCIA")
        return
    accion = esperando_respuesta.pop(user_id)
    resultado = await guardar_configuracion(accion, texto)
    await update.message.reply_text(resultado)
    log(f"✅ Configuración aplicada para {user_id}", "EXITO")


async def ver_estadisticas_generales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log(f"📊 Solicitando estadísticas por: {update.effective_user.id}", "INFO")
    if update.effective_user.id != Config.ADMIN_ID:
        log("🚫 Intento de acceso sin permiso a estadísticas", "ADVERTENCIA")
        return await update.callback_query.answer("❌ Sin permiso", show_alert=True)
    try:
        est = await obtener_estadisticas()
        texto = f"""📊 **ESTADÍSTICAS GENERALES**

👥 Usuarios totales: {est['usuarios']}
✅ Activos: {est['activos']}
💵 Ganancia total: ${est['ganancia_total']}

🏆 Más vendidos:
"""
        for item in est['mas_vendidos']:
            texto += f"• {item['_id']}: {item['cantidad']} ventas\n"
        await update.callback_query.edit_message_text(texto, parse_mode="Markdown", reply_markup=menu_acciones)
        log("✅ Estadísticas mostradas correctamente", "EXITO")
    except Exception as e:
        log(f"❌ ERROR CARGANDO ESTADÍSTICAS: {str(e)}", "ERROR")


async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dato = query.data.strip()
    log(f"🔘 BOTÓN PULSADO: {dato} | USUARIO: {update.effective_user.id}", "INFO")

    try:
        if dato == "verificar_suscripcion":
            if await verificar_suscripcion(update, context):
                await bienvenida_personalizada(update, context)
            else:
                await query.answer("❌ Aún no te unes al canal", show_alert=True)
        elif dato == "menu_tienda": await mostrar_categorias(update, context)
        elif dato == "menu_buscar": await query.edit_message_text("🔎 Escribe: /buscar seguidores instagram")
        elif dato == "menu_favoritos": await ver_favoritos(update, context)
        elif dato == "menu_carrito": await ver_carrito(update, context)
        elif dato == "menu_recarga": await iniciar_recarga(update, context)
        elif dato == "menu_perfil":
            from modulos.soporte_faq import perfil_completo
            await perfil_completo(update, context)
        elif dato == "menu_pedidos": await ver_pedidos(update, context)
        elif dato == "menu_admin":
            if update.effective_user.id == Config.ADMIN_ID:
                await query.edit_message_text("⚙️ PANEL DE ADMINISTRACIÓN", reply_markup=menu_admin)
            else:
                await query.answer("❌ Solo el administrador", show_alert=True)
        elif dato == "ad_salir": await bienvenida_personalizada(update, context)
        elif dato == "ad_usuarios": await query.edit_message_text("👥 GESTIÓN DE USUARIOS", reply_markup=menu_usuarios)
        elif dato == "ad_categorias": await query.edit_message_text("📂 GESTIÓN DE CATEGORÍAS", reply_markup=menu_categorias)
        elif dato == "ad_paneles": await query.edit_message_text("🔌 GESTIÓN DE PANELES", reply_markup=menu_panel)
        elif dato == "ad_config": await query.edit_message_text("⚙️ CONFIGURACIÓN GENERAL", reply_markup=menu_config)
        elif dato == "ad_acciones": await query.edit_message_text("📋 ACCIONES RÁPIDAS", reply_markup=menu_acciones)
        elif dato == "pan_agregar": await query.edit_message_text("📝 Escribe: /agregarpanel NOMBRE | URL | CLAVE | PORCENTAJE")
        elif dato == "pan_ver_ids": await ver_ids_paneles(update, context)
        elif dato == "pan_copiar": await query.edit_message_text("📋 Escribe: /copiarpanel ID_ORIGEN ID_DESTINO")
        elif dato == "pan_editar": await query.edit_message_text("✏️ Escribe: /editarpanel ID CAMPO NUEVO_VALOR")
        elif dato == "pan_eliminar": await query.edit_message_text("🗑️ Escribe: /eliminarpanel ID_DEL_PANEL")
        elif dato == "acc_aviso":
            esperando_respuesta[update.effective_user.id] = "mensaje_aviso"
            await query.edit_message_text("📢 Escribe el mensaje que recibirán todos:")
        elif dato == "acc_historial": await ver_historial(update, context)
        elif dato == "acc_respaldo": await crear_respaldo(update, context)
        elif dato == "acc_mantenimiento": await alternar_mantenimiento(update, context)
        elif dato == "acc_stats": await ver_estadisticas_generales(update, context)
        elif dato == "acc_reiniciar": await sincronizar_servicios(update, context)
        elif dato == "conf_niveles": await ver_niveles(update, context)
        elif dato == "conf_limite":
            esperando_respuesta[update.effective_user.id] = "limite_diario"
            await query.edit_message_text("🚧 Escribe el monto límite por día:")
        elif dato == "conf_referido":
            esperando_respuesta[update.effective_user.id] = "recompensa_referido"
            await query.edit_message_text("🎁 Escribe cuánto ganan por cada referido:")
        elif dato == "conf_saldobajo":
            esperando_respuesta[update.effective_user.id] = "aviso_saldo_minimo"
            await query.edit_message_text("🔔 Avisar cuando el saldo baje de:")
        elif dato == "conf_marca":
            await query.edit_message_text("""🎨 PERSONALIZAR TU MARCA

Comandos disponibles:
/cambiar nombre_bot Tu Nombre
/cambiar emoji ⚡
/cambiar mensaje_bienvenida Hola...
/cambiar pie_pagina © 2026 Tu Marca
/cambiar reglas 1. Regla uno...

Simplemente envía una foto para ponerla de portada.""")
        elif dato == "carrito_vaciar":
            coleccion_usuarios.update_one({"user_id": update.effective_user.id}, {"$set": {"carrito": []}})
            await query.answer("✅ Carrito vaciado", show_alert=True)
            await ver_carrito(update, context)
        elif dato.startswith("ver_cat_"):
            nombre_cat = dato.split("_", 2)[2]
            await mostrar_servicios(update, context, nombre_cat)

        log(f"✅ Acción {dato} procesada sin errores", "EXITO")

    except Exception as e:
        log(f"❌ ERROR AL PROCESAR BOTÓN {dato}: {str(e)}", "ERROR")
        log(f"🔍 Traza:\n{traceback.format_exc()}", "ERROR")


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

    # REGISTRO DE TODOS LOS COMANDOS
    bot_app.add_handler(CommandHandler("start", inicio))
    bot_app.add_handler(CommandHandler("cambiar", cambiar_ajuste))
    bot_app.add_handler(CommandHandler("bienvenida", bienvenida_personalizada))
    bot_app.add_handler(CommandHandler("permisos", dar_permisos))
    bot_app.add_handler(CommandHandler("rol", cambiar_rol))
    bot_app.add_handler(CommandHandler("addsaldo", recargar_saldo_manual))
    bot_app.add_handler(CommandHandler("ban", banear_usuario))
    bot_app.add_handler(CommandHandler("unban", banear_usuario))
    bot_app.add_handler(CommandHandler("crearcategoria", crear_categoria))
    bot_app.add_handler(CommandHandler("agregarpanel", agregar_panel_smm))
    bot_app.add_handler(CommandHandler("editarpanel", editar_panel))
    bot_app.add_handler(CommandHandler("eliminarpanel", eliminar_panel))
    bot_app.add_handler(CommandHandler("copiarpanel", copiar_panel))
    bot_app.add_handler(CommandHandler("actualizar", sincronizar_servicios))
    bot_app.add_handler(CommandHandler("limite", configurar_limite))
    bot_app.add_handler(CommandHandler("niveles", ver_niveles))
    bot_app.add_handler(CommandHandler("respaldo", crear_respaldo))
    bot_app.add_handler(CommandHandler("buscar", buscar_servicios))
    bot_app.add_handler(CommandHandler("usarreferido", verificar_referido))
    bot_app.add_handler(CommandHandler("moneda", cambiar_moneda))
    bot_app.add_handler(CommandHandler("faq", ver_faq))
    bot_app.add_handler(CommandHandler("recargar", iniciar_recarga))
    bot_app.add_handler(CommandHandler("diagnosticar", diagnosticar_panel))
    bot_app.add_handler(CommandHandler("probar", probar_servicio))
    bot_app.add_handler(CommandHandler("estadisticas", ver_estadisticas_generales))
    bot_app.add_handler(CommandHandler("dorks", generar_dorks))
    bot_app.add_handler(CommandHandler("bin", validar_bin))
    bot_app.add_handler(CommandHandler("cc", generar_cc))

    bot_app.add_handler(obtener_conv_pagos())
    bot_app.add_handler(MessageHandler(filters.PHOTO, subir_foto_bienvenida))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_configuracion))
    bot_app.add_handler(CallbackQueryHandler(manejar_botones))

    await bot_app.bot.delete_webhook(drop_pending_updates=True)
    log("🔌 Cualquier webhook antiguo eliminado", "EXITO")

    async def revisar():
        while True:
            await asyncio.sleep(1800)
            log("⏳ Ejecutando revisión programada de paneles...", "DETALLE")
            await revisar_estado_paneles(bot_app)
            log("✅ Revisión finalizada", "DETALLE")
    asyncio.create_task(revisar())

    log("="*70, "EXITO")
    log("🎉 🚀 BOT TOTALMENTE CONECTADO Y ESCUCHANDO MENSAJES", "EXITO")
    log("="*70, "EXITO")

    await bot_app.run_polling(drop_pending_updates=True, close_loop=False)

def arrancar_bot():
    try:
        asyncio.run(ejecutar_bot())
    except Exception as e:
        log(f"❌ ERROR GENERAL DEL BOT: {str(e)}", "ERROR")
        log(f"🔍 Traza completa:\n{traceback.format_exc()}", "ERROR")

if __name__ == "__main__":
    try:
        # Servidor en su propio hilo
        Thread(target=iniciar_servidor_web, daemon=True).start()
        # Bot en su propio hilo sin conflictos
        Thread(target=arrancar_bot, daemon=True).start()
        # Mantener el programa activo indefinidamente
        while True:
            time.sleep(3600)
    except Exception as e:
        log(f"❌ ERROR EN EL ARRANQUE GENERAL: {str(e)}", "ERROR")
        log(f"🔍 Traza completa:\n{traceback.format_exc()}", "ERROR")
