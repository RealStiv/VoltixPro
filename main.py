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
from flask import Flask
import asyncio
from threading import Thread

print("⚡ INICIANDO VOLTIXPRO V4...")

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

PUERTO = int(os.getenv("PORT", 8080))
servidor = Flask(__name__)
bot_app = None
listo = False
esperando_respuesta = {}


# Ruta web solo para que Render no detenga el servicio
@servidor.route('/')
def estado():
    return "✅ VOLTIXPRO V4 EN LÍNEA Y FUNCIONANDO"

def iniciar_servidor():
    servidor.run(host="0.0.0.0", port=PUERTO)


async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user = update.effective_user

    if args:
        codigo = args[0].upper()
        await verificar_referido(user.id, codigo)

    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    
    if not usuario:
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
        await update.message.reply_text(
            f"🔔 Antes de empezar debes unirte al canal oficial:\n{canal}",
            reply_markup=menu_suscripcion
        )
        return
    
    await bienvenida_personalizada(update, context)


async def recibir_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip()
    if user_id not in esperando_respuesta:
        return
    accion = esperando_respuesta.pop(user_id)
    resultado = await guardar_configuracion(accion, texto)
    await update.message.reply_text(resultado)


async def ver_estadisticas_generales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        return await update.callback_query.answer("❌ Sin permiso", show_alert=True)
    
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


async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dato = query.data.strip()
    await query.answer()
    print(f"🔘 Botón presionado: {dato}")

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
            await query.answer("❌ Solo el administrador puede entrar", show_alert=True)
    elif dato == "ad_salir": await bienvenida_personalizada(update, context)
    elif dato == "ad_usuarios": await query.edit_message_text("👥 GESTIÓN DE USUARIOS", reply_markup=menu_usuarios)
    elif dato == "ad_categorias": await query.edit_message_text("📂 GESTIÓN DE CATEGORÍAS", reply_markup=menu_categorias)
    elif dato == "ad_paneles": await query.edit_message_text("🔌 GESTIÓN DE PANELES", reply_markup=menu_panel)
    elif dato == "ad_config": await query.edit_message_text("⚙️ CONFIGURACIÓN GENERAL", reply_markup=menu_config)
    elif dato == "ad_acciones": await query.edit_message_text("📋 ACCIONES RÁPIDAS", reply_markup=menu_acciones)
    elif dato == "pan_agregar": await query.edit_message_text("📝 Escribe: /agregarpanel NOMBRE | URL | CLAVE | PORCENTAJE")
    elif dato == "pan_ver_ids": await ver_ids_paneles(update, context)
    elif dato == "pan_copiar": await query.edit_message_text("📋 Escribe: /copiarpanel ID_ORIGEN ID_DEL_PANEL")
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
/cambiar emoji_principal ⚡
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


async def iniciar_todo():
    global bot_app, listo

    print("⚙️ Cargando configuración base...")
    await iniciar_configuracion()

    print("🤖 Conectando al bot...")
    bot_app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    await bot_app.initialize()

    # TODOS LOS COMANDOS
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
    bot_app.add_handler(CommandHandler("pruebaservicio", probar_servicio))
    bot_app.add_handler(CommandHandler("estadisticas", ver_estadisticas_generales))
    bot_app.add_handler(CommandHandler("dorks", generar_dorks))
    bot_app.add_handler(CommandHandler("bin", validar_bin))
    bot_app.add_handler(CommandHandler("cc", generar_cc))

    # MENSAJES Y BOTONES
    bot_app.add_handler(obtener_conv_pagos())
    bot_app.add_handler(MessageHandler(filters.PHOTO, subir_foto_bienvenida))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_configuracion))
    bot_app.add_handler(CallbackQueryHandler(manejar_botones))

    # ELIMINAMOS CUALQUIER WEBHOOK QUE ESTORBE
    await bot_app.bot.delete_webhook(drop_pending_updates=True)
    print("🔌 Webhook eliminado | Modo Polling directo ACTIVO")

    # REVISIÓN AUTOMÁTICA
    async def revisar_periodico():
        while True:
            await asyncio.sleep(1800)
            await revisar_estado_paneles(bot_app)
    asyncio.create_task(revisar_periodico())

    listo = True
    print("✅ VOLTIXPRO V4 ARRANCADO Y ESCUCHANDO TUS MENSAJES")

    await bot_app.start()
    await bot_app.updater.start_polling(drop_pending_updates=True)


if __name__ == "__main__":
    # Servidor web en segundo plano
    hilo = Thread(target=iniciar_servidor, daemon=True)
    hilo.start()
    # Ejecutamos el bot
    asyncio.run(iniciar_todo())
