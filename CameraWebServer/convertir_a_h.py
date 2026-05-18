import gzip
import os

def convert_html_to_h(html_file_path, h_file_name, variable_name):
        try:
            with open(html_file_path, 'rb') as f_html:
                html_content = f_html.read()

            compressed_data = gzip.compress(html_content)

            compressed_len = len(compressed_data)

            h_content = f"#define {variable_name}_len {compressed_len}\n"
            h_content += f"const uint8_t {variable_name}[] = {{\n"

            hex_bytes = []
            for i, byte in enumerate(compressed_data):
                hex_bytes.append(f"0x{byte:02X}")
                if (i + 1) % 16 == 0:
                    h_bytes = ", ".join(hex_bytes)
                    h_content += f" {h_bytes},\n"
                    hex_bytes = []
            if hex_bytes:
                h_bytes = ", ".join(hex_bytes)
                h_content += f" {h_bytes}\n"
            else:
                h_content = h_content.rstrip(',\n') + '\n'
            h_content += "};\n"

            with open(h_file_name, 'w') as f_h:
                f_h.write(h_content)

            print(f"Archivo '{h_file_name}' generado exitosamente con {compressed_len} bytes.")

        except FileNotFoundError:
            print(f"Error: El archivo HTML '{html_file_path}' no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
        html_input_file = "camera_index.html"
        h_output_file = "camera_index.h"
        variable_name = "index_ov2640_html_gz"

        convert_html_to_h(html_input_file, h_output_file, variable_name)