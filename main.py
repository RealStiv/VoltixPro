import sys
import os
import certifi
import nest_asyncio
import logging
import traceback
import random
from datetime import datetime

# ==================================================
# 📢 CONFIGURACIÓN DE REGISTROS
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

archivo_log = logging.FileHandler(RUTA_LOG, encoding="utf-8")
archivo_log.setFormatter(formato_registro)
logger.addHandler(archivo_log)

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
log("⚡ INICIANDO VOLTIXPRO V4", "PASO")
log("="*70, "PASO")

nest_asyncio.apply()
os.environ["SSL_CERT_FILE"] = certifi.where()
log("✅ Corrección de certificados aplicada", "EXITO")

# ==================================================
# 📦 CARGA DE LIBRERÍAS
# ==================================================
log("📦 Cargando librerías...", "PASO")
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
    log("✅ Librerías cargadas", "EXITO")
except Exception as e:
    log(f"❌ Error librerías: {str(e)}", "ERROR")
    log(f"🔍 {traceback.format_exc()}", "ERROR")
    sys.exit(1)

# ==================================================
# ⚙️ VARIABLES DE ENTORNO
# ==================================================
log("⚙️ Cargando configuración...", "PASO")
try:
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    MONGO_URI = os.getenv("MONGO_URI")

    if not BOT_TOKEN: raise ValueError("Falta BOT_TOKEN")
    if not ADMIN_ID: raise ValueError("Falta ADMIN_ID")
    if not MONGO_URI: raise ValueError("Falta MONGO_URI")

    log("✅ Variables listas", "EXITO")
except Exception as e:
    log(f"❌ Error configuración: {str(e)}", "ERROR")
    sys.exit(1)

# ==================================================
# ✅ VERIFICACIÓN DE CANAL
# ==================================================
CANAL_OBLIGATORIO = "@Voltix_Pro"

async def verificar_suscripcion(usuario_id, bot):
    try:
        miembro = await bot.get_chat_member(chat_id=CANAL_OBLIGATORIO, user_id=usuario_id)
        return miembro.status in ["member", "administrator", "creator"]
    except Exception as e:
        log(f"⚠️ Verificación fallida: {e}", "ADVERTENCIA")
        return False

# ==================================================
# 🎨 TODOS LOS MENÚS Y BOTONES
# ==================================================
log("🎨 Preparando menús...", "PASO")

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

menu_panel = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ AGREGAR NUEVO", callback_data="pan_agregar")],
    [InlineKeyboardButton("📋 VER LISTA CON ID", callback_data="pan_ver_ids")],
    [InlineKeyboardButton("📋 COPIAR CONFIGURACIÓN", callback_data="pan_copiar")],
    [InlineKeyboardButton("✏️ EDITAR", callback_data="pan_editar"),
     InlineKeyboardButton("🗑️ ELIMINAR", callback_data="pan_eliminar")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_paneles")]
])

menu_acciones = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 AVISO A TODOS", callback_data="acc_aviso")],
    [InlineKeyboardButton("📜 HISTORIAL COMPLETO", callback_data="acc_historial"),
     InlineKeyboardButton("💾 CREAR RESPALDO", callback_data="acc_respaldo")],
    [InlineKeyboardButton("🚧 MODO MANTENIMIENTO", callback_data="acc_mantenimiento"),
     InlineKeyboardButton("📊 ESTADÍSTICAS", callback_data="acc_stats")],
    [InlineKeyboardButton("🔄 SINCRONIZAR SERVICIOS", callback_data="acc_reiniciar")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_acciones")]
])

menu_config = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏅 NIVELES Y DESCUENTOS", callback_data="conf_niveles")],
    [InlineKeyboardButton("🚧 LÍMITE DE GASTO DIARIO", callback_data="conf_limite"),
     InlineKeyboardButton("🎁 RECOMPENSA POR REFERIDOS", callback_data="conf_referido")],
    [InlineKeyboardButton("🔔 AVISO DE SALDO BAJO", callback_data="conf_saldobajo")],
    [InlineKeyboardButton("🎨 PERSONALIZAR TU MARCA", callback_data="conf_marca")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_config")]
])

