from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from bson import ObjectId
import json
from bson.json_util import dumps
from config import Config
from mongodb import (
    coleccion_usuarios, coleccion_categorias, coleccion_servicios,
    coleccion_facturas, coleccion_paneles, coleccion_configuracion, db
)
from interfaces.botones import menu_acciones, menu_config
from modulos.auditoria import registrar_accion
from modulos.niveles_limites import calcular_nivel_usuario
from api.gestor_paneles import coleccion_paneles


# 📌 Dar permisos especiales
async def dar_permisos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso: /permisos ID_USUARIO ver,comprar,agregar")
        return

    try:
        usuario_id = int(context.args[0])
        permisos = " ".join(context.args[1:])
    except:
        return await update.message.reply_text("❌ ID debe ser número")

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"permisos": permisos}}
    )
    await registrar_accion(admin_id, "Modificó permisos", f"Usuario {usuario_id}: {permisos}")
    await update.message.reply_text(f"✅ Permisos actualizados para {usuario_id}")


# 📌 Cambiar rol de usuario
async def cambiar_rol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso: /rol ID_USUARIO admin | usuario | vendedor")
        return

    try:
        usuario_id = int(context.args[0])
        nuevo_rol = context.args[1].lower()
    except:
        return await update.message.reply_text("❌ Datos incorrectos")

    roles_validos = ["usuario", "admin", "vendedor"]
    if nuevo_rol not in roles_validos:
        return await update.message.reply_text(f"Roles válidos: {', '.join(roles_validos)}")

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"rol": nuevo_rol}}
    )
    await registrar_accion(admin_id, "Cambió rol", f"Usuario {usuario_id} → {nuevo_rol}")
    await update.message.reply_text(f"✅ Rol actualizado correctamente")


# 📌 Agregar saldo manualmente
async def recargar_saldo_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso: /addsaldo ID_USUARIO MONTO")
        return

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
    await registrar_accion(admin_id, "Agregó saldo", f"Usuario {usuario_id} + ${monto}")
    await update.message.reply_text(f"✅ Se agregó ${monto} al usuario {usuario_id}")

    # Avisar al usuario
    await context.bot.send_message(
        usuario_id,
        f"✅ **SALDO AGREGADO**\nTe han agregado ${monto} a tu cuenta",
        parse_mode="Markdown"
    )


# 📌 Bloquear o desbloquear usuario
async def banear_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if not context.args:
        await update.message.reply_text("Uso: /ban ID o /unban ID")
        return

    try:
        usuario_id = int(context.args[0])
    except:
        return await update.message.reply_text("❌ ID inválido")

    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    if not usuario:
        return await update.message.reply_text("❌ Usuario no existe")

    estado_actual = usuario.get("baneado", False)
    nuevo_estado = not estado_actual

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"baneado": nuevo_estado}}
    )

    accion = "Bloqueó usuario" if nuevo_estado else "Desbloqueó usuario"
    await registrar_accion(admin_id, accion, f"Usuario {usuario_id}")
    texto = "✅ Usuario bloqueado" if nuevo_estado else "✅ Usuario desbloqueado"
    await update.message.reply_text(texto)


# 📌 Guardar configuración general
async def guardar_configuracion(accion: str, valor: str):
    try:
        if accion == "monto_minimo_recarga":
            valor = float(valor)
        elif accion == "porcentaje_ganancia":
            valor = float(valor)
        elif accion == "limite_diario":
            valor = float(valor)
        elif accion == "recompensa_referido":
            valor = float(valor)
        elif accion == "aviso_saldo_minimo":
            valor = float(valor)

        coleccion_configuracion.update_one(
            {"clave": accion},
            {"$set": {"valor": valor}},
            upsert=True
        )
        return "✅ Configuración guardada correctamente ❤️"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# 📌 Alternar modo mantenimiento
