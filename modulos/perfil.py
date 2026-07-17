from telegram import Update
from telegram.ext import ContextTypes
from mongodb import coleccion_usuarios, coleccion_pedidos, coleccion_facturas
from texto import t
from config import Config

async def mostrar_perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    usuario = coleccion_usuarios.find_one({"user_id": user.id})
    
    if not usuario:
        await update.message.reply_text("❌ No se encontró tu perfil, usa /start primero")
        return
    
    # Datos adicionales
    total_pedidos = coleccion_pedidos.count_documents({"user_id": user.id})
    total_facturas = coleccion_facturas.count_documents({"user_id": user.id})
    
    await update.message.reply_text(
        t("perfil",
            user_id=user.id,
            nombre=user.full_name,
            saldo=usuario.get("saldo", 0.0),
            pedidos=total_pedidos,
            facturas=total_facturas,
            claves=usuario.get("claves_api", "Sin claves asignadas"),
            rol=usuario.get("rol", "usuario"),
            permisos=usuario.get("permisos", "ver,comprar"),
            fecha=usuario.get("creado_en", datetime.now()).strftime("%d/%m/%Y")
        ),
        parse_mode="HTML"
    )
