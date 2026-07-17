from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from mongodb import coleccion_usuarios, coleccion_servicios, coleccion_categorias
from modulos.niveles_limites import calcular_nivel_usuario

# 🔍 Buscador inteligente
async def buscar_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🔎 Escribe: `/buscar seguidores instagram`")
        return

    busqueda = " ".join(context.args).lower()
    resultados = list(coleccion_servicios.find({
        "$or": [
            {"nombre": {"$regex": busqueda, "$options": "i"}},
            {"categoria_nombre": {"$regex": busqueda, "$options": "i"}}
        ],
        "activo": True
    }).limit(20))

    if not resultados:
        texto = "❌ No se encontraron servicios con ese nombre."
    else:
        texto = f"🔎 RESULTADOS PARA: «{busqueda}»\n\n"
        botones = []
        for s in resultados:
            texto += f"• {s['nombre']} - ${s['precio_venta']:.2f}\n"
            botones.append([InlineKeyboardButton(f"🛒 {s['nombre'][:28]}...", callback_data=f"serv_{s['id_api']}")])
        
        botones.append([InlineKeyboardButton("🔙 Volver a tienda", callback_data="menu_tienda")])
        await update.message.reply_text(texto, reply_markup=InlineKeyboardMarkup(botones))
        return

    await update.message.reply_text(texto)

# ⭐ Sistema de favoritos
async def agregar_favorito(usuario_id: int, id_api: str):
    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    favoritos = usuario.get("favoritos", [])
    if id_api not in favoritos:
        favoritos.append(id_api)
        coleccion_usuarios.update_one({"user_id": usuario_id}, {"$set": {"favoritos": favoritos}})

async def ver_favoritos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = coleccion_usuarios.find_one({"user_id": update.effective_user.id})
    favoritos_ids = usuario.get("favoritos", [])

    if not favoritos_ids:
        texto = "⭐ Aún no tienes servicios favoritos.\nAgrega desde la página de cada servicio."
    else:
        servicios = list(coleccion_servicios.find({"id_api": {"$in": favoritos_ids}, "activo": True}))
        texto = "⭐ TUS SERVICIOS FAVORITOS:\n\n"
        botones = []
        for s in servicios:
            texto += f"• {s['nombre']} - ${s['precio_venta']:.2f}\n"
            botones.append([InlineKeyboardButton(f"🛒 {s['nombre'][:28]}...", callback_data=f"serv_{s['id_api']}")])
        botones.append([InlineKeyboardButton("🔙 Volver", callback_data="menu_tienda")])
        await update.callback_query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(botones))
        return

    await update.callback_query.edit_message_text(texto)

# 🛒 Carrito de compras
async def agregar_carrito(usuario_id: int, id_api: str, cantidad: int):
    nivel, descuento = await calcular_nivel_usuario(usuario_id)
    servicio = coleccion_servicios.find_one({"id_api": id_api})
    precio_final = round(servicio["precio_venta"] * (1 - descuento/100), 2)
    subtotal = precio_final * cantidad

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$addToSet": {"carrito": {
            "id_api": id_api,
            "nombre": servicio["nombre"],
            "cantidad": cantidad,
            "precio_unitario": precio_final,
            "subtotal": subtotal
        }}}
    )

async def ver_carrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = coleccion_usuarios.find_one({"user_id": update.effective_user.id})
    carrito = usuario.get("carrito", [])

    if not carrito:
        texto = "🛒 Tu carrito está vacío por ahora."
    else:
        total = sum(item["subtotal"] for item in carrito)
        texto = "🛒 TU CARRITO DE COMPRAS:\n\n"
        for item in carrito:
            texto += f"• {item['nombre']}\n   Cant: {item['cantidad']} | ${item['subtotal']:.2f}\n"
        texto += f"\n💸 TOTAL A PAGAR: ${total:.2f}"

        botones = [
            [InlineKeyboardButton("✅ Pagar todo", callback_data="carrito_pagar")],
            [InlineKeyboardButton("🗑️ Vaciar carrito", callback_data="carrito_vaciar")],
            [InlineKeyboardButton("🔙 Volver", callback_data="menu_tienda")]
        ]
        await update.callback_query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(botones))
        return

    await update.callback_query.edit_message_text(texto)
