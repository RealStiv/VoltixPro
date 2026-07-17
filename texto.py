from config import Config
from modulos.personalizacion import obtener_ajuste

T = {
    "bienvenida": """
✨ <b>¡BIENVENIDO A VOLTIXPRO!</b> ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
El sistema de crecimiento más completo, rápido y seguro 🚀

🔹 <b>Versión:</b> v{version}
🔹 <b>Servicios disponibles:</b> Más de {min} activos
🔹 <b>Moneda:</b> {simbolo}
🔹 <b>Recargas desde:</b> {simbolo}{minimo:.2f}

✅ ¿Qué puedes hacer aquí?
• Comprar seguidores, me gusta, vistas y más
• Precios con tu ganancia personalizada
• Recargas automáticas con confirmación inmediata
• Soporte directo con el administrador
• Herramientas exclusivas incluidas

⚡ Todo funciona 24/7 sin interrupciones

Elige la opción que necesites del menú de abajo 👇
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
© VoltixPro - Todos los derechos reservados
""",

    "necesitas_suscribirte": """⚠️ <b>ACCESO RESTRINGIDO</b>
Debes estar suscrito a nuestro canal oficial para usar el bot:
🔗 {canal}
Al suscribirte pulsa el botón de abajo.
""",

    "suscrito_correcto": "✅ <b>VERIFICADO</b> - ¡Bienvenido! Ya puedes usar el bot.",

    "perfil": """👤 <b>TU PERFIL COMPLETO</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 ID: <code>{user_id}</code>
📝 Nombre: {nombre}
💰 Saldo: {simbolo}{saldo:.2f}
🛒 Pedidos realizados: {pedidos}
🧾 Facturas: {facturas}
🔑 Claves API: {claves}
🎖️ Rol: <b>{rol}</b>
🔒 Permisos: {permisos}
📅 Fecha de registro: {fecha}
""",

    "recarga_instruccion": """💸 <b>RECARGA DE SALDO</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Método de pago: {metodo}
🏦 Datos de cuenta: <code>{cuenta}</code>
💰 Monto mínimo: {simbolo}{minimo:.2f}
📷 Envía ahora la foto del comprobante o archivo TXT/PDF:
""",

    "factura_oficial": """🧾 <b>FACTURA DE RECARGA N° {numero}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Fecha: {fecha} | ⏰ Hora: {hora}
👤 <b>DATOS DEL USUARIO</b>
🆔 ID Telegram: <code>{user_id}</code>
📝 Nombre completo: {nombre}
🎖️ Tipo de cuenta: {rol}
💸 <b>DETALLE DEL PAGO</b>
💰 Monto: {simbolo}{monto:.2f}
📌 Estado: <b>{estado}</b>
📋 Método: {metodo}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Bot SMM v{version} - Todos los derechos reservados
""",

    "pago_aprobado": """✅ <b>PAGO APROBADO</b>
Se agregó correctamente el saldo a tu cuenta.
💰 Saldo actual: {simbolo}{saldo:.2f}
""",

    "pago_rechazado": """❌ <b>PAGO RECHAZADO</b>
Motivo: {motivo}
Verifica el comprobante y vuelve a intentarlo.
""",

    "tienda_inicio": """🛒 <b>TIENDA DE SERVICIOS</b>
Selecciona una categoría para ver los servicios disponibles:
""",

    "admin_panel": """🔐 <b>PANEL DE ADMINISTRACIÓN TOTAL</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 Usuarios totales: {usuarios}
📂 Categorías activas: {categorias}
🛒 Servicios disponibles: {servicios}
🧾 Facturas pendientes: {facturas}
⚙️ Paneles SMM conectados: {paneles}
""",

    # Textos generales complementarios de la V4
    "acceso_denegado": "❌ No tienes permiso para realizar esta acción.",
    "error_general": "⚠️ Ocurrió un error, intenta nuevamente más tarde.",
    "modo_mantenimiento": "🚧 <b>MODO MANTENIMIENTO ACTIVO</b>\nEstamos realizando mejoras, vuelve en unos minutos.",
    "saldo_insuficiente": "💸 No tienes saldo suficiente para realizar esta compra.",
    "aviso_saldo_bajo": "🔔 Tu saldo es muy bajo, recarga pronto para seguir comprando.",
    "referido_registrado": "✅ Se registró correctamente tu invitación.",
    "ya_tienes_referido": "⚠️ Ya fuiste registrado por un invitante anteriormente.",
    "carrito_vacio": "🛒 Tu carrito está vacío.",
    "agregado_carrito": "✅ Se agregó al carrito correctamente.",
    "guardado_correctamente": "✅ Se guardó todo correctamente."
}

def t(clave, **kwargs):
    # Busca primero si tienes el texto personalizado en la configuración
    personalizado = await obtener_ajuste(clave)
    if personalizado is not None:
        return personalizado

    # Si falta el texto, devuelve aviso en lugar de error
    if clave not in T:
        return f"ℹ️ Texto no configurado: {clave}"
    
    return T[clave].format(
        version=getattr(Config, "VERSION", "4.0"),
        min=getattr(Config, "MIN_SERVICIOS", 0),
        max=getattr(Config, "MAX_SERVICIOS", 0),
        canal=await obtener_ajuste("canal_obligatorio", getattr(Config, "CANAL_OBLIGATORIO", "@VoltixPro")),
        simbolo=getattr(Config, "SIMBOLO", "$"),
        metodo=await obtener_ajuste("metodos_pago_activos", getattr(Config, "METODO_PAGO", "Transferencia")),
        cuenta=await obtener_ajuste("datos_pago", getattr(Config, "DATOS_PAGO", "Sin configurar")),
        minimo=await obtener_ajuste("monto_minimo_recarga", getattr(Config, "MONTO_MINIMO", 5.0)),
        **kwargs
    )