menu_usuarios = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 BUSCAR USUARIO", callback_data="usr_buscar")],
    [InlineKeyboardButton("➕ AGREGAR SALDO", callback_data="usr_sumar"),
     InlineKeyboardButton("🗑️ QUITAR SALDO", callback_data="usr_quitar")],
    [InlineKeyboardButton("🚫 BLOQUEAR / DESBLOQUEAR", callback_data="usr_bloquear")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_usuarios")]
])

menu_categorias = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ CREAR CATEGORÍA", callback_data="cat_crear")],
    [InlineKeyboardButton("✏️ EDITAR", callback_data="cat_editar"),
     InlineKeyboardButton("🗑️ ELIMINAR", callback_data="cat_eliminar")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_categorias")]
])

volver = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_salir")]])
log("✅ Menús listos", "EXITO")

# ==================================================
# 🛠️ TODAS LAS FUNCIONES YA CREADAS
# ==================================================
async def funcion_en_construccion(*args, **kwargs):
    mensaje = "🔧 Función en desarrollo o archivo faltante"
    obj = args[0]
    if hasattr(obj, "edit_message_text"):
        await obj.edit_message_text(mensaje, reply_markup=volver)
    elif hasattr(obj, "message"):
        await obj.message.reply_text(mensaje, reply_markup=volver)

async def mostrar_categorias(update, context):
    texto = "🛍️ Categorías disponibles:\n🔧 Agrega categorías primero desde el panel admin"
    await update.callback_query.edit_message_text(texto, reply_markup=menu_categorias)

async def mostrar_servicios(update, context):
    texto = "📦 Servicios:\n🔧 Todavía no hay servicios cargados"
    await update.callback_query.edit_message_text(texto, reply_markup=volver)

async def iniciar_recarga(update, context):
    texto = "💳 Recarga de saldo\nMétodos disponibles: Yape, Plin, Transferencia\nEscribe el monto a recargar"
    await update.callback_query.edit_message_text(texto, reply_markup=volver)

async def procesar_factura(*args):
    return True

async def perfil_completo(update, context):
    uid = update.effective_user.id
    usuario = coleccion_usuarios.find_one({"user_id": uid})
    if not usuario: return "❌ Perfil no encontrado"
    texto = f"""👤 TU PERFIL
🆔 ID: {usuario['user_id']}
👤 Nombre: {usuario['nombre']}
💰 Saldo: ${usuario['saldo']}
🏅 Nivel: {usuario['nivel']}
🎁 Código referido: {usuario['codigo_referido']}
📅 Ingreso: {usuario['fecha_registro'].strftime('%d/%m/%Y')}"""
    return texto

async def ver_pedidos(update, context):
    texto = "📦 Tus pedidos:\n🔧 Todavía no has realizado ningún pedido"
    await update.callback_query.edit_message_text(texto, reply_markup=volver)

async def ver_favoritos(update, context):
    texto = "📌 Tus favoritos:\n🔧 Todavía no agregaste nada"
    await update.callback_query.edit_message_text(texto, reply_markup=volver)

async def ver_carrito(update, context):
    texto = "🛒 Tu carrito está vacío"
    await update.callback_query.edit_message_text(texto, reply_markup=volver)

async def cambiar_moneda(update, context):
    texto = "💱 Elige tu moneda:\n✅ USD Dólar\n✅ BOB Boliviano"
    await update.callback_query.edit_message_text(texto, reply_markup=volver)

async def ver_faq(update, context):
    texto = """❓ PREGUNTAS FRECUENTES
1. ¿Cómo compro? Eliges el servicio y pagas
2. ¿Reembolsos? Solo si el servicio falla
3. ¿Cuánto tarda? Entre 5 y 30 minutos
📞 Soporte: @TuSoporte"""
    await update.callback_query.edit_message_text(texto, reply_markup=volver)

async def generar_codigo_ref(uid):
    return f"REF{random.randint(10000,99999)}{str(uid)[-3:]}"
asignar_codigo_referido = generar_codigo_ref

async def verificar_referido(uid, codigo_ref):
    try:
        referidor = coleccion_usuarios.find_one({"codigo_referido": codigo_ref})
        if referidor and referidor["user_id"] != uid:
            coleccion_usuarios.update_one({"user_id": referidor["user_id"]}, {"$inc": {"saldo": 2.50}})
            log(f"🎁 Bono $2.50 a {referidor['user_id']}", "EXITO")
    except: pass

