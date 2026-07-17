from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# 📌 Verificación de suscripción
menu_suscripcion = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔗 IR AL CANAL", url="https://t.me/Voltix_Pro")],
    [InlineKeyboardButton("✅ YA ME SUSCRIBÍ", callback_data="verificar_suscripcion")]
])

# 📌 Menú Principal - Diseño limpio 2 columnas
menu_principal = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛒 Tienda", callback_data="menu_tienda"),
     InlineKeyboardButton("🔍 Buscar", callback_data="menu_buscar")],
    [InlineKeyboardButton("⭐ Favoritos", callback_data="menu_favoritos"),
     InlineKeyboardButton("🛒 Carrito", callback_data="menu_carrito")],
    [InlineKeyboardButton("💰 Recargar", callback_data="menu_recarga"),
     InlineKeyboardButton("👤 Mi Perfil", callback_data="menu_perfil")],
    [InlineKeyboardButton("📦 Mis Pedidos", callback_data="menu_pedidos")],
    [InlineKeyboardButton("⚙️ Administración", callback_data="menu_admin")]
])

# 📌 Menú Principal Administrador
menu_admin = InlineKeyboardMarkup([
    [InlineKeyboardButton("👥 Usuarios", callback_data="ad_usuarios"),
     InlineKeyboardButton("📂 Categorías", callback_data="ad_categorias")],
    [InlineKeyboardButton("🔌 Paneles", callback_data="ad_paneles"),
     InlineKeyboardButton("⚙️ Configuración", callback_data="ad_config")],
    [InlineKeyboardButton("📋 Acciones Rápidas", callback_data="ad_acciones")],
    [InlineKeyboardButton("🔙 Volver al inicio", callback_data="ad_salir")]
])

# 📌 Gestión de Paneles
menu_panel = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Agregar nuevo", callback_data="pan_agregar")],
    [InlineKeyboardButton("📋 Ver lista con ID", callback_data="pan_ver_ids")],
    [InlineKeyboardButton("📋 Copiar configuración", callback_data="pan_copiar")],
    [InlineKeyboardButton("✏️ Editar", callback_data="pan_editar"),
     InlineKeyboardButton("🗑️ Eliminar", callback_data="pan_eliminar")],
    [InlineKeyboardButton("🔙 Volver", callback_data="menu_admin")]
])

# 📌 Acciones Rápidas
menu_acciones = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Aviso a todos", callback_data="acc_aviso")],
    [InlineKeyboardButton("📜 Historial", callback_data="acc_historial"),
     InlineKeyboardButton("💾 Respaldo", callback_data="acc_respaldo")],
    [InlineKeyboardButton("🚧 Mantenimiento", callback_data="acc_mantenimiento"),
     InlineKeyboardButton("📊 Estadísticas", callback_data="acc_stats")],
    [InlineKeyboardButton("🔄 Sincronizar", callback_data="acc_reiniciar")],
    [InlineKeyboardButton("🔙 Volver", callback_data="menu_admin")]
])

# 📌 Configuración General
menu_config = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏅 Niveles y descuentos", callback_data="conf_niveles")],
    [InlineKeyboardButton("🚧 Límite de gasto", callback_data="conf_limite"),
     InlineKeyboardButton("🎁 Recompensa referidos", callback_data="conf_referido")],
    [InlineKeyboardButton("🔔 Aviso saldo bajo", callback_data="conf_saldobajo"),
     InlineKeyboardButton("🔒 Seguridad", callback_data="conf_seguridad")],
    [InlineKeyboardButton("🎨 Personalizar marca", callback_data="conf_marca")],
    [InlineKeyboardButton("🔙 Volver", callback_data="menu_admin")]
])

# 📌 Gestión de Usuarios
menu_usuarios = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 Buscar usuario", callback_data="usr_buscar")],
    [InlineKeyboardButton("➕ Agregar saldo", callback_data="usr_sumar"),
     InlineKeyboardButton("🗑️ Quitar saldo", callback_data="usr_quitar")],
    [InlineKeyboardButton("🚫 Bloquear/Desbloquear", callback_data="usr_bloquear")],
    [InlineKeyboardButton("🔙 Volver", callback_data="menu_admin")]
])

# 📌 Gestión de Categorías
menu_categorias = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Crear categoría", callback_data="cat_crear")],
    [InlineKeyboardButton("✏️ Editar", callback_data="cat_editar"),
     InlineKeyboardButton("🗑️ Eliminar", callback_data="cat_eliminar")],
    [InlineKeyboardButton("🔙 Volver", callback_data="menu_admin")]
])

# 📌 Perfil de usuario
menu_perfil = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎁 Mis referidos", callback_data="ref_menu"),
     InlineKeyboardButton("💱 Cambiar moneda", callback_data="conf_moneda")],
    [InlineKeyboardButton("❓ Ayuda y FAQ", callback_data="faq_menu")],
    [InlineKeyboardButton("🔙 Menú principal", callback_data="ad_salir")]
])

# 📌 Acciones Carrito
botones_carrito = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Pagar todo", callback_data="carrito_pagar")],
    [InlineKeyboardButton("🗑️ Vaciar carrito", callback_data="carrito_vaciar")],
    [InlineKeyboardButton("🔙 Volver a tienda", callback_data="menu_tienda")]
])

# 📌 Confirmación de pago
botones_factura = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Ya realicé el pago", callback_data="pagado_confirmar")],
    [InlineKeyboardButton("❌ Cancelar", callback_data="pagado_cancelar")]
])
