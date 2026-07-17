from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
from bson import ObjectId
import os

from config import Config
from mongodb import (
    coleccion_usuarios, coleccion_categorias, coleccion_servicios,
    coleccion_facturas, coleccion_paneles, coleccion_configuracion, db
)
from interfaces.botones import menu_acciones, menu_config
from modulos.auditoria import registrar_accion
from texto import t


# 📌 Dar permisos especiales
async def dar_permisos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        return await update.message.reply_text(await t("acceso_denegado"))

    if len(context.args) < 2:
        return await update.message.reply_text("ℹ️ Uso correcto: /permisos ID_USUARIO ver,comprar,agregar")

    try:
        usuario_id = int(context.args[0])
        permisos = " ".join(context.args[1:])
    except:
        return await update.message.reply_text("❌ El ID debe ser un número válido")

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"permisos": permisos}}
    )
    await registrar_accion(admin_id, "Modificó permisos", f"Usuario {usuario_id}: {permisos}")
    await update.message.reply_text(f"✅ Permisos actualizados correctamente para el usuario {usuario_id}")


# 📌 Cambiar rol de usuario
async def cambiar_rol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        return await update.message.reply_text(await t("acceso_denegado"))

    if len(context.args) < 2:
        return await update.message.reply_text("ℹ️ Uso correcto: /rol ID_USUARIO admin | usuario | vendedor")

    try:
        usuario_id = int(context.args[0])
        nuevo_rol = context.args[1].lower()
    except:
        return await update.message.reply_text("❌ Datos incorrectos")

    roles_validos = ["usuario", "admin", "vendedor"]
    if nuevo_rol not in roles_validos:
        return await update.message.reply_text(f"Roles permitidos: {', '.join(roles_validos)}")

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"rol": nuevo_rol}}
    )
    await registrar_accion(admin_id, "Cambió rol", f"Usuario {usuario_id} → {nuevo_rol}")
    await update.message.reply_text(f"✅ Rol cambiado correctamente a «{nuevo_rol}»")


# 📌 Agregar saldo manualmente
async def recargar_saldo_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        return await update.message.reply_text(await t("acceso_denegado"))

    if len(context.args) < 2:
        return await update.message.reply_text("ℹ️ Uso correcto: /addsaldo ID_USUARIO MONTO")

    try:
        usuario_id = int(context.args[0])
        monto = float(context.args[1])
    except:
        return await update.message.reply_text("❌ Datos inválidos")

    if monto <= 0:
        return await update.message.reply_text("❌ El monto debe ser mayor a 0")

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$inc": {"saldo": monto}}
    )
    await registrar_accion(admin_id, "Agregó saldo", f"Usuario {usuario_id} + {Config.SIMBOLO}{monto}")
    await update.message.reply_text(f"✅ Se agregó {Config.SIMBOLO}{monto} al usuario {usuario_id}")

    # Avisar al usuario
    await context.bot.send_message(
        usuario_id,
        f"✅ <b>SALDO AGREGADO</b>\nEl administrador te agregó: {Config.SIMBOLO}{monto}",
        parse_mode="HTML"
    )


# 📌 Bloquear o desbloquear usuario
async def banear_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        return await update.message.reply_text(await t("acceso_denegado"))

    if not context.args:
        return await update.message.reply_text("ℹ️ Uso: /ban ID o /unban ID")

    try:
        usuario_id = int(context.args[0])
    except:
        return await update.message.reply_text("❌ ID no válido")

    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    if not usuario:
        return await update.message.reply_text("❌ Usuario no encontrado")

    estado_actual = usuario.get("baneado", False)
    nuevo_estado = not estado_actual

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"baneado": nuevo_estado}}
    )

    accion = "Bloqueó usuario" if nuevo_estado else "Desbloqueó usuario"
    texto = "✅ Usuario bloqueado correctamente" if nuevo_estado else "✅ Usuario desbloqueado correctamente"
    await registrar_accion(admin_id, accion, f"Usuario {usuario_id}")
    await update.message.reply_text(texto)


# 📌 Guardar configuración general
async def guardar_configuracion(accion: str, valor: str):
    try:
        if accion in ["monto_minimo_recarga", "porcentaje_ganancia", "limite_diario", "recompensa_referido", "aviso_saldo_minimo"]:
            valor = float(valor)

        coleccion_configuracion.update_one(
            {"clave": accion},
            {"$set": {"valor": valor}},
            upsert=True
        )
        return await t("guardado_correctamente")
    except Exception as e:
        return f"❌ Error al guardar: {str(e)}"