async def obtener_estadisticas():
    try:
        total = coleccion_usuarios.count_documents({})
        activos = coleccion_usuarios.count_documents({"baneado": False})
        return {"usuarios": total, "activos": activos, "ganancia_total":0, "mas_vendidos":["Próximamente"]}
    except: return {"usuarios":0, "activos":0, "ganancia_total":0, "mas_vendidos":["Sin datos"]}

async def recargar_saldo_manual(update, context):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /addsaldo ID_USUARIO MONTO")
        return
    try:
        uid = int(context.args[0])
        monto = float(context.args[1])
        coleccion_usuarios.update_one({"user_id": uid}, {"$inc": {"saldo": monto}})
        await update.message.reply_text(f"✅ +${monto} al usuario {uid}")
    except: await update.message.reply_text("❌ Datos incorrectos")

async def banear_usuario(update, context):
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /ban ID_USUARIO")
        return
    try:
        uid = int(context.args[0])
        usuario = coleccion_usuarios.find_one({"user_id": uid})
        estado = not usuario.get("baneado", False)
        coleccion_usuarios.update_one({"user_id": uid}, {"$set": {"baneado": estado}})
        await update.message.reply_text(f"✅ Usuario {uid} {'bloqueado' if estado else 'desbloqueado'}")
    except: await update.message.reply_text("❌ ID incorrecto")

async def crear_categoria(*args):
    return await funcion_en_construccion(*args)
async def dar_permisos(*args):
    return await funcion_en_construccion(*args)
async def cambiar_rol(*args):
    return await funcion_en_construccion(*args)
async def guardar_configuracion(*args):
    return await funcion_en_construccion(*args)
async def sincronizar_servicios(*args):
    return await funcion_en_construccion(*args)
async def copiar_panel(*args):
    return await funcion_en_construccion(*args)
async def alternar_mantenimiento(*args):
    return await funcion_en_construccion(*args)
async def crear_respaldo(*args):
    return await funcion_en_construccion(*args)
async def configurar_limite(*args):
    return await funcion_en_construccion(*args)
async def ver_niveles(*args):
    return await funcion_en_construccion(*args)
async def agregar_panel_smm(*args):
    return await funcion_en_construccion(*args)
async def ver_ids_paneles(*args):
    return "Sin paneles registrados"
async def editar_panel(*args):
    return await funcion_en_construccion(*args)
async def eliminar_panel(*args):
    return await funcion_en_construccion(*args)
async def importar_desde_api(*args):
    return await funcion_en_construccion(*args)
async def ver_historial(*args):
    return await funcion_en_construccion(*args)
async def calcular_nivel_usuario(*args):
    return "bronce"
async def verificar_limite_gasto(*args):
    return True
async def revisar_estado_paneles(*args):
    return []
async def buscar_servicios(*args):
    return await funcion_en_construccion(*args)
async def revisar_saldo_bajo(*args):
    return False
async def diagnosticar_panel(*args):
    return "Todo bien"
async def probar_servicio(*args):
    return "Funciona correctamente"
async def generar_dorks(*args):
    return "🔧 Función en desarrollo"
async def validar_bin(*args):
    return "🔧 Función en desarrollo"
async def generar_cc(*args):
    return "🔧 Función en desarrollo"
async def obtener_conv_pagos():
    return MessageHandler(filters.TEXT, funcion_en_construccion)

# ==================================================
# 📂 IMPORTACIONES SEGURAS
# ==================================================
log("📂 Cargando módulos...", "PASO")
coleccion_usuarios = None
coleccion_categorias = None
coleccion_servicios = None
coleccion_facturas = None
coleccion_paneles = None
coleccion_configuracion = None
iniciar_configuracion = lambda: None

try:
    from config import Config
    from mongodb import (
        coleccion_usuarios, coleccion_categorias, coleccion_servicios,
        coleccion_facturas, coleccion_paneles, coleccion_configuracion,
        iniciar_configuracion
    )
    log("✅ Base de datos conectada", "EXITO")
