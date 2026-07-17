from datetime import datetime, date
from config import Config
from mongodb import coleccion_usuarios, coleccion_configuracion

async def calcular_nivel_usuario(usuario_id: int):
    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    if not usuario:
        return "bronce", 0

    gasto_total = usuario.get("gasto_total", 0)
    niveles = coleccion_configuracion.find_one({"clave": "niveles"})["valor"]

    nivel_actual = "bronce"
    descuento = 0
    for nivel, datos in sorted(niveles.items(), key=lambda x: x[1]["minimo_gasto"], reverse=True):
        if gasto_total >= datos["minimo_gasto"]:
            nivel_actual = nivel
            descuento = datos["descuento"]
            break

    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$set": {"nivel": nivel_actual}}
    )
    return nivel_actual, descuento

async def verificar_limite_gasto(usuario_id: int, monto: float):
    hoy = date.today().isoformat()
    usuario = coleccion_usuarios.find_one({"user_id": usuario_id})
    limite = coleccion_configuracion.find_one({"clave": "limite_diario_global"})["valor"]

    ultimo_dia = usuario.get("ultimo_gasto_dia", "")
    gasto_hoy = usuario.get("gasto_hoy", 0) if ultimo_dia == hoy else 0

    if ultimo_dia != hoy:
        coleccion_usuarios.update_one(
            {"user_id": usuario_id},
            {"$set": {"gasto_hoy": 0, "ultimo_gasto_dia": hoy}}
        )
        gasto_hoy = 0

    if limite > 0 and (gasto_hoy + monto) > limite:
        return False, f"❌ Superas tu límite diario de ${limite} (gastaste: ${gasto_hoy:.2f})"
    
    return True, "✅ Dentro del límite"

async def sumar_gasto_usuario(usuario_id: int, monto: float):
    hoy = date.today().isoformat()
    coleccion_usuarios.update_one(
        {"user_id": usuario_id},
        {"$inc": {"gasto_total": monto, "gasto_hoy": monto}, "$set": {"ultimo_gasto_dia": hoy}}
    )
    await calcular_nivel_usuario(usuario_id)
