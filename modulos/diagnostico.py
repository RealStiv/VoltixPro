import aiohttp
import time
from datetime import datetime
from bson import ObjectId
from config import Config
from mongodb import coleccion_paneles, coleccion_servicios

async def diagnosticar_panel(update, context):
    from modulos.auditoria import registrar_accion
    if update.effective_user.id != Config.ADMIN_ID:
        return await update.message.reply_text("❌ Sin permiso")

    if not context.args:
        return await update.message.reply_text("Uso: /diagnosticar ID_DEL_PANEL")

    try:
        panel_id = ObjectId(context.args[0])
    except:
        return await update.message.reply_text("❌ ID no válido")

    panel = coleccion_paneles.find_one({"_id": panel_id})
    if not panel:
        return await update.message.reply_text("❌ Panel no encontrado")

    inicio = time.time()
    estado = "✅ Funcionando correctamente"
    codigo = 0
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
            async with s.get(panel["url"]) as res:
                codigo = res.status
                if res.status != 200:
                    estado = f"⚠️ Responde con código {res.status}"
    except Exception as e:
        estado = f"❌ Error de conexión: {str(e)}"

    velocidad = round((time.time() - inicio) * 1000)
    servicios = coleccion_servicios.count_documents({"id_panel": str(panel_id)})

    texto = f"""🔍 **DIAGNÓSTICO: {panel['nombre']}**

🌐 URL: {panel['url']}
📡 Estado: {estado}
⚡ Tiempo respuesta: {velocidad}ms
🛠️ Servicios vinculados: {servicios}
📊 Margen ganancia: {panel['porcentaje_ganancia']}%
"""
    await registrar_accion(update.effective_user.id, "Ejecutó diagnóstico", f"Panel {panel['nombre']}")
    await update.message.reply_text(texto, parse_mode="Markdown")


async def probar_servicio(update, context):
    from modulos.auditoria import registrar_accion
    if update.effective_user.id != Config.ADMIN_ID:
        return await update.message.reply_text("❌ Sin permiso")

    if len(context.args) < 2:
        return await update.message.reply_text("Uso: /pruebaservicio ID_SERVICIO ENLACE_DE_PRUEBA")

    id_serv = context.args[0]
    enlace = " ".join(context.args[1:])
    servicio = coleccion_servicios.find_one({"id_api": id_serv})

    if not servicio:
        return await update.message.reply_text("❌ Servicio no encontrado")

    texto = f"""🧪 **PRUEBA DE SERVICIO SOLICITADA**

📦 Servicio: {servicio['nombre']}
🔗 Enlace: {enlace}
💸 Precio: ${servicio['precio_venta']}

⚠️ Esta función envía una orden real pequeña al proveedor para confirmar que funciona.
Escribe /confirmarprueba para proceder o ignora este mensaje.
"""
    await registrar_accion(update.effective_user.id, "Solicitó prueba de servicio", servicio['nombre'])
    await update.message.reply_text(texto)