async def alternar_mantenimiento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.callback_query.answer("❌ Sin permiso", show_alert=True)
        return

    estado_actual = coleccion_configuracion.find_one({"clave": "modo_mantenimiento"})["valor"]
    nuevo_estado = not estado_actual

    coleccion_configuracion.update_one(
        {"clave": "modo_mantenimiento"},
        {"$set": {"valor": nuevo_estado}}
    )

    await registrar_accion(admin_id, "Cambió modo mantenimiento", f"Quedó en: {nuevo_estado}")
    texto = "🚧 **MODO MANTENIMIENTO ACTIVO**\nLos usuarios no pueden realizar compras ni recargas" if nuevo_estado else "✅ **Mantenimiento finalizado**\nTodo volvió a la normalidad"

    await update.callback_query.edit_message_text(texto, parse_mode="Markdown", reply_markup=menu_acciones)


# 📌 Copiar configuración entre paneles
async def copiar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso: /copiarpanel ID_ORIGEN ID_DESTINO")
        return

    try:
        id_origen = ObjectId(context.args[0])
        id_destino = ObjectId(context.args[1])
    except:
        return await update.message.reply_text("❌ IDs inválidos")

    origen = coleccion_paneles.find_one({"_id": id_origen})
    if not origen:
        return await update.message.reply_text("❌ Panel de origen no existe")

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
        await update.callback_query.answer("❌ Sin permiso", show_alert=True)
        return

    todas_colecciones = ["usuarios", "categorias", "servicios", "facturas", "paneles", "configuracion", "auditoria"]
    datos = {}
    for nombre in todas_colecciones:
        datos[nombre] = list(db[nombre].find({}))

    nombre_archivo = f"respaldo_voltixpro_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(dumps(datos, indent=2, ensure_ascii=False))

    await registrar_accion(admin_id, "Generó respaldo", nombre_archivo)
    await context.bot.send_document(update.effective_chat.id, document=open(nombre_archivo, "rb"))
    import os
    os.remove(nombre_archivo)

    await update.callback_query.edit_message_text("✅ Respaldo generado y enviado", reply_markup=menu_acciones)


# 📌 Configurar límite de gasto
async def configurar_limite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if not context.args:
        await update.message.reply_text("Uso: /limite 0 para quitar o /limite 100")
        return

    try:
        monto = float(context.args[0])
    except:
        return await update.message.reply_text("❌ Solo números")

    coleccion_configuracion.update_one({"clave": "limite_diario_global"}, {"$set": {"valor": monto}})
    await registrar_accion(admin_id, "Configuró límite diario", f"Valor: ${monto}")
    await update.message.reply_text(f"✅ Límite diario fijado en ${monto}")


# 📌 Ver niveles actuales
async def ver_niveles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    niveles = coleccion_configuracion.find_one({"clave": "niveles"})["valor"]
    texto = "🏅 **CONFIGURACIÓN DE NIVELES**\n\n"
    for nivel, datos in niveles.items():
        texto += f"🔹 {nivel.upper()}\n💸 Gasto mínimo: ${datos['minimo_gasto']}\n📉 Descuento: {datos['descuento']}%\n\n"

    await update.callback_query.edit_message_text(texto, parse_mode="Markdown", reply_markup=menu_config)


# 📌 Crear categoría
async def crear_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.message.reply_text("❌ Sin permiso")
        return

    if not context.args:
        await update.message.reply_text("Uso: /crearcategoria NOMBRE | DESCRIPCIÓN")
        return

    partes = " ".join(context.args).split("|")
    nombre = partes[0].strip()
    descripcion = partes[1].strip() if len(partes) > 1 else "Sin descripción"

    coleccion_categorias.insert_one({
        "nombre": nombre,
        "descripcion": descripcion,
        "creado": datetime.now()
    })

    await registrar_accion(admin_id, "Creó categoría", nombre)
    await update.message.reply_text(f"✅ Categoría «{nombre}» creada")


# 📌 Sincronizar servicios
async def sincronizar_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if admin_id != Config.ADMIN_ID:
        await update.callback_query.answer("❌ Sin permiso", show_alert=True)
        return

    await update.callback_query.edit_message_text("🔄 Sincronizando servicios, por favor espera...")
    from api.importar_servicios import importar_desde_api
    resultado = await importar_desde_api()

    await registrar_accion(admin_id, "Sincronizó servicios", resultado)
    await update.callback_query.edit_message_text(f"✅ {resultado}", reply_markup=menu_acciones)
