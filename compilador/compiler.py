#!/usr/bin/env python3

import sys
import re

def interpret_eswino(code):
    """
    Interpreta código .eswino y ejecuta las instrucciones
    """
    # Buscar llamadas a la función conjura
    conjura_pattern = r'conjura\(\s*"([^"]*)"\s*\)'
    matches = re.findall(conjura_pattern, code)
    
    # Ejecutar cada función conjura encontrada
    for text in matches:
        print(text)

def main():
    if len(sys.argv) < 2:
        print("Uso: python compiler.py archivo.eswino")
        sys.exit(1)
        
    filename = sys.argv[1]
    if not filename.endswith('.eswino'):
        print("Error: El archivo debe tener la extensión .eswino")
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
            interpret_eswino(code)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al interpretar el archivo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 