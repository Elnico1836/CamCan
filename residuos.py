import concurrent.futures
import os
import random
import time
from io import BytesIO

import requests
from ddgs import DDGS
from PIL import Image

imagenes_por_objeto = 150
base_dir = r"C:\Users\user\Downloads\Residuos"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
})

palabras_excluidas = "-fresco -fresh -limpio -clean -entero -whole -perfecto -stock -nuevo -new -comprar -buy"

# PEGA AQUÍ TODO TU DICCIONARIO 'categorias' CON LAS 44 ETIQUETAS EXACTAMENTE COMO ESTABA
categorias = {
    # ---------------- CANECA NEGRA (No Aprovechables / Especiales) ----------------
    "pila_bateria": {"caneca": "Negra", "terminos": ["used batteries waste", "pilas usadas basura"]},
    "plastico_roto_sucio": {"caneca": "Negra", "terminos": ["broken dirty plastic waste", "plastico roto sucio basura"]},
    "colilla_cigarrillo": {"caneca": "Negra", "terminos": ["cigarette butts garbage", "colillas de cigarrillo basura"]},
    "carton_sucio": {"caneca": "Negra", "terminos": ["dirty greasy cardboard waste", "carton sucio basura"]},
    "plastico_contaminado": {"caneca": "Negra", "terminos": ["contaminated plastic waste", "plastico contaminado basura"]},
    "vaso_cafe_desechable": {"caneca": "Negra", "terminos": ["used disposable coffee cup waste", "vaso de cafe desechable sucio"]},
    "empaque_comida_sucio": {"caneca": "Negra", "terminos": ["dirty food packaging waste", "empaque de comida sucio basura"]},
    "residuos_mezclados": {"caneca": "Negra", "terminos": ["mixed garbage bin", "basura mezclada en caneca"]},
    "residuos_no_reciclables": {"caneca": "Negra", "terminos": ["non recyclable waste", "basura no reciclable"]},
    "caja_pizza_grasosa": {"caneca": "Negra", "terminos": ["greasy pizza box waste", "caja de pizza sucia basura"]},
    "contenedor_plastico_comida": {"caneca": "Negra", "terminos": ["dirty plastic food container waste", "recipiente plastico comida sucio"]},
    "desecho_sanitario": {"caneca": "Negra", "terminos": ["sanitary waste bin", "desechos sanitarios basura"]},
    "basura_callejera": {"caneca": "Negra", "terminos": ["street garbage pile", "basura tirada en la calle"]},
    "icopor_desechable": {"caneca": "Negra", "terminos": ["styrofoam waste garbage", "icopor sucio basura"]},
    "basura_comun": {"caneca": "Negra", "terminos": ["common trash waste", "basura ordinaria"]},
    "bolsa_basura_negra": {"caneca": "Negra", "terminos": ["black trash bag garbage", "bolsa de basura negra llena"]},
    "servilleta_usada": {"caneca": "Negra", "terminos": ["dirty used napkin waste", "servilleta sucia arrugada basura"]},
    "toalla_papel_usada": {"caneca": "Negra", "terminos": ["used paper towel waste", "toalla de papel sucia basura"]},
    "panuelo_usado": {"caneca": "Negra", "terminos": ["used tissue waste", "pañuelo desechable usado basura"]},
    "basura_vertedero": {"caneca": "Negra", "terminos": ["landfill waste", "basura de vertedero municipal"]},
    "empaque_papas_galletas": {"caneca": "Negra", "terminos": ["snack wrapper garbage", "bolsa de papas vacia basura"]},
    "pitillo_plastico": {"caneca": "Negra", "terminos": ["plastic straw waste", "pitillo de plastico usado basura"]},
    "viruta_lapiz": {"caneca": "Negra", "terminos": ["pencil shavings waste", "viruta de lapiz basura"]},
    "borrador_gastado": {"caneca": "Negra", "terminos": ["used eraser crumbs waste", "restos de borrador basura"]},
    "papel_chicle_dulces": {"caneca": "Negra", "terminos": ["candy wrapper waste", "envoltura de dulce basura"]},
    "esfero_mina_gastada": {"caneca": "Negra", "terminos": ["empty pens waste", "esferos gastados basura"]},

    # ---------------- CANECA BLANCA (Aprovechables) ----------------
    "carton_limpio": {"caneca": "Blanca", "terminos": ["clean cardboard box waste", "caja de carton reciclaje"]},
    "metal_reciclable": {"caneca": "Blanca", "terminos": ["recyclable metal waste", "metal reciclable chatarra"]},
    "papel_limpio": {"caneca": "Blanca", "terminos": ["clean paper recycling", "papel para reciclar"]},
    "plastico_limpio": {"caneca": "Blanca", "terminos": ["clean plastic bottle recycling", "botellas de plastico reciclaje"]},
    "ropa_usable": {"caneca": "Blanca", "terminos": ["old clothes donation", "ropa vieja usada"]},
    "calzado": {"caneca": "Blanca", "terminos": ["old shoes waste", "zapatos viejos basura"]},
    "cuaderno_viejo": {"caneca": "Blanca", "terminos": ["old notebook recycling", "cuaderno viejo reciclaje"]},
    "caja_jugo_tetrapak": {"caneca": "Blanca", "terminos": ["crushed tetrapak waste", "caja de jugo vacia basura"]},
    "botella_agua_pet": {"caneca": "Blanca", "terminos": ["crushed pet water bottle", "botella de agua plastica vacia aplastada"]},
    "lata_gaseosa": {"caneca": "Blanca", "terminos": ["crushed soda can waste", "lata de gaseosa vacia aplastada"]},
    "volante_papel": {"caneca": "Blanca", "terminos": ["paper flyer recycling", "volantes de papel arrugados"]},

    # ---------------- CANECA VERDE (Orgánicos) ----------------
    "desecho_biologico": {"caneca": "Verde", "terminos": ["biological waste compost", "desechos biologicos compost"]},
    "residuos_organicos": {"caneca": "Verde", "terminos": ["organic waste compost", "basura organica compostaje"]},
    "cascara_banano": {"caneca": "Verde", "terminos": ["banana peel garbage", "cascara de banano basura"]},
    "corazon_manzana": {"caneca": "Verde", "terminos": ["apple core waste", "corazon de manzana basura"]},
    "cascara_naranja": {"caneca": "Verde", "terminos": ["orange peel garbage", "cascara de naranja basura"]},
    "sobras_lonchera": {"caneca": "Verde", "terminos": ["food leftovers waste", "sobras de comida basura"]},
    "cascara_huevo": {"caneca": "Verde", "terminos": ["eggshell waste compost", "cascaras de huevo basura"]}
}


