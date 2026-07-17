import aiohttp
from datetime import datetime
from mongodb import coleccion_paneles
from config import Config

async def revisar_estado_paneles(bot_app):
    paneles = list(coleccion_paneles.find({"activo": True}))
    alertas = []

    for panel in paneles:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
                async with s.get(panel["url"]) as res:
                    if res.status != 200:
                        alertas.append(f"⚠️ Panel {panel['nombre']} responde con error {res.status}")
        except Exception as e:
            alertas.append(f"⚠️ Panel {panel['nombre']} no se conecta: {str(e)}")

    if alertas:
        mensaje = "🚨 ALERTAS DE PANELES:\n\n" + "\n".join(alertas)
        await bot_app.bot.send_message(Config.ADMIN_ID, mensaje)
