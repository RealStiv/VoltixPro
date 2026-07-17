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

print("✅ ARCHIVOS CARGADOS - TODO CON BOTONES")

from config import Config
from mongodb import (
    coleccion_usuarios, coleccion_categorias, coleccion_servicios,
    coleccion_facturas, coleccion_paneles, coleccion_configuracion
)
from texto import t
from interfaces.botones import (
    menu_principal, menu_suscripcion, menu_admin,
    menu_usuarios, menu_categorias, menu_panel as menu_paneles,
    menu_config, menu_acciones, botones_factura, botones_lista_facturas
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
    crear_categoria
)
from api.gestor_paneles import agregar_panel_smm, listar_paneles, editar_panel, eliminar_panel
from api.importar_servicios import importar_desde_api
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
    return "✅ VOLTIXPRO ENCENDIDO"

@servidor.route('/webhook', methods=['GET','POST'])
def recibir():
    global loop_principal, bot_app, listo
    if request.method == 'POST' and listo:
        try:
            datos = request.get_json()
            print(f"📥 LLEGÓ ACCIÓN: {list(datos.keys())}")
            update = Update.de_json(datos, bot_app.bot)
            asyncio.run_coroutine_threadsafe(bot_app.process_update(update), loop_principal)
        except Exception as e:
            print(f"❌ ERROR AL RECIBIR: {str(e)}")
    return "✅ RECIBIDO", 200

def arrancar_servidor():
    servidor.run(host="0.0.0.0", port=PUERTO, use_reloader=False)


async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    
    if not usuario:
        coleccion_usuarios.insert_one({
            "user_id": user.id,
            "nombre": user.full_name,
            "saldo": 0.0,
            "rol": "usuario",
            "permisos": "ver,comprar",
            "claves_api": "Sin claves asignadas",
            "baneado": False,
            "creado_en": datetime.now()
        })
    
    if not await verificar_suscripcion(update, context):
        await update.message.reply_text(t("necesitas_suscribirte"), parse_mode="HTML", reply_markup=menu_suscripcion)
        return
    
    await update.message.reply_text(t("bienvenida"), parse_mode="HTML", reply_markup=menu_principal)


async def recibir_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto_recibido = update.message.text.strip()

    if user_id not in esperando_respuesta:
        return

    accion = esperando_respuesta[user_id]
    del esperando_respuesta[user_id]

    resultado = await guardar_configuracion(accion, texto_recibido)
    await update.message.reply_text(resultado, reply_markup=menu_config, parse_mode="HTML")