def descargar_imagen(url, ruta_archivo):
    """Descarga individual. Retorna True si fue exitosa."""
    if os.path.exists(ruta_archivo):
        return True
    try:
        with session.get(url, timeout=5) as r:
            if r.status_code == 200:
                content = r.content
                img = Image.open(BytesIO(content))
                img.verify()
                img = Image.open(BytesIO(content))
                img.convert("RGB").save(ruta_archivo, "JPEG", quality=85)
                return True
    except Exception:
        return False
    return False


def buscar_con_reintentos(query, max_results, max_reintentos=5):
    """
    Busca imágenes en DDG con backoff exponencial + jitter ante rate limits (403).
    Si sigue fallando, intenta con otro backend antes de rendirse.
    """
    backends_a_probar = ["auto", "html", "lite"]

    for intento in range(max_reintentos):
        backend = backends_a_probar[min(intento, len(backends_a_probar) - 1)]
        try:
            with DDGS() as ddgs:
                resultados = list(
                    ddgs.images(query, max_results=max_results, backend=backend)
                )
            if resultados:
                return [r.get("image") for r in resultados if r.get("image")]
            return []
        except Exception as e:
            mensaje = str(e)
            es_rate_limit = "403" in mensaje or "Ratelimit" in mensaje or "ratelimit" in mensaje.lower()
            espera = (2 ** intento) + random.uniform(1, 3)
            if es_rate_limit:
                print(f"    ⏳ Rate limit detectado (intento {intento + 1}/{max_reintentos}). "
                      f"Esperando {espera:.1f}s y reintentando con backend='{backend}'...")
            else:
                print(f"    ⚠️ Error no relacionado a rate limit (intento {intento + 1}/{max_reintentos}): {e}")
            time.sleep(espera)

    print(f"    ❌ Se agotaron los reintentos para '{query}'. Saltando.")
    return []


if __name__ == "__main__":
    print(f"📁 Destino: {base_dir}\n")
    print("⏳ Iniciando extractor con protección Anti-Bloqueo...\n")

    for subcat, info in categorias.items():
        caneca = info["caneca"]

        for termino in info["terminos"]:
            carpeta = os.path.join(base_dir, caneca, subcat)
            os.makedirs(carpeta, exist_ok=True)

            busqueda_filtrada = f"{termino} {palabras_excluidas}"
            nombre_base = termino.replace(" ", "_")[:50]

            print(f"🔍 Buscando URLs para: '{termino}'...")

            # 1. BÚSQUEDA SECUENCIAL con reintentos y backoff (clave para no ser bloqueado)
            urls = buscar_con_reintentos(busqueda_filtrada, imagenes_por_objeto * 2)

            if not urls:
                print(f"⏭️ No se encontraron URLs para '{termino}'. Saltando.\n")
                # Aun sin resultados, pausamos para no golpear DDG de inmediato con el siguiente término
                time.sleep(random.uniform(4, 8))
                continue

            # 2. DESCARGA EN PARALELO (rápido, porque descarga de distintos servidores)
            exitos = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futuros = {}
                for i, url in enumerate(urls):
                    archivo = os.path.join(carpeta, f"{nombre_base}_{i + 1}.jpg")
                    futuros[executor.submit(descargar_imagen, url, archivo)] = url

                for futuro in concurrent.futures.as_completed(futuros):
                    if futuro.result():
                        exitos += 1
                    if exitos >= imagenes_por_objeto:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

            print(f"✅ {exitos:>3} imgs descargadas | {caneca}/{subcat} ← '{termino}'")

            # 3. PAUSA OBLIGATORIA con jitter (evita patrones detectables de request)
            pausa = random.uniform(4, 9)
            print(f"    💤 Pausando {pausa:.1f}s antes de la siguiente búsqueda...\n")
            time.sleep(pausa)

    print("\n🎉 Descarga masiva completada.")