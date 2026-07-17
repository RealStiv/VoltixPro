from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

# -------------------------------
# MENÚS GENERALES
# -------------------------------
def menu_principal():
    return ReplyKeyboardMarkup([
        ["🛒 Tienda SMM", "💰 Recargar Saldo"],
        ["👤 Mi Perfil", "📦 Mis Pedidos"],
        ["🔧 Herramientas", "⚙️ Admin Total"]
    ], resize_keyboard=True, input_field_placeholder="Selecciona una opción")

def menu_suscripcion():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 IR AL CANAL OFICIAL", url=f"https://t.me/{Config.CANAL_OBLIGATORIO.replace('@','')}")],
        [InlineKeyboardButton("✅ YA ME SUSCRIBÍ", callback_data="verificar_sus")]
    ])

def menu_admin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Gestionar Usuarios", callback_data="ad_usuarios"),
         InlineKeyboardButton("📂 Categorías", callback_data="ad_categorias")],
        [InlineKeyboardButton("➕ Agregar Panel SMM", callback_data="ad_panel"),
         InlineKeyboardButton("🔄 Actualizar Servicios", callback_data="ad_actualizar")],
        [InlineKeyboardButton("🧾 Revisar Facturas", callback_data="ad_facturas"),
         InlineKeyboardButton("⚙️ Configuración", callback_data="ad_config")],
        [InlineKeyboardButton("📊 Acciones Rápidas", callback_data="acc_menu")],
        [InlineKeyboardButton("🔙 SALIR DEL PANEL", callback_data="ad_salir")]
    ])

# -------------------------------
# SUBMENÚS COMPLETOS
# -------------------------------
def menu_usuarios():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Ver lista completa", callback_data="us_lista"),
         InlineKeyboardButton("💸 Recargar saldo", callback_data="us_recargar")],
        [InlineKeyboardButton("🔒 Bloquear usuario", callback_data="us_bloquear"),
         InlineKeyboardButton("🔓 Desbloquear", callback_data="us_desbloquear")],
        [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_salir")]
    ])

def menu_categorias():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Crear nueva", callback_data="cat_crear"),
         InlineKeyboardButton("✏️ Editar", callback_data="cat_editar")],
        [InlineKeyboardButton("❌ Eliminar", callback_data="cat_eliminar")],
        [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_salir")]
    ])

def menu_panel():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Agregar nuevo", callback_data="pan_agregar"),
         InlineKeyboardButton("📋 Ver activos", callback_data="pan_lista")],
        [InlineKeyboardButton("✏️ Editar", callback_data="pan_editar"),
         InlineKeyboardButton("❌ Eliminar", callback_data="pan_eliminar")],
        [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_salir")]
    ])

def menu_config():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Monto mínimo recarga", callback_data="conf_minimo"),
         InlineKeyboardButton("📢 Canal obligatorio", callback_data="conf_canal")],
        [InlineKeyboardButton("🔑 Datos de pago", callback_data="conf_pago"),
         InlineKeyboardButton("📊 Porcentaje ganancia", callback_data="conf_margen")],
        [InlineKeyboardButton("🔔 Mensajes y avisos", callback_data="conf_mensajes")],
        [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_salir")]
    ])

def menu_acciones():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Enviar aviso a todos", callback_data="acc_aviso"),
         InlineKeyboardButton("📈 Ver estadísticas", callback_data="acc_stats")],
        [InlineKeyboardButton("🔄 Reiniciar servicios", callback_data="acc_reiniciar")],
        [InlineKeyboardButton("🔙 VOLVER AL INICIO", callback_data="ad_salir")]
    ])

# -------------------------------
# BOTONES ESPECÍFICOS
# -------------------------------
def botones_factura(numero_factura: str, monto: float = 0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ APROBAR RECARGA", callback_data=f"fac_ok_{numero_factura}_{monto}")],
        [InlineKeyboardButton("❌ RECHAZAR", callback_data=f"fac_no_{numero_factura}")],
        [InlineKeyboardButton("🔙 VOLVER", callback_data="ad_facturas")]
    ])

def botones_lista_facturas(lista_facturas):
    filas = []
    for fac in lista_facturas:
        filas.append([
            InlineKeyboardButton(f"📄 N°{fac['numero']} - ${fac['monto']}", callback_data=f"fac_ver_{fac['numero']}"),
            InlineKeyboardButton("✅", callback_data=f"fac_ok_{fac['numero']}_{fac['monto']}"),
            InlineKeyboardButton("❌", callback_data=f"fac_no_{fac['numero']}")
        ])
    filas.append([InlineKeyboardButton("🔙 VOLVER", callback_data="ad_facturas")])
    return InlineKeyboardMarkup(filas)