async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dato = query.data.strip()
    await query.answer()
    print(f"🔘 BOTÓN PRESIONADO: '{dato}'")
    
    # ✅ VERIFICAR SUSCRIPCIÓN
    if dato == "verificar_sus":
        if await verificar_suscripcion(update, context):
            await query.edit_message_text(t("suscrito_correcto"), parse_mode="HTML")
            await inicio(update, context)
        else:
            await query.answer("❌ Aún no apareces como suscrito. Espera 1 minuto y vuelve a pulsar", show_alert=True)
    
    # ✅ MENÚ PRINCIPAL
    elif dato == "menu_tienda":
        await mostrar_categorias(update, context)
    elif dato == "menu_recarga":
        await iniciar_recarga(update, context)
    elif dato == "menu_perfil":
        await mostrar_perfil(update, context)
    elif dato == "menu_pedidos":
        await ver_pedidos(update, context)
    elif dato == "menu_herramientas":
        await query.edit_message_text("""🔧 **HERRAMIENTAS DISPONIBLES**
/dorks → Generar dorks
/bin 123456 → Validar BIN
/cc 5 → Generar tarjetas""", parse_mode="Markdown")
    elif dato == "menu_admin":
        await query.edit_message_text("⚙️ **PANEL DE ADMINISTRADOR**", reply_markup=menu_admin, parse_mode="HTML")

    # ✅ VOLVER A INICIO / SALIR DE ADMIN
    elif dato == "ad_salir":
        await inicio(update, context)

    # ✅ MENÚS ADMINISTRATIVOS
    elif dato == "ad_usuarios":
        await query.edit_message_text("👥 **GESTIÓN DE USUARIOS**\nElige una acción:", reply_markup=menu_usuarios, parse_mode="Markdown")
    elif dato == "ad_categorias":
        await query.edit_message_text("📂 **GESTIÓN DE CATEGORÍAS**\nElige lo que quieres hacer:", reply_markup=menu_categorias, parse_mode="Markdown")
    elif dato == "ad_panel":
        await query.edit_message_text("➕ **GESTIÓN DE PANELES SMM**\nElige una opción:", reply_markup=menu_paneles, parse_mode="Markdown")
    elif dato == "menu_admin":
        await query.edit_message_text("⚙️ **PANEL DE ADMINISTRADOR**", reply_markup=menu_admin, parse_mode="Markdown")
    elif dato == "ad_actualizar":
        await query.edit_message_text("🔄 Sincronizando servicios desde paneles... ⏳", reply_markup=menu_admin)
        resultado = await importar_desde_api()
        await query.edit_message_text(resultado, reply_markup=menu_admin, parse_mode="HTML")
    elif dato == "ad_facturas":
        lista = list(coleccion_facturas.find({"estado": "PENDIENTE"}))
        if not lista:
            await query.edit_message_text("✅ No hay facturas pendientes", reply_markup=menu_admin)
        else:
            await query.edit_message_text("🧾 **FACTURAS PENDIENTES**", reply_markup=botones_lista_facturas(lista))
    elif dato == "ad_config":
        await query.edit_message_text("⚙️ **CONFIGURACIÓN GENERAL DEL BOT**\nElige lo que quieres modificar:", reply_markup=menu_config, parse_mode="Markdown")
    elif dato == "acc_menu":
        await query.edit_message_text("📊 **ACCIONES RÁPIDAS**\nElige la acción:", reply_markup=menu_acciones, parse_mode="Markdown")

    # ✅ ACCIONES DE PANELES
    elif dato == "pan_agregar":
        await query.edit_message_text("📝 **AGREGAR NUEVO PANEL**\nEscribe: `/agregarpanel NOMBRE | URL | API_KEY | PORCENTAJE`", reply_markup=menu_paneles)
    elif dato == "pan_lista":
        await listar_paneles(update, context)
    elif dato == "pan_editar":
        await query.edit_message_text("✏️ **EDITAR PANEL**\nEscribe: `/editarpanel ID CAMPO VALOR`", reply_markup=menu_paneles)
    elif dato == "pan_eliminar":
        await query.edit_message_text("❌ **ELIMINAR PANEL**\nEscribe: `/borrarpanel ID`", reply_markup=menu_paneles)

    # ✅ ACCIONES DE CONFIGURACIÓN
    elif dato == "conf_minimo":
        esperando_respuesta[update.effective_user.id] = "monto_minimo_recarga"
        await query.edit_message_text("💵 **MONTO MÍNIMO DE RECARGA**\nEscribe el nuevo monto:", reply_markup=menu_config)
    elif dato == "conf_canal":
        esperando_respuesta[update.effective_user.id] = "canal_obligatorio"
        await query.edit_message_text("📢 **CANAL OBLIGATORIO**\nEscribe: @nombre_canal o ID:", reply_markup=menu_config)
    elif dato == "conf_pago":
        esperando_respuesta[update.effective_user.id] = "datos_pago"
        await query.edit_message_text("🔑 **DATOS DE PAGO**\nEscribe: Banco | Número | Titular", reply_markup=menu_config)
    elif dato == "conf_margen":
        esperando_respuesta[update.effective_user.id] = "porcentaje_ganancia"
        await query.edit_message_text("📊 **PORCENTAJE DE GANANCIA**\nEscribe solo el número, ejemplo: 20 = 20%", reply_markup=menu_config)
    elif dato == "conf_mensajes":
        esperando_respuesta[update.effective_user.id] = "mensajes_aviso"
        await query.edit_message_text("🔔 **MENSAJES DEL BOT**\nEscribe el mensaje personalizado:", reply_markup=menu_config)

    # ✅ ACCIONES RÁPIDAS
    elif dato == "acc_aviso":
        await query.edit_message_text("📢 **ENVIAR AVISO GENERAL**\nEscribe el mensaje que recibirán todos los usuarios:", reply_markup=menu_acciones)
    elif dato == "acc_stats":
        stats = {
            "usuarios": coleccion_usuarios.count_documents({}),
            "activos": coleccion_usuarios.count_documents({"baneado": False}),
            "servicios": coleccion_servicios.count_documents({"activo": True}),
            "facturas_pen": coleccion_facturas.count_documents({"estado": "PENDIENTE"}),
            "paneles": coleccion_paneles.count_documents({"activo": True})
        }
        texto = f"""📊 **ESTADÍSTICAS GENERALES**

👥 Total usuarios: {stats['usuarios']}
✅ Activos: {stats['activos']}
🛠️ Servicios activos: {stats['servicios']}
🧾 Facturas pendientes: {stats['facturas_pen']}
🔌 Paneles conectados: {stats['paneles']}
"""
        await query.edit_message_text(texto, reply_markup=menu_acciones, parse_mode="Markdown")
    elif dato == "acc_reiniciar":
        await query.edit_message_text("🔄 Sincronizando todo nuevamente... ⏳", reply_markup=menu_acciones)
        resultado = await importar_desde_api()
        await query.edit_message_text(resultado, reply_markup=menu_acciones, parse_mode="HTML")

    # ✅ TIENDA Y OTROS
    elif dato.startswith("ver_cat_"):
        categoria = dato.split("_", 2)[2]
        await mostrar_servicios(update, context, categoria)
    elif dato.startswith("fac_ver_"):
        numero = dato.split("_")[-1]
        await procesar_factura(update, context, numero)
    elif dato.startswith("fac_ok_"):
        partes = dato.split("_")
        numero = partes[2]
        monto = float(partes[3])
        await procesar_factura(update, context, numero, aprobar=True, monto=monto)
    elif dato.startswith("fac_no_"):
        numero = dato.split("_")[-1]
        await procesar_factura(update, context, numero, aprobar=False)

    else:
        await query.answer("❌ Opción no disponible", show_alert=True)
        print(f"⚠️ Acción desconocida: '{dato}'")


