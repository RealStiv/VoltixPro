from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# 📌 Verificación de suscripción
menu_suscripcion = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔗 IR AL CANAL OFICIAL", url="https://t.me/Voltix_Pro")],
    [InlineKeyboardButton("✅ YA ME SUSCRIBÍ", callback_data="verificar_sus")]
])

# 📌 Menú principal usuarios
menu_principal = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛒 Tienda SMM", callback_data="menu_tienda")],
    [InlineKeyboardButton("💰 Recargar Saldo", callback_data="menu_recarga")],
    [InlineKeyboardButton("👤 Mi Perfil", callback_data="menu_perfil")],
    [InlineKeyboardButton("📦 Mis Pedidos", callback_data="menu_pedidos")],
    [InlineKeyboardButton("🔧 Herramientas", callback_data="menu_herramientas")],
    [InlineKeyboardButton("⚙️ Admin Total", callback_data="menu_admin")]
])

# 📌 Menú principal Administrador
menu_admin = InlineKeyboardMarkup([
    [InlineKeyboardButton("👥 Gestión de Usuarios", callback_data="ad_usuarios")],
    [InlineKeyboardButton("📂 Gestión de Categorías", callback_data="ad_categorias")],
    [InlineKeyboardButton("➕ Gestión de Paneles", callback_data="ad_panel")],
    [InlineKeyboardButton("⚙️ Configuración General", callback_data="ad_config")],
    [InlineKeyboardButton("📊 Acciones Rápidas", callback_data="acc_menu")],
    [InlineKeyboardButton("🔙 Volver al inicio", callback_data="ad_salir")]
])

# 📌 Gestión de Paneles
menu_panel = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Agregar nuevo", callback_data="pan_agregar")],
    [InlineKeyboardButton("📋 Ver activos", callback_data="pan_lista")],
    [InlineKeyboardButton("✏️ Editar", callback_data="pan_editar")],
    [InlineKeyboardButton("❌ Eliminar", callback_data="pan_eliminar")],
    [InlineKeyboardButton("🔙 Volver al menú admin", callback_data="menu_admin")]
])

# 📌 Gestión de Usuarios
menu_usuarios = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 Buscar usuario", callback_data="usr_buscar")],
    [InlineKeyboardButton("➕ Agregar saldo", callback_data="usr_sumar")],
    [InlineKeyboardButton("➖ Quitar saldo", callback_data="usr_restar")],
    [InlineKeyboardButton("🚫 Bloquear", callback_data="usr_bloquear")],
    [InlineKeyboardButton("✅ Desbloquear", callback_data="usr_desbloquear")],
    [InlineKeyboardButton("🔙 Volver al menú admin", callback_data="menu_admin")]
])

# 📌 Gestión de Categorías
menu_categorias = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ Crear categoría", callback_data="cat_crear")],
    [InlineKeyboardButton("✏️ Editar categoría", callback_data="cat_editar")],
    [InlineKeyboardButton("❌ Eliminar categoría", callback_data="cat_eliminar")],
    [InlineKeyboardButton("🔙 Volver al menú admin", callback_data="menu_admin")]
])

# 📌 Configuración General
menu_config = InlineKeyboardMarkup([
    [InlineKeyboardButton("💵 Monto mínimo recarga", callback_data="conf_minimo")],
    [InlineKeyboardButton("📢 Canal obligatorio", callback_data="conf_canal")],
    [InlineKeyboardButton("🔑 Datos de pago", callback_data="conf_pago")],
    [InlineKeyboardButton("📈 % Ganancia por venta", callback_data="conf_margen")],
    [InlineKeyboardButton("🔙 Volver al menú admin", callback_data="menu_admin")]
])

# 📌 Acciones Rápidas
menu_acciones = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Enviar aviso a todos", callback_data="acc_aviso")],
    [InlineKeyboardButton("📊 Ver estadísticas", callback_data="acc_stats")],
    [InlineKeyboardButton("🔄 Sincronizar servicios", callback_data="acc_reiniciar")],
    [InlineKeyboardButton("🔙 Volver al menú admin", callback_data="menu_admin")]
])

# 📌 Botones para facturas
botones_factura = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Ya realicé el pago", callback_data="pagado")],
    [InlineKeyboardButton("❌ Cancelar", callback_data="cancelar_pago")]
])

botones_lista_facturas = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 Volver a recargas", callback_data="menu_recarga")]
])