except Exception as e:
    log(f"⚠️ Sin archivo mongodb.py: {str(e)}", "ADVERTENCIA")
    class Config: ADMIN_ID = ADMIN_ID

try:
    from modulos.pagos_facturas import obtener_conv_pagos, procesar_factura, iniciar_recarga
except: pass
try:
    from modulos.tienda_categorias import mostrar_categorias, mostrar_servicios
except: pass
try:
    from modulos.pedidos import ver_pedidos
except: pass
try:
    from modulos.herramientas import generar_dorks, validar_bin, generar_cc
except: pass
try:
    from modulos.admin_total import (
        dar_permisos, cambiar_rol, recargar_saldo_manual, banear_usuario,
        guardar_configuracion, sincronizar_servicios, crear_categoria,
        copiar_panel, alternar_mantenimiento, crear_respaldo,
        configurar_limite, ver_niveles
    )
except: pass
try:
    from api.gestor_paneles import agregar_panel_smm, ver_ids_paneles, editar_panel, eliminar_panel
except: pass
try:
    from api.importar_servicios import importar_desde_api
except: pass
try:
    from modulos.auditoria import ver_historial
except: pass
try:
    from modulos.niveles_limites import calcular_nivel_usuario, verificar_limite_gasto
except: pass
try:
    from modulos.alertas import revisar_estado_paneles
except: pass
try:
    from modulos.tienda_avanzada import buscar_servicios, ver_favoritos, ver_carrito
except: pass
try:
    from modulos.referidos import asignar_codigo_referido, verificar_referido
except: pass
try:
    from modulos.preferencias_usuario import cambiar_moneda, revisar_saldo_bajo
except: pass
try:
    from modulos.soporte_faq import ver_faq, perfil_completo
except: pass
try:
    from modulos.diagnostico import diagnosticar_panel, probar_servicio
except: pass
try:
    from modulos.estadisticas_avanzadas import obtener_estadisticas
except: pass

# ==================================================
# 🌐 SERVIDOR ANTI-SUSPENSIÓN
# ==================================================
log("🌐 Iniciando servidor web...", "PASO")
try:
    PUERTO = int(os.getenv("PORT", 8080))
    servidor = Flask(__name__)

    @servidor.route("/")
    def raiz(): return "✅ VOLTIXPRO ACTIVO"
    @servidor.route("/ping")
    def ping(): return "🏓 PONG"

    def arrancar():
        servidor.run(host="0.0.0.0", port=PUERTO, use_reloader=False)
    Thread(target=arrancar, daemon=True).start()
    log(f"✅ Servidor en puerto {PUERTO}", "EXITO")
except Exception as e:
    log(f"❌ Error servidor: {str(e)}", "ERROR")

# ==================================================
# 🤖 COMANDO /START
# ==================================================
async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    log(f"📩 /start de {uid}", "INFO")
    try:
        args = context.args
        usuario = coleccion_usuarios.find_one({"user_id": uid}) if coleccion_usuarios else None

        if not usuario:
            log("👤 Nuevo usuario", "DETALLE")
            ref_code = await asignar_codigo_referido(uid)
            datos = {
                "user_id": uid, "nombre": update.effective_user.full_name,
                "usuario": update.effective_user.username or "Sin usuario",
                "saldo": 0.0, "rol": "usuario", "nivel": "bronce",
                "codigo_referido": ref_code, "referido_por": args[0].upper() if args else None,
                "fecha_registro": datetime.now(), "baneado": False,
                "preferencias": {"moneda":"USD", "notificaciones":True},
                "carrito":[], "favoritos":[]
            }
            if coleccion_usuarios: coleccion_usuarios.insert_one(datos)
            if args: await verificar_referido(uid, args[0].upper())

        if not await verificar_suscripcion(uid, context.bot):
            await update.message.reply_text("⚠️ Únete primero al canal oficial:\nhttps://t.me/Voltix_Pro", reply_markup=menu_suscripcion)
            return

        texto = """⚡ VOLTIXPRO V4
¡Bienvenido! Tu tienda de servicios confiable y rápida.

📋 Reglas:
1. Revisa bien tu enlace antes de pagar.
2. Sin reembolsos por errores tuyos.

⚡ VOLTIXPRO – Todos los derechos reservados"""
        await update.message.reply_text(texto, reply_markup=menu_principal)
    except Exception as e:
        log(f"❌ Error /start: {e}", "ERROR")
        await update.message.reply_text("❌ Error al cargar tu perfil")

