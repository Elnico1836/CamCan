import os
import requests
from io import BytesIO
from PIL import Image
from ddgs import DDGS
import concurrent.futures

imagenes_por_objeto = 300
base_dir = r"C:\Users\user\Downloads\Residuos"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

categorias = {
    "Fondo_Blanco": {
        "caneca": "Fondo",
        "terminos": [
            "fondo blanco"
        ]
    }
}

def descargar_imagen(url, ruta_archivo):
    try:
        with session.get(url, timeout=6) as r:
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content))
                img.convert("RGB").save(ruta_archivo, "JPEG")
                return True
    except Exception:
        return False
    return False

def descargar_objeto(caneca, subcategoria, termino):
    carpeta = os.path.join(base_dir, caneca, subcategoria)
    os.makedirs(carpeta, exist_ok=True)
    resultados = DDGS().images(termino, max_results=imagenes_por_objeto)
    count = 0
    for r in resultados:
        url = r.get("image")
        if not url:
            continue
        nombre = termino.replace(" ", "_")[:60]
        archivo = os.path.join(carpeta, f"{nombre}_{count + 1}.jpg")
        if descargar_imagen(url, archivo):
            count += 1
        if count >= imagenes_por_objeto:
            break
    print(f"✅ {count:>3} imgs | {caneca}/{subcategoria} ← '{termino}'")

if __name__ == "__main__":
    tareas = []
    for subcat, info in categorias.items():
        caneca = info["caneca"]
        for termino in info["terminos"]:
            tareas.append((caneca, subcat, termino))

    print(f"📋 Total de búsquedas: {len(tareas)}")
    print(f"📁 Destino: {base_dir}\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(lambda t: descargar_objeto(*t), tareas)

    print("\n🎉 Descarga completada.")