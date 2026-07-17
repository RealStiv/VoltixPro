import sys
import warnings
import os
import certifi
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
from flask import Flask, request
import asyncio
from threading import Thread

print("✅ VOLTIXPRO V4 CARGANDO...")

from config import Config
from mongodb import (
    coleccion_usuarios, coleccion_categorias, coleccion_servicios,
    coleccion_facturas, coleccion_paneles, coleccion_configuracion,
    iniciar_configuracion
)
from texto import t
from interfaces.botones import (
    menu_principal, menu_suscripcion, menu_admin, menu_usuarios,
    menu_categorias, menu_panel, menu_config, menu_acciones
)
from modulos.acceso import verificar_suscripcion
from modulos.pagos_facturas import obtener_conv_pagos, procesar_factura, iniciar_recarga
from modulos.tienda_categorias import mostrar_categorias, mostrar_servicios
from modulos.perfil import mostrar_perfil
from modulos.pedidos import ver_pedidos
from modulos.herramientas import generar_dorks, validar_bin, generar_cc
from modulos.admin_total import (
    dar_permisos, cambiar_rol, recargar_saldo_manual,
    banear_usuario, guardar_configuracion, sincronizar_servicios,
    crear_categoria, copiar_panel, alternar_mantenimiento, crear_respaldo,
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
from datetime import datetime

PUERTO = int(os.getenv("PORT", 8080))
DOMINIO = "https://voltixpro.onrender.com"
servidor = Flask(__name__)
bot_app = None
loop_principal = None
listo = False

esperando_respuesta = {}


@servidor.route('/')
def activo():
    return "✅ VOLTIXPRO V4 EN LÍNEA"

@servidor.route('/webhook', methods=['GET','POST'])
def recibir():
    global loop_principal, bot_app, listo
    if request.method == 'POST' and listo:
        try:
            datos = request.get_json()
            print(f"📥 LLEGÓ SOLICITUD: {list(datos.keys())}")
            update = Update.de_json(datos, bot_app.bot)
            asyncio.run_coroutine_threadsafe(bot_app.process_update(update), loop_principal)
        except Exception as e:
            print(f"❌ ERROR AL RECIBIR: {str(e)}")
    return "✅ RECIBIDO", 200

def arrancar_servidor():
    servidor.run(host="0.0.0.0", port=PUERTO, use_reloader=False)


async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user

    # Verificar referido al ingresar por enlace
    if args:
        codigo = args[0].upper()
        await verificar_referido(user.id, codigo)

    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    
    if not usuario:
        await asignar_codigo_referido(user.id)
        coleccion_usuarios.insert_one({
            "user_id": user.id,
            "nombre": user.full_name or user.first_name,
            "saldo": 0.0,
            "rol": "usuario",
            "nivel": "bronce",
            "gasto_total": 0.0,
            "gasto_hoy": 0.0,
            "ultimo_gasto_dia": None,
            "codigo_referido": await asignar_codigo_referido(user.id),
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
        await update.message.reply_text(t("necesitas_suscribirte"), reply_markup=menu_suscripcion)
        return
    
    await update.message.reply_text(t("bienvenida"), reply_markup=menu_principal)


async def recibir_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto_recibido = update.message.text.strip()

    if user_id not in esperando_respuesta:
        return

    accion = esperando_respuesta[user_id]
    del esperando_respuesta[user_id]

    await guardar_configuracion(accion, texto_recibido)
    await update.message.reply_text("✅ Configuración actualizada correctamente")


async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dato = query.data.strip()
    await query.answer()
    print(f"🔘 OPCIÓN SELECCIONADA: '{dato}'")

    # Verificar suscripción
    if dato == "verificar_suscripcion":
        if await verificar_suscripcion(update, context):
            await query.edit_message_text(t("suscrito_correcto"), reply_markup=menu_principal)
        else:
            await query.answer("❌ Aún no te has suscrito", show_alert=True)

    # Menú principal
    elif dato == "menu_tienda":
        await mostrar_categorias(update, context)
    elif dato == "menu_buscar":
        await query.edit_message_text("🔎 Escribe: /buscar nombre del servicio")
    elif dato == "menu_favoritos":
        await ver_favoritos(update, context)
    elif dato == "menu_carrito":
        await ver_carrito(update, context)
    elif dato == "menu_recarga":
        await iniciar_recarga(update, context)
    elif dato == "menu_perfil":
        await perfil_completo(update, context)
    elif dato == "menu_pedidos":
        await ver_pedidos(update, context)
    elif dato == "menu_admin":
        if update.effective_user.id == Config.ADMIN_ID:
            await query.edit_message_text("⚙️ PANEL DE ADMINISTRADOR", reply_markup=menu_admin)
        else:
            await query.answer("❌ Sin acceso", show_alert=True)

    # Volver al inicio
    elif dato == "ad_salir":
        await query.edit_message_text(t("bienvenida"), reply_markup=menu_principal)

    # Submenús de administrador
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

    # Acciones de paneles
    elif dato == "pan_agregar":
        await query.edit_message_text("📝 Escribe: /agregarpanel NOMBRE | URL_COMPLETA | API_KEY | PORCENTAJE")
    elif dato == "pan_ver_ids":
        await ver_ids_paneles(update, context)
    elif dato == "pan_copiar":
        await query.edit_message_text("📋 Escribe: /copiarpanel ID_ORIGEN ID_DESTINO")
    elif dato == "pan_editar":
        await query.edit_message_text("✏️ Escribe: /editarpanel ID | CAMPO | VALOR")
    elif dato == "pan_eliminar":
        await query.edit_message_text("🗑️ Escribe: /borrarpanel ID_DEL_PANEL")

    # Acciones rápidas
    elif dato == "acc_aviso":
        esperando_respuesta[update.effective_user.id] = "mensaje_aviso"
        await query.edit_message_text("📢 Escribe el mensaje para todos los usuarios:")
    elif dato == "acc_historial":
        await ver_historial(update, context)
    elif dato == "acc_respaldo":
        await crear_respaldo(update, context)
    elif dato == "acc_mantenimiento":
        await alternar_mantenimiento(update, context)
    elif dato == "acc_stats":
        await ver_niveles(update, context)
    elif dato == "acc_reiniciar":
        await sincronizar_servicios(update, context)

    # Configuración
    elif dato == "conf_niveles":
        await ver_niveles(update, context)
    elif dato == "conf_limite":
        esperando_respuesta[update.effective_user.id] = "limite_diario"
        await query.edit_message_text("🚧 Escribe el monto límite diario:")
    elif dato == "conf_referido":
        esperando_respuesta[update.effective_user.id] = "recompensa_referido"
        await query.edit_message_text("🎁 Escribe el monto de recompensa por referido:")
    elif dato == "conf_saldobajo":
        esperando_respuesta[update.effective_user.id] = "aviso_saldo_minimo"
        await query.edit_message_text("🔔 Escribe el monto mínimo para avisar saldo bajo:")

    # Carrito
    elif dato == "carrito_vaciar":
        coleccion_usuarios.update_one({"user_id": update.effective_user.id}, {"$set": {"carrito": []}})
        await query.answer("✅ Carrito vaciado", show_alert=True)
        await ver_carrito(update, context)

    # Categorías y servicios
    elif dato.startswith("ver_cat_"):
        nombre_cat = dato.split("_", 2)[2]
        await mostrar_servicios(update, context, nombre_cat)

    else:
        await query.answer("❌ Opción no disponible", show_alert=True)
        print(f"⚠️ Opción desconocida: '{dato}'")


async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip()
    print(f"💬 MENSAJE DE {user_id}: {texto}")

    if texto.startswith("/"):
        return

    if user_id in esperando_respuesta:
        await recibir_configuracion(update, context)
        return


async def iniciar_todo():
    global bot_app, loop_principal, listo
    loop_principal = asyncio.get_running_loop()

    print("⚙️ INICIALIZANDO CONFIGURACIÓN...")
    await iniciar_configuracion()

    print("🔑 CARGANDO BOT...")
    bot_app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    await bot_app.initialize()

    # Comandos
    bot_app.add_handler(CommandHandler("start", inicio))
    bot_app.add_handler(CommandHandler("permisos", dar_permisos))
    bot_app.add_handler(CommandHandler("rol", cambiar_rol))
    bot_app.add_handler(CommandHandler("addsaldo", recargar_saldo_manual))
    bot_app.add_handler(CommandHandler("ban", banear_usuario))
    bot_app.add_handler(CommandHandler("unban", banear_usuario))
    bot_app.add_handler(CommandHandler("actualizar", sincronizar_servicios))
    bot_app.add_handler(CommandHandler("agregarpanel", agregar_panel_smm))
    bot_app.add_handler(CommandHandler("editarpanel", editar_panel))
    bot_app.add_handler(CommandHandler("borrarpanel", eliminar_panel))
    bot_app.add_handler(CommandHandler("copiarpanel", copiar_panel))
    bot_app.add_handler(CommandHandler("crearcategoria", crear_categoria))
    bot_app.add_handler(CommandHandler("limite", configurar_limite))
    bot_app.add_handler(CommandHandler("buscar", buscar_servicios))
    bot_app.add_handler(CommandHandler("usarreferido", verificar_referido))
    bot_app.add_handler(CommandHandler("moneda", cambiar_moneda))
    bot_app.add_handler(CommandHandler("faq", ver_faq))
    bot_app.add_handler(CommandHandler("perfil", perfil_completo))
    bot_app.add_handler(CommandHandler("respaldo", crear_respaldo))
    bot_app.add_handler(CommandHandler("recargar", iniciar_recarga))
    bot_app.add_handler(CommandHandler("dorks", generar_dorks))
    bot_app.add_handler(CommandHandler("bin", validar_bin))
    bot_app.add_handler(CommandHandler("cc", generar_cc))

    # Manejadores
    bot_app.add_handler(obtener_conv_pagos())
    bot_app.add_handler(CallbackQueryHandler(manejar_botones))
    bot_app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, manejar_mensajes))

    # Webhook
    await bot_app.bot.delete_webhook(drop_pending_updates=True)
    await bot_app.bot.set_webhook(
        url=f"{DOMINIO}/webhook",
        drop_pending_updates=True,
        certificate=certifi.where()
    )
    listo = True

    print(f"✅ WEBHOOK ACTIVO EN: {DOMINIO}/webhook")
    print("✅ VOLTIXPRO V4 TOTALMENTE EN LÍNEA")

    # Revisión automática de paneles cada 30 minutos
    async def revisar_periodicamente():
        while True:
            await asyncio.sleep(1800)
            await revisar_estado_paneles(bot_app)
    asyncio.create_task(revisar_periodicamente())

    await bot_app.start()
    await bot_app.updater.start_polling()


if __name__ == "__main__":
    hilo = Thread(target=arrancar_servidor, daemon=True)
    hilo.start()
    asyncio.run(iniciar_todo())
