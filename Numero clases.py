import os
import re

# Pon aquí la ruta de la carpeta con tus ~40,000 imágenes
ruta_imagenes = "D:\Residuos\Caneca_verde"

clases_detectadas = set()

# Expresión regular para quitar los números al final y la extensión (.jpg, .png, etc.)
# Ejemplo: "cardboard_1.jpg" -> "cardboard"
patron = re.compile(r'^(.*?)(?:_\d+)?\.[a-zA-Z0-9]+$')

for nombre_archivo in os.listdir(ruta_imagenes):
    coincidencia = patron.match(nombre_archivo)
    if coincidencia:
        clase = coincidencia.group(1)
        clases_detectadas.add(clase)

lista_clases = sorted(list(clases_detectadas))

print(f"Total de clases encontradas: {len(lista_clases)}\n")
print("Copia esta lista y pégamela aquí:\n")
for c in lista_clases:
    print(c)