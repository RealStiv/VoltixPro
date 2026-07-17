from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config import Config

# 📦 Conexión principal
try:
    cliente = MongoClient(Config.MONGO_URI)
    db = cliente["voltixpro_v4"]
    print("✅ CONEXIÓN A MONGODB EXITOSA")
except PyMongoError as e:
    print(f"❌ ERROR AL CONECTAR: {str(e)}")
    raise SystemExit

# 📚 TODAS LAS COLECCIONES
coleccion_usuarios = db["usuarios"]
coleccion_categorias = db["categorias"]
coleccion_servicios = db["servicios"]
coleccion_pedidos = db["pedidos"]
coleccion_facturas = db["facturas"]
coleccion_paneles = db["paneles"]
coleccion_configuracion = db["configuracion"]
coleccion_auditoria = db["auditoria"]
coleccion_programados = db["avisos_programados"]

# ⚙️ INICIALIZA VALORES POR DEFECTO SI NO EXISTEN
async def iniciar_configuracion():
    configuracion_por_defecto = [
        # Generales
        {"clave": "modo_mantenimiento", "valor": False},
        {"clave": "monto_minimo_recarga", "valor": 5.0},
        {"clave": "canal_obligatorio", "valor": "@Voltix_Pro"},
        {"clave": "datos_pago", "valor": "Sin configurar"},
        {"clave": "porcentaje_ganancia", "valor": 20.0},

        # Niveles de usuario
        {"clave": "niveles", "valor": {
            "bronce": {"descuento": 0, "minimo_gasto": 0},
            "plata": {"descuento": 5, "minimo_gasto": 50},
            "oro": {"descuento": 10, "minimo_gasto": 150},
            "diamante": {"descuento": 18, "minimo_gasto": 400}
        }},

        # Límites y alertas
        {"clave": "limite_diario_global", "valor": 0},
        {"clave": "aviso_saldo_minimo", "valor": 2.0},

        # Sistema de referidos
        {"clave": "recompensa_referido", "valor": 5.0},

        # Seguridad
        {"clave": "clave_admin_seguridad", "valor": ""},
        {"clave": "metodos_pago_activos", "valor": ["transferencia", "cripto"]},
        {"clave": "direccion_usdt", "valor": ""},
        {"clave": "direccion_btc", "valor": ""},

        # 🎨 Marca y apariencia
        {"clave": "nombre_bot", "valor": "VOLTIXPRO"},
        {"clave": "emoji_principal", "valor": "⚡"},
        {"clave": "color_tema", "valor": "azul"},
        {"clave": "mensaje_bienvenida", "valor": "¡Bienvenido! Tu tienda de servicios confiable y rápida."},
        {"clave": "foto_bienvenida", "valor": ""},
        {"clave": "pie_pagina", "valor": "⚡ VOLTIXPRO - Todos los derechos reservados"},
        {"clave": "reglas", "valor": "1. Revisa bien tu enlace antes de pagar.\n2. No hacemos reembolsos por errores tuyos."}
    ]

    # Inserta solo si no existen
    for item in configuracion_por_defecto:
        if not coleccion_configuracion.find_one({"clave": item["clave"]}):
            coleccion_configuracion.insert_one(item)

    # Crea índices para búsquedas rápidas y evitar duplicados
    coleccion_usuarios.create_index("user_id", unique=True)
    coleccion_usuarios.create_index("codigo_referido", unique=True)
    coleccion_servicios.create_index([("nombre", "text")])
    coleccion_servicios.create_index("activo")
    coleccion_pedidos.create_index("usuario_id")
    coleccion_facturas.create_index("estado")

    print("✅ CONFIGURACIÓN E ÍNDICES CARGADOS CORRECTAMENTE")
