import uuid
from datetime import datetime
from config import Config
from texto import t

def generar_numero_factura():
    fecha = datetime.now().strftime("%Y%m%d")
    codigo = uuid.uuid4().hex[:8].upper()
    return f"FAC-{fecha}-{codigo}"

def crear_factura_completa(datos_pago: dict, usuario: dict):
    numero = generar_numero_factura()
    fecha_actual = datetime.now()
    
    return {
        "numero": numero,
        "user_id": usuario.get("user_id"),
        "nombre_usuario": usuario.get("nombre", "Sin nombre"),
        "rol_usuario": usuario.get("rol", "usuario"),
        "monto": datos_pago.get("monto", 0),
        "estado": "PENDIENTE",
        "metodo_pago": Config.METODO_PAGO or "No especificado",
        "comprobante": datos_pago.get("archivo", ""),
        "fecha": fecha_actual.strftime("%d/%m/%Y"),
        "hora": fecha_actual.strftime("%H:%M:%S"),
        "creado_en": fecha_actual
    }

def plantilla_factura(factura: dict):
    return t("factura_oficial",
        numero=factura.get("numero"),
        fecha=factura.get("fecha"),
        hora=factura.get("hora"),
        user_id=factura.get("user_id"),
        nombre=factura.get("nombre_usuario"),
        rol=factura.get("rol_usuario"),
        monto=factura.get("monto"),
        estado=factura.get("estado"),
        metodo=factura.get("metodo_pago")
    )
