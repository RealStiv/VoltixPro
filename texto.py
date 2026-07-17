from config import Config

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
"""
,
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
"""
}

def t(clave, **kwargs):
    # Si falta el texto, devuelve aviso en lugar de error
    if clave not in T:
        return f"ℹ️ Texto no configurado: {clave}"
    
    return T[clave].format(
        version=Config.VERSION,
        min=Config.MIN_SERVICIOS,
        max=Config.MAX_SERVICIOS,
        canal=Config.CANAL_OBLIGATORIO,
        simbolo=Config.SIMBOLO,
        metodo=Config.METODO_PAGO,
        cuenta=Config.DATOS_PAGO,
        minimo=Config.MONTO_MINIMO,
        **kwargs
    )
