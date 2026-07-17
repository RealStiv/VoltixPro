from datetime import datetime, timedelta
from mongodb import (
    coleccion_usuarios, coleccion_servicios, coleccion_facturas,
    coleccion_pedidos, coleccion_configuracion
)

async def obtener_estadisticas():
    hoy = datetime.now()
    mes_actual = hoy.month
    año_actual = hoy.year

    # Datos generales
    total_usuarios = coleccion_usuarios.count_documents({})
    activos = coleccion_usuarios.count_documents({"baneado": False})
    ganancia_total = coleccion_facturas.aggregate([
        {"$match": {"estado": "PAGADO"}},
        {"$group": {"_id": None, "total": {"$sum": "$monto"}}}
    ])
    ganancia = next(ganancia_total, {}).get("total", 0)

    # Más vendidos
    mas_vendidos = list(coleccion_pedidos.aggregate([
        {"$group": {"_id": "$nombre_servicio", "cantidad": {"$sum": 1}}},
        {"$sort": {"cantidad": -1}},
        {"$limit": 5}
    ]))

    # Horas de actividad
    horas_pico = list(coleccion_pedidos.aggregate([
        {"$group": {"_id": {"$hour": "$fecha"}, "cantidad": {"$sum": 1}}},
        {"$sort": {"cantidad": -1}},
        {"$limit": 3}
    ]))

    return {
        "usuarios": total_usuarios,
        "activos": activos,
        "ganancia_total": round(ganancia, 2),
        "mas_vendidos": mas_vendidos,
        "horas_pico": horas_pico
    }
