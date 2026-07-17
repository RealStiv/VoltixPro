import re
import aiohttp
from datetime import datetime
from mongodb import coleccion_servicios, coleccion_paneles, coleccion_categorias
from margenes import calcular_precios
from modulos.tienda_categorias import clasificar_servicio


async def importar_desde_api():
    paneles = list(coleccion_paneles.find({"activo": True}))
    total_importados = 0
    total_nuevos = 0
    total_actualizados = 0
    errores = []
    
    for panel in paneles:
        try:
            url_base = panel["url"].rstrip("/")
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as sesion:
                async with sesion.get(f"{url_base}/?key={panel['api_key']}&action=services") as respuesta:
                    if respuesta.status != 200:
                        errores.append(f"{panel['nombre']}: Error {respuesta.status}")
                        continue
                    datos = await respuesta.json()
                    
                    lista_servicios = datos if isinstance(datos, list) else list(datos.values())

                    for servicio in lista_servicios:
                        if not isinstance(servicio, dict):
                            continue
                            
                        id_externo = str(servicio.get("service", servicio.get("id")))
                        nombre = servicio.get("name", "Sin nombre")
                        costo_bruto = float(servicio.get("rate", 0))
                        costo_proveedor = costo_bruto / 1000 if costo_bruto > 100 else costo_bruto
                        
                        precios = calcular_precios(costo_proveedor, panel.get("porcentaje_ganancia"))
                        categoria = clasificar_servicio(nombre)
                        
                        existe = coleccion_servicios.find_one({"id_externo": id_externo, "panel_id": panel["_id"]})
                        
                        datos_guardar = {
                            "id_externo": id_externo,
                            "nombre": nombre,
                            "categoria": categoria,
                            "costo_proveedor": precios["costo_proveedor"],
                            "precio_venta": precios["precio_venta"],
                            "minimo": int(servicio.get("min", 10)),
                            "maximo": int(servicio.get("max", 5000)),
                            "panel_id": panel["_id"],
                            "activo": True,
                            "actualizado_en": datetime.now()
                        }
                        
                        if existe:
                            coleccion_servicios.update_one({"_id": existe["_id"]}, {"$set": datos_guardar})
                            total_actualizados +=1
                        else:
                            datos_guardar["creado_en"] = datetime.now()
                            coleccion_servicios.insert_one(datos_guardar)
                            total_nuevos +=1
                        
                        total_importados += 1

        except Exception as e:
            errores.append(f"{panel['nombre']}: {str(e)}")
            continue
    
    # Actualizar lista de categorías únicas
    categorias_unicas = coleccion_servicios.distinct("categoria", {"activo": True})
    coleccion_categorias.delete_many({})
    for cat in categorias_unicas:
        coleccion_categorias.insert_one({"nombre": cat, "activo": True, "creado_en": datetime.now()})
    
    texto = f"✅ Importación finalizada: {total_importados} servicios procesados\n🆕 Nuevos: {total_nuevos} | 🔄 Actualizados: {total_actualizados}"
    if errores:
        texto += f"\n⚠️ Errores:\n" + "\n".join(errores[:5])
    return texto


async def importar_desde_texto(texto: str):
    patron = r"(\d{1,5})\s*[-:]\s*(.+?)\s*[-:]\s*([0-9.]{1,10})"
    coincidencias = re.findall(patron, texto, re.IGNORECASE)
    total = 0
    
    for id_serv, nombre, precio in coincidencias:
        categoria = clasificar_servicio(nombre.strip())
        precios = calcular_precios(float(precio))
        
        coleccion_servicios.update_one(
            {"id_externo": int(id_serv)},
            {"$set": {
                "id_externo": int(id_serv),
                "nombre": nombre.strip(),
                "categoria": categoria,
                "costo_proveedor": precios["costo_proveedor"],
                "precio_venta": precios["precio_venta"],
                "minimo": 10,
                "maximo": 3000,
                "activo": True,
                "actualizado_en": datetime.now()
            }},
            upsert=True
        )
        total += 1
    
    # Actualizar categorías
    categorias_unicas = coleccion_servicios.distinct("categoria", {"activo": True})
    coleccion_categorias.delete_many({})
    for cat in categorias_unicas:
        coleccion_categorias.insert_one({"nombre": cat, "activo": True})
    
    return f"✅ Se cargaron {total} servicios desde el archivo TXT"


async def sincronizar_servicios():
    return await importar_desde_api()
