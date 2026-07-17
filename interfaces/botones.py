from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# 📌 Verificación de suscripción - Enlace exacto de tu canal
menu_suscripcion = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔗 IR AL CANAL", url="https://t.me/Voltix_Pro")],
    [InlineKeyboardButton("✅ YA ME SUSCRIBÍ", callback_data="verificar_suscripcion")]
])

# 📌 MENÚ PRINCIPAL ACTUALIZADO - 2 columnas, limpio y sin elementos sobrantes
menu_principal = InlineKeyboardMarkup([
    [InlineKeyboardButton("🛍️ VER TIENDA", callback_data="menu_tienda"),
     InlineKeyboardButton("➕ RECARGAR SALDO", callback_data="menu_recarga")],
    [InlineKeyboardButton("👤 MI PERFIL", callback_data="menu_perfil"),
     InlineKeyboardButton("🛠️ HERRAMIENTAS", callback_data="menu_buscar")],
    [InlineKeyboardButton("❓ AYUDA / FAQ", callback_data="faq")],
    [InlineKeyboardButton("⚙️ PANEL ADMINISTRADOR", callback_data="menu_admin")]
])

# 📌 MENÚ DENTRO DE MI PERFIL - Aquí están ahora todos los que pediste mover
menu_perfil = InlineKeyboardMarkup([
    [InlineKeyboardButton("📦 MIS PEDIDOS", callback_data="menu_pedidos"),
     InlineKeyboardButton("📌 MIS FAVORITOS", callback_data="menu_favoritos")],
    [InlineKeyboardButton("🛒 CARRITO DE COMPRAS", callback_data="menu_carrito")],
    [InlineKeyboardButton("🎁 MIS REFERIDOS", callback_data="ref_menu"),
     InlineKeyboardButton("💱 CAMBIAR MONEDA", callback_data="conf_moneda")],
    [InlineKeyboardButton("🔙 VOLVER AL INICIO", callback_data="ad_salir")]
])

# 📌 Menú Principal Administrador
menu_admin = InlineKeyboardMarkup([
    [InlineKeyboardButton("👥 GESTIÓN DE USUARIOS", callback_data="ad_usuarios"),
     InlineKeyboardButton("📂 CATEGORÍAS Y SERVICIOS", callback_data="ad_categorias")],
    [InlineKeyboardButton("🔌 GESTIÓN DE PANELES", callback_data="ad_paneles"),
     InlineKeyboardButton("⚙️ CONFIGURACIÓN GENERAL", callback_data="ad_config")],
    [InlineKeyboardButton("📋 ACCIONES RÁPIDAS", callback_data="ad_acciones")],
    [InlineKeyboardButton("🔙 VOLVER AL INICIO", callback_data="ad_salir")]
])

# 📌 Gestión de Paneles
menu_panel = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ AGREGAR NUEVO", callback_data="pan_agregar")],
    [InlineKeyboardButton("📋 VER LISTA CON ID", callback_data="pan_ver_ids")],
    [InlineKeyboardButton("📋 COPIAR CONFIGURACIÓN", callback_data="pan_copiar")],
    [InlineKeyboardButton("✏️ EDITAR", callback_data="pan_editar"),
     InlineKeyboardButton("🗑️ ELIMINAR", callback_data="pan_eliminar")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="menu_admin")]
])

# 📌 Acciones Rápidas
menu_acciones = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 AVISO A TODOS", callback_data="acc_aviso")],
    [InlineKeyboardButton("📜 HISTORIAL COMPLETO", callback_data="acc_historial"),
     InlineKeyboardButton("💾 CREAR RESPALDO", callback_data="acc_respaldo")],
    [InlineKeyboardButton("🚧 MODO MANTENIMIENTO", callback_data="acc_mantenimiento"),
     InlineKeyboardButton("📊 ESTADÍSTICAS", callback_data="acc_stats")],
    [InlineKeyboardButton("🔄 SINCRONIZAR SERVICIOS", callback_data="acc_reiniciar")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="menu_admin")]
])

# 📌 Configuración General
menu_config = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏅 NIVELES Y DESCUENTOS", callback_data="conf_niveles")],
    [InlineKeyboardButton("🚧 LÍMITE DE GASTO DIARIO", callback_data="conf_limite"),
     InlineKeyboardButton("🎁 RECOMPENSA POR REFERIDOS", callback_data="conf_referido")],
    [InlineKeyboardButton("🔔 AVISO DE SALDO BAJO", callback_data="conf_saldobajo")],
    [InlineKeyboardButton("🎨 PERSONALIZAR TU MARCA", callback_data="conf_marca")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="menu_admin")]
])

# 📌 Gestión de Usuarios
menu_usuarios = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 BUSCAR USUARIO", callback_data="usr_buscar")],
    [InlineKeyboardButton("➕ AGREGAR SALDO", callback_data="usr_sumar"),
     InlineKeyboardButton("🗑️ QUITAR SALDO", callback_data="usr_quitar")],
    [InlineKeyboardButton("🚫 BLOQUEAR / DESBLOQUEAR", callback_data="usr_bloquear")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="menu_admin")]
])

# 📌 Gestión de Categorías
menu_categorias = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ CREAR CATEGORÍA", callback_data="cat_crear")],
    [InlineKeyboardButton("✏️ EDITAR", callback_data="cat_editar"),
     InlineKeyboardButton("🗑️ ELIMINAR", callback_data="cat_eliminar")],
    [InlineKeyboardButton("🔙 VOLVER", callback_data="menu_admin")]
])

# 📌 Acciones Carrito
botones_carrito = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ PAGAR TODO", callback_data="carrito_pagar")],
    [InlineKeyboardButton("🗑️ VACIAR CARRITO", callback_data="carrito_vaciar")],
    [InlineKeyboardButton("🔙 VOLVER A TIENDA", callback_data="menu_tienda")]
])

# 📌 Confirmación de pago
botones_factura = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ YA REALICÉ EL PAGO", callback_data="pagado_confirmar")],
    [InlineKeyboardButton("❌ CANCELAR", callback_data="pagado_cancelar")]
])