# 📌 Alternar modo mantenimiento
async def alternar_mantenimiento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.callback_query.answer(await t("acceso_denegado"), show_alert=True)
        return

    estado_actual = coleccion_configuracion.find_one({"clave": "modo_mantenimiento"}).get("valor", False)
    nuevo_estado = not estado_actual

    coleccion_configuracion.update_one(
        {"clave": "modo_mantenimiento"},
        {"$set": {"valor": nuevo_estado}}
    )

    await registrar_accion(admin_id, "Cambió modo mantenimiento", f"Estado: {nuevo_estado}")
    texto = await t("modo_mantenimiento") if nuevo_estado else "✅ El mantenimiento ha finalizado, todo está activo nuevamente"
    await update.callback_query.edit_message_text(texto, parse_mode="HTML", reply_markup=menu_acciones)


# 📌 Copiar configuración entre paneles
async def copiar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        return await update.message.reply_text(await t("acceso_denegado"))

    if len(context.args) < 2:
        return await update.message.reply_text("ℹ️ Uso: /copiarpanel ID_ORIGEN ID_DESTINO")

    try:
        id_origen = ObjectId(context.args[0])
        id_destino = ObjectId(context.args[1])
    except:
        return await update.message.reply_text("❌ IDs inválidos")

    origen = coleccion_paneles.find_one({"_id": id_origen})
    if not origen:
        return await update.message.reply_text("❌ El panel de origen no existe")

    coleccion_paneles.update_one(
        {"_id": id_destino},
        {"$set": {
            "porcentaje_ganancia": origen["porcentaje_ganancia"],
            "activo": origen["activo"]
        }}
    )

    await registrar_accion(admin_id, "Copió configuración de panel", f"De {id_origen} a {id_destino}")
    await update.message.reply_text("✅ Configuración copiada perfectamente")


# 📌 Crear respaldo completo
async def crear_respaldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.callback_query.answer(await t("acceso_denegado"), show_alert=True)
        return

    todas_colecciones = ["usuarios", "categorias", "servicios", "facturas", "paneles", "configuracion", "auditoria"]
    datos = {}
    for nombre in todas_colecciones:
        datos[nombre] = list(db[nombre].find({}))

    nombre_archivo = f"respaldo_voltixpro_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    from bson.json_util import dumps
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(dumps(datos, indent=2, ensure_ascii=False))

    await registrar_accion(admin_id, "Generó respaldo", nombre_archivo)
    await context.bot.send_document(update.effective_chat.id, document=open(nombre_archivo, "rb"))
    os.remove(nombre_archivo)

    await update.callback_query.edit_message_text("✅ Respaldo generado y enviado correctamente", reply_markup=menu_acciones)


# 📌 Configurar límite de gasto
async def configurar_limite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        return await update.message.reply_text(await t("acceso_denegado"))

    if not context.args:
        return await update.message.reply_text("ℹ️ Uso: /limite 0 para quitar o /limite 100")

    try:
        monto = float(context.args[0])
    except:
        return await update.message.reply_text("❌ Solo puedes usar números")

    coleccion_configuracion.update_one({"clave": "limite_diario_global"}, {"$set": {"valor": monto}})
    await registrar_accion(admin_id, "Configuró límite diario", f"{Config.SIMBOLO}{monto}")
    await update.message.reply_text(f"✅ Límite diario fijado en: {Config.SIMBOLO}{monto}")


# 📌 Ver niveles y descuentos
async def ver_niveles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    configuracion = coleccion_configuracion.find_one({"clave": "niveles"})
    niveles = configuracion.get("valor", {}) if configuracion else {}
    
    texto = "🏅 <b>NIVELES Y DESCUENTOS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for nivel, datos in niveles.items():
        texto += f"🔹 <b>{nivel.upper()}</b>\n💸 Desde: {Config.SIMBOLO}{datos['minimo_gasto']}\n📉 Descuento: {datos['descuento']}%\n\n"

    await update.callback_query.edit_message_text(texto, parse_mode="HTML", reply_markup=menu_config)


# 📌 Crear categoría nueva
async def crear_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        return await update.message.reply_text(await t("acceso_denegado"))

    if not context.args:
        return await update.message.reply_text("ℹ️ Uso: /crearcategoria Nombre | Descripción opcional")

    partes = " ".join(context.args).split("|")
    nombre = partes[0].strip()
    descripcion = partes[1].strip() if len(partes) > 1 else "Sin descripción"

    coleccion_categorias.insert_one({
        "nombre": nombre,
        "descripcion": descripcion,
        "creado_en": datetime.now()
    })

    await registrar_accion(admin_id, "Creó categoría", nombre)
    await update.message.reply_text(f"✅ Categoría «{nombre}» creada exitosamente")


# 📌 Sincronizar servicios
async def sincronizar_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.callback_query.answer(await t("acceso_denegado"), show_alert=True)
        return

    await update.callback_query.edit_message_text("🔄 Sincronizando servicios, por favor espera unos segundos...")
    from api.importar_servicios import importar_desde_api
    resultado = await importar_desde_api()

    await registrar_accion(admin_id, "Sincronizó servicios", resultado)
    await update.callback_query.edit_message_text(f"✅ {resultado}", reply_markup=menu_acciones)
