import gzip

# Asume que camera_index.h contiene el array index_ov2640_html_gz
with open("camera_index.h", "r") as f:
    content = f.read()

# Extrae los bytes entre llaves {} (simplificado)
start = content.find('{') + 1
end = content.find('}')
bytes_data = bytearray(map(lambda x: int(x.strip(), 16), content[start:end].split(',')))

# Guarda y descomprime
with open("camera_index.html", "wb") as f:
    f.write(gzip.decompress(bytes_data))