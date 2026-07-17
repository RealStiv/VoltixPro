import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # Nombres unificados para que todo coincida
    CANAL_OBLIGATORIO = os.getenv("CANAL_OBLIGATORIO", "VoltixProOficial")
    MONGO_URI = os.getenv("MONGODB_URI")
    NOMBRE_BASE_DATOS = os.getenv("DB_NOMBRE", "voltixpro_db")
    
    VERSION = "13.0"
    MIN_SERVICIOS = 100
    MAX_SERVICIOS = 300
    MONEDA = os.getenv("MONEDA", "USD")
    SIMBOLO = os.getenv("SIMBOLO", "$")
    METODO_PAGO = os.getenv("METODO_PAGO", "")
    DATOS_PAGO = os.getenv("DATOS_CUENTA", "")
    MONTO_MINIMO = float(os.getenv("MONTO_MINIMO", 10.0))
    MARGEN_GENERAL = float(os.getenv("MARGEN_GENERAL", 40))
