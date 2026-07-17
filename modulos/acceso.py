from telegram import ChatMember
from config import Config
from mongodb import coleccion_usuarios

async def verificar_suscripcion(update, context):
    user = update.effective_user
    if not user:
        return False

    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    if usuario and usuario.get("baneado", False):
        await update.message.reply_text("❌ Tu acceso ha sido bloqueado por el administrador.")
        return False

    canal = Config.CANAL_OBLIGATORIO.strip()
    if not canal.startswith("@"):
        canal = "@" + canal

    try:
        miembro = await context.bot.get_chat_member(chat_id=canal, user_id=user.id)
        return miembro.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        print(f"Error al verificar: {e}")
        return False
