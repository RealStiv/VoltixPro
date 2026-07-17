from config import Config
from mongodb import coleccion_configuracion

def calcular_precios(costo_proveedor: float, margen_personalizado: float = None):
    # Primero busca configuración guardada, si no usa la por defecto
    config = coleccion_configuracion.find_one({"tipo": "general"}) or {}
    margen_base = config.get("porcentaje_ganancia", Config.MARGEN_GENERAL)
    
    margen = margen_personalizado if margen_personalizado is not None else margen_base
    precio_venta = costo_proveedor * (1 + margen / 100)
    ganancia = precio_venta - costo_proveedor
    
    return {
        "costo_proveedor": round(costo_proveedor, 4),
        "precio_venta": round(precio_venta, 4),
        "ganancia": round(ganancia, 4),
        "margen_aplicado": margen
    }
