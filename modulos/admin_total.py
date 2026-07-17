from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
import asyncio
from config import Config
from mongodb import (
    coleccion_usuarios, coleccion_categorias, coleccion_configuracion
)
from api.importar_servicios import importar_desde_api

# 🛡️ Evitar que se ejecute dos veces la sincronización al mismo tiempo
sincronizando_ahora = False


# 📌 Asignar permisos de administrador
async def dar_permisos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes autorización para esta acción.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Formato correcto:\n`/permisos ID_DEL_USUARIO admin`",
            parse_mode="Markdown"
        )
        return

    try:
        usuario_id = int(context.args[0])
        nuevo_rol = context.args[1].lower()
    except:
        await update.message.reply_text("❌ El ID debe ser solo números.")
        return

    if nuevo_rol not in ["usuario", "admin"]:
        await update.message.reply_text("❌ El rol solo puede ser: `usuario` o `admin`")
        return

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"rol": nuevo_rol}},
        upsert=True
    )

    await update.message.reply_text(f"✅ Rol cambiado correctamente a **{nuevo_rol}**")


# 📌 Cambiar rol de usuario
async def cambiar_rol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await dar_permisos(update, context)


# 📌 Agregar o quitar saldo
async def recargar_saldo_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes autorización.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Formato correcto:\n`/addsaldo ID_DEL_USUARIO CANTIDAD`",
            parse_mode="Markdown"
        )
        return

    try:
        usuario_id = int(context.args[0])
        cantidad = float(context.args[1])
    except:
        await update.message.reply_text("❌ Datos incorrectos, usa solo números.")
        return

    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    saldo_anterior = usuario.get("saldo", 0) if usuario else 0
    saldo_nuevo = saldo_anterior + cantidad

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"saldo": saldo_nuevo}},
        upsert=True
    )

    accion = "Agregado" if cantidad >= 0 else "Quitado"
    await update.message.reply_text(
        f"✅ Saldo actualizado\n\n👤 Usuario: `{usuario_id}`\n💵 Anterior: ${saldo_anterior:.2f}\n{accion}: ${abs(cantidad):.2f}\n💵 Nuevo: ${saldo_nuevo:.2f}",
        parse_mode="Markdown"
    )


# 📌 Bloquear / Desbloquear usuario
async def banear_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes autorización.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Formato correcto:\n`/ban ID_DEL_USUARIO` para bloquear\n`/unban ID_DEL_USUARIO` para desbloquear",
            parse_mode="Markdown"
        )
        return

    try:
        usuario_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ El ID debe ser solo números.")
        return

    accion = "baneado" if update.message.text.startswith("/ban") else "desbloqueado"
    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"baneado": accion == "baneado"}},
        upsert=True
    )

    await update.message.reply_text(f"✅ Usuario ha sido **{accion}** correctamente.")


# 📌 Guardar configuraciones generales
async def guardar_configuracion(clave, valor):
    coleccion_configuracion.update_one(
        {"clave": clave},
        {"$set": {"valor": valor, "actualizado_en": datetime.now()}},
        upsert=True
    )
    return True


# 📌 Crear categoría nueva
async def crear_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes autorización.")
        return

    if not context.args:
        await update.message.reply_text(
            "⚠️ Formato correcto:\n`/crearcategoria Nombre de la Categoría`",
            parse_mode="Markdown"
        )
        return

    nombre = " ".join(context.args).strip()
    existe = coleccion_categorias.find_one({"nombre": nombre})

    if existe:
        await update.message.reply_text("❌ Esta categoría ya existe.")
        return

    coleccion_categorias.insert_one({
        "nombre": nombre,
        "descripcion": "",
        "activo": True,
        "creado_en": datetime.now()
    })

    await update.message.reply_text(f"✅ Categoría **{nombre}** creada correctamente.")


# 🚀 SINCRONIZACIÓN MEJORADA EN SEGUNDO PLANO
async def sincronizar_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sincronizando_ahora
    user_id = update.effective_user.id
    if user_id != Config.ADMIN_ID:
        await update.callback_query.answer("❌ No tienes permiso", show_alert=True)
        return

    if sincronizando_ahora:
        await update.callback_query.answer("⏳ Ya hay una sincronización en curso, espera un momento", show_alert=True)
        return

    await update.callback_query.answer()
    mensaje_proceso = await update.callback_query.edit_message_text(
        "🔄 **INICIANDO SINCRONIZACIÓN...**\nPor favor no cierres el chat, esto tardará unos segundos.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Volver al menú", callback_data="menu_admin")]
        ])
    )

    # Ejecutamos sin bloquear el bot
    async def tarea_en_segundo_plano():
        global sincronizando_ahora
        sincronizando_ahora = True
        try:
            resultado = await importar_desde_api()
            await mensaje_proceso.edit_text(
                resultado,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Volver al menú", callback_data="menu_admin")]
                ])
            )
        except Exception as error:
            print(f"❌ ERROR SINCRONIZACIÓN: {str(error)}")
            await mensaje_proceso.edit_text(
                f"❌ **ERROR DURANTE LA SINCRONIZACIÓN**\n{str(error)}\nRevisa que los datos de los paneles sean correctos.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Volver al menú", callback_data="menu_admin")]
                ])
            )
        finally:
            sincronizando_ahora = False

    asyncio.create_task(tarea_en_segundo_plano())
