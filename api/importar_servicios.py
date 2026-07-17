import aiohttp
from datetime import datetime
from mongodb import coleccion_paneles, coleccion_servicios, coleccion_categorias

async def importar_desde_api():
    paneles = list(coleccion_paneles.find({"activo": True}))
    
    if not paneles:
        return "⚠️ <b>No hay paneles activos registrados para sincronizar.</b>"

    total_nuevos = 0
    total_actualizados = 0
    lista_errores = []

    for panel in paneles:
        nombre_panel = panel.get("nombre", "Panel sin nombre")
        url_base = str(panel.get("url", "")).strip().rstrip("/")
        api_key = str(panel.get("api_key", "")).strip()
        porcentaje_extra = float(panel.get("porcentaje_ganancia", 0))

        if not url_base or not api_key:
            lista_errores.append(f"• {nombre_panel}: Falta URL o clave API")
            continue

        url_peticion = f"{url_base}/api.php?key={api_key}&action=services"

        try:
            # Máximo 15 segundos de espera por cada panel
            tiempo_limite = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=tiempo_limite) as sesion:
                async with sesion.get(url_peticion, allow_redirects=True) as respuesta:
                    if respuesta.status != 200:
                        lista_errores.append(f"• {nombre_panel}: Error de conexión ({respuesta.status})")
                        continue

                    datos_recibidos = await respuesta.json()

                    if not isinstance(datos_recibidos, list):
                        lista_errores.append(f"• {nombre_panel}: La API no devolvió una lista válida")
                        continue

                    for servicio in datos_recibidos:
                        id_api = str(servicio.get("service", "")).strip()
                        nombre_servicio = str(servicio.get("name", "Sin nombre")).strip()
                        nombre_categoria = str(servicio.get("category", "Sin categoría")).strip()
                        precio_base = float(servicio.get("rate", 0))
                        minimo = int(servicio.get("min", 1))
                        maximo = int(servicio.get("max", 10000))
                        descripcion = str(servicio.get("description", "")).strip()

                        if not id_api or precio_base <= 0:
                            continue

                        # Buscar o crear categoría automáticamente
                        cat_existe = coleccion_categorias.find_one({"nombre": nombre_categoria})
                        if cat_existe:
                            id_categoria = cat_existe["_id"]
                        else:
                            nueva_categoria = {
                                "nombre": nombre_categoria,
                                "descripcion": "",
                                "activo": True,
                                "creado_en": datetime.now()
                            }
                            resultado = coleccion_categorias.insert_one(nueva_categoria)
                            id_categoria = resultado.inserted_id

                        # Calcular precio final con tu ganancia
                        precio_final = round(precio_base * (1 + (porcentaje_extra / 100)), 2)

                        datos_guardar = {
                            "id_api": id_api,
                            "nombre": nombre_servicio,
                            "categoria_id": id_categoria,
                            "categoria_nombre": nombre_categoria,
                            "descripcion": descripcion,
                            "precio_original": precio_base,
                            "precio_venta": precio_final,
                            "cantidad_minima": minimo,
                            "cantidad_maxima": maximo,
                            "panel_origen": nombre_panel,
                            "activo": True,
                            "actualizado_en": datetime.now()
                        }

                        # Actualizar o insertar
                        existe = coleccion_servicios.find_one({"id_api": id_api, "panel_origen": nombre_panel})
                        if existe:
                            coleccion_servicios.update_one({"_id": existe["_id"]}, {"$set": datos_guardar})
                            total_actualizados += 1
                        else:
                            coleccion_servicios.insert_one(datos_guardar)
                            total_nuevos += 1

        except aiohttp.ClientConnectionError:
            lista_errores.append(f"• {nombre_panel}: No se pudo conectar al servidor")
        except aiohttp.ClientResponseError:
            lista_errores.append(f"• {nombre_panel}: Respuesta inválida del panel")
        except asyncio.TimeoutError:
            lista_errores.append(f"• {nombre_panel}: Tardó demasiado en responder")
        except Exception as e:
            lista_errores.append(f"• {nombre_panel}: {str(e)}")
            print(f"Error detallado en {nombre_panel}: {str(e)}")
        continue

    # Mensaje final completo
    mensaje = f"""✅ <b>SINCRONIZACIÓN FINALIZADA</b>

➕ Servicios nuevos agregados: <b>{total_nuevos}</b>
🔄 Servicios actualizados: <b>{total_actualizados}</b>
"""

    if lista_errores:
        mensaje += f"\n⚠️ <b>Hubo inconvenientes en:</b>\n"
        # Mostrar máximo 5 errores para no alargar el mensaje
        for error in lista_errores[:5]:
            mensaje += f"{error}\n"
        if len(lista_errores) > 5:
            mensaje += f"... y {len(lista_errores)-5} más, revisa los registros"

    return mensaje
