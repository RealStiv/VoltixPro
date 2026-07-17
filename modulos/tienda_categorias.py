from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from mongodb import coleccion_categorias, coleccion_servicios


async def mostrar_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Trae solo categorías activas, ordenadas alfabéticamente
    categorias = list(coleccion_categorias.find({"activo": True}).sort("nombre", 1))

    if not categorias:
        await update.callback_query.edit_message_text(
            "❌ Aún no hay categorías disponibles.\nPrimero sincroniza los servicios desde el panel de administrador.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Volver al menú", callback_data="ad_salir")]
            ])
        )
        return

    filas_botones = []

    for categoria in categorias:
        # Cuenta solo servicios activos que pertenecen a esta categoría
        cantidad_servicios = coleccion_servicios.count_documents({
            "categoria_id": categoria["_id"],
            "activo": True
        })

        filas_botones.append([
            InlineKeyboardButton(
                f"{categoria['nombre']} 💀 ({cantidad_servicios})",
                callback_data=f"ver_cat_{categoria['nombre']}"
            )
        ])

    # Agregamos el botón de volver al final
    filas_botones.append([
        InlineKeyboardButton("🔙 VOLVER AL MENÚ PRINCIPAL", callback_data="ad_salir")
    ])

    teclado = InlineKeyboardMarkup(filas_botones)

    await update.callback_query.edit_message_text(
        "🛒 **TIENDA DE SERVICIOS**\nSelecciona una categoría para ver los servicios disponibles:",
        parse_mode="Markdown",
        reply_markup=teclado
    )


async def mostrar_servicios(update: Update, context: ContextTypes.DEFAULT_TYPE, nombre_categoria: str):
    categoria = coleccion_categorias.find_one({"nombre": nombre_categoria, "activo": True})

    if not categoria:
        await update.callback_query.edit_message_text(
            "❌ Esta categoría ya no existe o fue desactivada.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Ver todas las categorías", callback_data="menu_tienda")]
            ])
        )
        return

    servicios = list(coleccion_servicios.find({
        "categoria_id": categoria["_id"],
        "activo": True
    }).sort("nombre", 1))

    if not servicios:
        texto = f"📂 **{nombre_categoria}**\n\n⚠️ No hay servicios disponibles en esta categoría por ahora."
    else:
        texto = f"📂 **{nombre_categoria}**\n\n"
        for s in servicios[:15]:  # Mostramos máximo 15 por mensaje para no saturar
            texto += f"• {s['nombre']}\n💵 ${s['precio_venta']:.2f} / 1000\n\n"
        if len(servicios) > 15:
            texto += f"... y {len(servicios)-15} servicios más"

    botones = []
    for s in servicios[:8]:
        botones.append([InlineKeyboardButton(f"🛒 {s['nombre'][:25]}...", callback_data=f"serv_{s['id_api']}")])

    botones.append([InlineKeyboardButton("🔙 Volver a categorías", callback_data="menu_tienda")])

    await update.callback_query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(botones)
    )