async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip()
    print(f"💬 MENSAJE RECIBIDO DE {user_id}: {texto}")

    if texto.startswith("/"):
        return

    if user_id in esperando_respuesta:
        await recibir_configuracion(update, context)
        return

    if texto == "🛒 Tienda SMM":
        await mostrar_categorias(update, context)
    elif texto == "💰 Recargar Saldo":
        await iniciar_recarga(update, context)
    elif texto == "👤 Mi Perfil":
        await mostrar_perfil(update, context)
    elif texto == "📦 Mis Pedidos":
        await ver_pedidos(update, context)
    elif texto == "🔧 Herramientas":
        await update.message.reply_text("""🔧 **HERRAMIENTAS DISPONIBLES**
/dorks → Generar dorks
/bin 123456 → Validar BIN
/cc 5 → Generar tarjetas""", parse_mode="Markdown")
    elif texto == "⚙️ Admin Total" and user_id == Config.ADMIN_ID:
        stats = {
            "usuarios": coleccion_usuarios.count_documents({}),
            "categorias": coleccion_categorias.count_documents({}),
            "servicios": coleccion_servicios.count_documents({"activo": True}),
            "facturas": coleccion_facturas.count_documents({"estado": "PENDIENTE"}),
            "paneles": coleccion_paneles.count_documents({"activo": True})
        }
        await update.message.reply_text(
            t("admin_panel",** stats),
            parse_mode="HTML",
            reply_markup=menu_admin
        )


async def iniciar_todo():
    global bot_app, loop_principal, listo
    loop_principal = asyncio.get_running_loop()

    print("=============================================================================")
    print(f"🔑 TOKEN CARGADO CORRECTAMENTE: {'SÍ' if Config.BOT_TOKEN else 'NO'}")
    print("=============================================================================")

    bot_app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    await bot_app.initialize()
    
    # 📌 TODOS LOS COMANDOS REGISTRADOS
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
    bot_app.add_handler(CommandHandler("crearcategoria", crear_categoria))
    bot_app.add_handler(CommandHandler("recargar", iniciar_recarga))
    bot_app.add_handler(CommandHandler("dorks", generar_dorks))
    bot_app.add_handler(CommandHandler("bin", validar_bin))
    bot_app.add_handler(CommandHandler("cc", generar_cc))

    bot_app.add_handler(obtener_conv_pagos())
    bot_app.add_handler(CallbackQueryHandler(manejar_botones))
    bot_app.add_handler(MessageHandler(filters.ALL, manejar_mensajes))

    await bot_app.bot.delete_webhook(drop_pending_updates=True)
    await bot_app.bot.set_webhook(
        url=f"{DOMINIO}/webhook",
        drop_pending_updates=True,
        certificate=certifi.where()
    )
    listo = True
    print(f"✅ WEBHOOK ACTIVO EN: {DOMINIO}/webhook")
    print("✅ TODAS LAS CONEXIONES CARGADAS - BOT LISTO")

    await bot_app.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    Thread(target=arrancar_servidor, daemon=True).start()
    asyncio.run(iniciar_todo())