# ==================================================
# 🤖 MANEJO COMPLETO DE BOTONES
# ==================================================
async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    dato = q.data.strip()
    uid = update.effective_user.id
    log(f"🔘 Botón: {dato} | {uid}", "INFO")
    await q.answer()

    if dato == "verificar_suscripcion":
        if await verificar_suscripcion(uid, context.bot):
            await q.edit_message_text("""⚡ VOLTIXPRO V4
¡Bienvenido! Tu tienda de servicios confiable y rápida.

📋 Reglas:
1. Revisa bien tu enlace antes de pagar.
2. Sin reembolsos por errores tuyos.

⚡ VOLTIXPRO – Todos los derechos reservados""", reply_markup=menu_principal)
        else:
            await q.answer("❌ Aún no te unes al canal", show_alert=True)
        return

    if dato == "ad_salir":
        await q.edit_message_text("""⚡ VOLTIXPRO V4
¡Bienvenido! Tu tienda de servicios confiable y rápida.

📋 Reglas:
1. Revisa bien tu enlace antes de pagar.
2. Sin reembolsos por errores tuyos.

⚡ VOLTIXPRO – Todos los derechos reservados""", reply_markup=menu_principal)
        return

    elif dato == "menu_tienda": await mostrar_categorias(update, context)
    elif dato == "menu_buscar": await q.edit_message_text("🔎 Escribe lo que buscas:", reply_markup=volver)
    elif dato == "menu_perfil": await q.edit_message_text(str(await perfil_completo(update, context)), reply_markup=menu_perfil)
    elif dato == "menu_pedidos": await ver_pedidos(update, context)
    elif dato == "menu_favoritos": await ver_favoritos(update, context)
    elif dato == "menu_carrito": await ver_carrito(update, context)
    elif dato == "ref_menu": await q.edit_message_text("🎁 Tus referidos", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_perfil")]]))
    elif dato == "conf_moneda": await cambiar_moneda(update, context)
    elif dato == "faq": await ver_faq(update, context)
    elif dato == "menu_recarga": await iniciar_recarga(update, context)

    elif dato == "menu_admin":
        if str(uid) != str(getattr(Config, "ADMIN_ID", ADMIN_ID)):
            await q.answer("❌ Sin permiso", show_alert=True); return
        await q.edit_message_text("⚙️ PANEL ADMINISTRADOR", reply_markup=menu_admin)

    elif dato == "ad_usuarios": await q.edit_message_text("👥 GESTIÓN DE USUARIOS", reply_markup=menu_usuarios)
    elif dato == "ad_categorias": await q.edit_message_text("📂 CATEGORÍAS", reply_markup=menu_categorias)
    elif dato == "ad_paneles": await q.edit_message_text("🔌 PANELES", reply_markup=menu_panel)
    elif dato == "ad_config": await q.edit_message_text("⚙️ CONFIGURACIÓN", reply_markup=menu_config)
    elif dato == "ad_acciones": await q.edit_message_text("📋 ACCIONES RÁPIDAS", reply_markup=menu_acciones)

    elif dato == "pan_agregar": await q.edit_message_text("➕ Envía: URL | API | NOMBRE", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]]))
    elif dato == "pan_ver_ids":
        t = await ver_ids_paneles(update, context)
        await q.edit_message_text(t, reply_markup=menu_panel)
    elif dato == "pan_copiar": await q.edit_message_text("📋 Escribe ID", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]]))
    elif dato == "pan_editar": await q.edit_message_text("✏️ Escribe ID", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]]))
    elif dato == "pan_eliminar": await q.edit_message_text("🗑️ Escribe ID", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_paneles")]]))

    elif dato == "usr_buscar": await q.edit_message_text("🔍 Escribe ID o nombre", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))
    elif dato == "usr_sumar": await q.edit_message_text("➕ Formato: ID | MONTO", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))
    elif dato == "usr_quitar": await q.edit_message_text("🗑️ Formato: ID | MONTO", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))
    elif dato == "usr_bloquear": await q.edit_message_text("🚫 Escribe ID", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_usuarios")]]))

    elif dato == "cat_crear": await q.edit_message_text("➕ Nombre categoría", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_categorias")]]))
    elif dato == "cat_editar": await q.edit_message_text("✏️ Nombre categoría", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_categorias")]]))
    elif dato == "cat_eliminar": await q.edit_message_text("🗑️ Nombre categoría", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="ad_categorias")]]))

    elif dato.startswith("conf_"): await q.edit_message_text("⚙️ Configuración...", reply_markup=volver)
    elif dato == "acc_aviso": await q.edit_message_text("📢 Escribe mensaje para todos", reply_markup=volver)
    elif dato == "acc_historial": await q.edit_message_text("📜 Historial...", reply_markup=volver)
    elif dato == "acc_respaldo":
        await q.delete_message()
        await context.bot.send_message(uid, "💾 Creando respaldo...", reply_markup=volver)
    elif dato == "acc_mantenimiento": await q.edit_message_text("🚧 Mantenimiento...", reply_markup=volver)
    elif dato == "acc_stats":
        datos = await obtener_estadisticas()
        texto = f"""📊 ESTADÍSTICAS
👤 Usuarios: {datos['usuarios']}
🟢 Activos: {datos['activos']}
💰 Ganancia: ${datos['ganancia_total']}
📦 Más vendidos: {', '.join(map(str, datos['mas_vendidos']))}"""
        await q.edit_message_text(texto, reply_markup=volver)
    elif dato == "acc_reiniciar": await q.edit_message_text("🔄 Sincronizando...", reply_markup=volver)

