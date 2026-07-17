from telegram import ChatMember
from config import Config
from mongodb import coleccion_usuarios

async def verificar_suscripcion(update, context):
    user = update.effective_user
    if not user:
        return False

    # Verificar si el usuario está bloqueado
    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    if usuario and usuario.get("baneado", False):
        await update.message.reply_text("❌ Tu acceso ha sido bloqueado por el administrador.")
        return False

    # Preparar el identificador del canal
    canal = str(Config.CANAL_OBLIGATORIO).strip()
    # Si no es ID ni tiene @, se lo agregamos automáticamente
    if not canal.startswith("-100") and not canal.startswith("@"):
        canal = "@" + canal

    try:
        # Revisar el estado del usuario en el canal
        miembro = await context.bot.get_chat_member(chat_id=canal, user_id=user.id)
        estados_validos = [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER
        ]
        return miembro.status in estados_validos

    except Exception as error:
        # Solo para depurar en los registros, no lo ve el usuario
        print(f"⚠️ Error al verificar canal: {str(error)} | Canal usado: {canal}")
        return False
