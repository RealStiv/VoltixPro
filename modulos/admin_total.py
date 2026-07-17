from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from mongodb import coleccion_usuarios, coleccion_servicios, coleccion_categorias, coleccion_configuracion
from api.importar_servicios import importar_desde_api
from datetime import datetime

async def dar_permisos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("✅ Uso correcto: /permisos ID_USUARIO permiso1,permiso2,permiso3")
        return
    
    user_id = int(context.args[0])
    permisos = " ".join(context.args[1:])
    
    coleccion_usuarios.update_one({"user_id": user_id}, {"$set": {"permisos": permisos}}, upsert=True)
    await update.message.reply_text(f"✅ Permisos actualizados al usuario <code>{user_id}</code>", parse_mode="HTML")

async def cambiar_rol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("✅ Uso correcto: /rol ID_USUARIO usuario/vip/moderador/admin")
        return
    
    user_id = int(context.args[0])
    rol = context.args[1].lower()
    roles_validos = ["usuario", "vip", "moderador", "admin"]
    
    if rol not in roles_validos:
        await update.message.reply_text("❌ Rol no válido. Usa: usuario, vip, moderador o admin")
        return
    
    coleccion_usuarios.update_one({"user_id": user_id}, {"$set": {"rol": rol}}, upsert=True)
    await update.message.reply_text(f"✅ Rol cambiado a <b>{rol}</b> para el usuario {user_id}", parse_mode="HTML")

async def recargar_saldo_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("✅ Uso correcto: /addsaldo ID_USUARIO MONTO")
        return
    
    try:
        user_id = int(context.args[0])
        monto = float(context.args[1])
    except:
        await update.message.reply_text("❌ Valores incorrectos")
        return
    
    coleccion_usuarios.update_one({"user_id": user_id}, {"$inc": {"saldo": monto}}, upsert=True)
    await update.message.reply_text(f"✅ Se agregó {Config.SIMBOLO}{monto:.2f} al usuario {user_id}")
    try:
        await context.bot.send_message(user_id, f"🎉 <b>NOTIFICACIÓN</b>\nSe agregó {Config.SIMBOLO}{monto:.2f} a tu saldo por parte del administrador", parse_mode="HTML")
    except:
        await update.message.reply_text(f"⚠️ No se pudo notificar al usuario, quizás no ha iniciado el bot")

async def banear_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return
    
    if not context.args:
        await update.message.reply_text("✅ Uso: /ban ID_USUARIO o /unban ID_USUARIO")
        return
    
    user_id = int(context.args[0])
    accion = update.message.text.split()[0]
    estado = True if accion == "/ban" else False
    
    coleccion_usuarios.update_one({"user_id": user_id}, {"$set": {"baneado": estado}}, upsert=True)
    texto = "bloqueado" if estado else "desbloqueado"
    await update.message.reply_text(f"✅ Usuario {user_id} {texto} correctamente")

async def crear_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return
    
    nombre = " ".join(context.args).strip()
    if not nombre:
        await update.message.reply_text("✅ Uso: /crearcategoria NOMBRE_DE_LA_CATEGORIA")
        return
    
    existe = coleccion_categorias.find_one({"nombre": nombre})
    if existe:
        await update.message.reply_text("❌ Esa categoría ya existe")
        return
    
    coleccion_categorias.insert_one({"nombre": nombre, "activo": True, "creado_en": datetime.now()})
    await update.message.reply_text(f"✅ Categoría <b>{nombre}</b> creada correctamente", parse_mode="HTML")

async def sincronizar_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return
    
    mensaje = await update.message.reply_text("🔄 Actualizando servicios desde los paneles...")
    resultado = await importar_desde_api()
    await mensaje.edit_text(resultado, parse_mode="HTML")

async def guardar_configuracion(opcion, valor):
    config = coleccion_configuracion.find_one({"tipo": "general"})
    if not config:
        coleccion_configuracion.insert_one({"tipo": "general"})
    coleccion_configuracion.update_one(
        {"tipo": "general"},
        {"$set": {opcion: valor, "actualizado_en": datetime.now()}},
        upsert=True
    )
    return f"✅ **CONFIGURACIÓN GUARDADA CORRECTAMENTE**\nAhora está activo: `{valor}`"
