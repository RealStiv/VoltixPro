from telegram import ChatMember
from config import Config
from mongodb import coleccion_usuarios

async def verificar_suscripcion(update, context):
    user = update.effective_user
    if not user:
        return False

    # Revisa si está bloqueado primero
    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    if usuario and usuario.get("baneado", False):
        await update.message.reply_text("❌ Tu acceso ha sido bloqueado por el administrador")
        return False

    # Verifica suscripción al canal
    try:
        canal_id = f"@{Config.CANAL_OBLIGATORIO.strip()}"
        miembro = await context.bot.get_chat_member(chat_id=canal_id, user_id=user.id)
        # Estados que SÍ permiten entrada
        estados_validos = [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER
        ]
        return miembro.status in estados_validos
    except Exception as error:
        print(f"Error al verificar: {error}")
        return False
