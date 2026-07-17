import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from mongodb import coleccion_paneles
from bson.objectid import ObjectId
from datetime import datetime


async def verificar_panel(url: str, api_key: str):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as sesion:
            async with sesion.get(f"{url}?key={api_key}&action=balance") as respuesta:
                return respuesta.status == 200
    except Exception as e:
        print(f"Error al verificar panel: {e}")
        return False


async def agregar_panel_smm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return

    texto_completo = " ".join(context.args).strip()
    if not texto_completo or "|" not in texto_completo:
        await update.message.reply_text(
            "❌ Formato incorrecto ⚠️\n✅ Usa exactamente así:\n`/agregarpanel NOMBRE | URL | API_KEY | PORCENTAJE`",
            parse_mode="Markdown"
        )
        return

    partes = [p.strip() for p in texto_completo.split("|")]
    if len(partes) != 4:
        await update.message.reply_text(
            "❌ Faltan datos o sobran separadores ⚠️\n✅ Usa: NOMBRE | URL | API_KEY | PORCENTAJE",
            parse_mode="Markdown"
        )
        return

    nombre, url, api_key, margen_texto = partes
    if not nombre or not url or not api_key or not margen_texto:
        await update.message.reply_text("❌ No puedes dejar ningún dato vacío")
        return

    try:
        margen_personalizado = float(margen_texto)
    except:
        await update.message.reply_text("❌ El porcentaje debe ser solo un número, ejemplo: 40")
        return

    if not url.endswith("/"):
        url += "/"
    
    if not await verificar_panel(url, api_key):
        await update.message.reply_text("❌ No se pudo conectar al panel, verifica la URL o API Key")
        return
    
    existe = coleccion_paneles.find_one({"url": url, "activo": True})
    if existe:
        await update.message.reply_text("⚠️ Este panel ya está registrado y activo")
        return
    
    coleccion_paneles.insert_one({
        "nombre": nombre,
        "url": url,
        "api_key": api_key,
        "porcentaje_ganancia": margen_personalizado,
        "activo": True,
        "creado_en": datetime.now()
    })
    await update.message.reply_text(f"✅ Panel <b>{nombre}</b> agregado correctamente y listo para usar", parse_mode="HTML")


async def listar_paneles():
    return list(coleccion_paneles.find({"activo": True}).sort("creado_en", -1))


async def editar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ Formato incorrecto ⚠️\n✅ Usa: `/editarpanel ID CAMPO VALOR`\nCampos: nombre / url / api_key / porcentaje",
            parse_mode="Markdown"
        )
        return

    identificador = context.args[0]
    campo = context.args[1].lower()
    nuevo_valor = " ".join(context.args[2:])

    mapa_campos = {
        "nombre": "nombre",
        "url": "url",
        "api_key": "api_key",
        "porcentaje": "porcentaje_ganancia",
        "margen": "porcentaje_ganancia"
    }
    campo_real = mapa_campos.get(campo)
    if not campo_real:
        await update.message.reply_text("❌ Campo no válido")
        return

    if campo_real == "porcentaje_ganancia":
        try:
            nuevo_valor = float(nuevo_valor)
        except:
            await update.message.reply_text("❌ El porcentaje debe ser un número")
            return

    try:
        busqueda = {}
        if len(identificador) == 24:
            busqueda["_id"] = ObjectId(identificador)
        else:
            busqueda["nombre"] = identificador
        busqueda["activo"] = True

        resultado = coleccion_paneles.update_one(
            busqueda,
            {"$set": {campo_real: nuevo_valor, "actualizado_en": datetime.now()}}
        )
        if resultado.modified_count > 0:
            await update.message.reply_text("✅ Panel actualizado correctamente")
        else:
            await update.message.reply_text("❌ No se encontró el panel o no hubo cambios")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def eliminar_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ No tienes permisos suficientes")
        return

    if not context.args:
        await update.message.reply_text("❌ Escribe el ID o nombre del panel:\n`/borrarpanel ID o NOMBRE`", parse_mode="Markdown")
        return

    identificador = " ".join(context.args)
    try:
        busqueda = {}
        if len(identificador) == 24:
            busqueda["_id"] = ObjectId(identificador)
        else:
            busqueda["nombre"] = identificador

        resultado = coleccion_paneles.update_one(
            busqueda,
            {"$set": {"activo": False, "eliminado_en": datetime.now()}}
        )
        if resultado.modified_count > 0:
            await update.message.reply_text("✅ Panel eliminado correctamente")
        else:
            await update.message.reply_text("❌ No se encontró el panel")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
