from datetime import date
from mongodb import coleccion_usuarios, coleccion_configuracion

tasas_cambio = {
    "USD": 1,
    "BOB": 6.96,
    "COP": 3800,
    "MXN": 17.50
}

async def convertir_moneda(monto: float, moneda_destino: str):
    base = tasas_cambio.get(moneda_destino, 1)
    return round(monto * base, 2)

async def cambiar_moneda(usuario_id: int, nueva_moneda: str):
    if nueva_moneda not in tasas_cambio:
        return False, "Monedas disponibles: USD, BOB, COP, MXN"
    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"moneda": nueva_moneda}}
    )
    return True, f"✅ Ahora verás todo en {nueva_moneda}"

async def revisar_saldo_bajo(usuario_id: int):
    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    minimo = coleccion_configuracion.find_one({"clave": "aviso_saldo_minimo"})["valor"]
    hoy = date.today().isoformat()
    ultimo = usuario.get("ultimo_aviso_saldo_bajo", "")
    
    if usuario["saldo"] <= minimo and ultimo != hoy:
        coleccion_usuarios.update_one(
            {"user_id": usuario_id},
            {"$set": {"ultimo_aviso_saldo_bajo": hoy}}
        )
        return True
    return False

async def cambiar_interfaz(usuario_id: int, modo: str):
    if modo not in ["completo", "compacto"]:
        return False
    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"modo_interfaz": modo}}
    )
    return True