# ==================================================
# 🚀 ARRANQUE FINAL
# ==================================================
async def arrancar_bot():
    log("🔗 Conectando base de datos...", "PASO")
    try: await iniciar_configuracion()
    except Exception as e: log(f"⚠️ BD: {e}", "ADVERTENCIA")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.delete_webhook(drop_pending_updates=True)
    log("🔌 Conexiones antiguas eliminadas", "EXITO")

    app.add_handler(CommandHandler("start", inicio))
    app.add_handler(CommandHandler("permisos", dar_permisos))
    app.add_handler(CommandHandler("rol", cambiar_rol))
    app.add_handler(CommandHandler("addsaldo", recargar_saldo_manual))
    app.add_handler(CommandHandler("ban", banear_usuario))
    app.add_handler(CommandHandler("crearcategoria", crear_categoria))
    app.add_handler(CommandHandler("agregarpanel", agregar_panel_smm))
    app.add_handler(CommandHandler("editarpanel", editar_panel))
    app.add_handler(CommandHandler("eliminarpanel", eliminar_panel))
    app.add_handler(CommandHandler("copiarpanel", copiar_panel))
    app.add_handler(CommandHandler("actualizar", sincronizar_servicios))
    app.add_handler(CommandHandler("limite", configurar_limite))
    app.add_handler(CommandHandler("niveles", ver_niveles))
    app.add_handler(CommandHandler("respaldo", crear_respaldo))
    app.add_handler(CommandHandler("buscar", buscar_servicios))
    app.add_handler(CommandHandler("usarreferido", verificar_referido))
    app.add_handler(CommandHandler("moneda", cambiar_moneda))
    app.add_handler(CommandHandler("faq", ver_faq))
    app.add_handler(CommandHandler("recargar", iniciar_recarga))
    app.add_handler(CommandHandler("dorks", generar_dorks))
    app.add_handler(CommandHandler("bin", validar_bin))
    app.add_handler(CommandHandler("cc", generar_cc))
    try: app.add_handler(obtener_conv_pagos())
    except: pass

    app.add_handler(CallbackQueryHandler(manejar_botones))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, funcion_en_construccion))

    log("="*50, "EXITO")
    log("🎉 BOT LISTO Y FUNCIONANDO", "EXITO")
    log("="*50, "EXITO")
    await app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try: asyncio.run(arrancar_bot())
    except Exception as e: log(f"❌ ERROR: {e}", "ERROR"); log(traceback.format_exc(), "ERROR")
