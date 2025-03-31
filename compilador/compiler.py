#!/usr/bin/env python3

import sys
import re

def interpret_eswino(code):
    """
    Interpreta código .eswino y ejecuta las instrucciones
    """
    # Diccionario para almacenar las variables
    variables = {}
    
    # Procesar el código línea por línea
    for line in code.splitlines():
        line = line.strip()
        if not line or line.startswith('//'):
            continue
            
        # Buscar declaraciones de variables con alohomora
        alohomora_match = re.match(r'alohomora\s+(\w+)\s*=\s*(.+)', line)
        if alohomora_match:
            var_name = alohomora_match.group(1)
            var_value = alohomora_match.group(2).strip()
            
            # Evaluar el valor de la variable (números, cadenas, etc.)
            try:
                # Si es una cadena entre comillas
                if (var_value.startswith('"') and var_value.endswith('"')) or \
                   (var_value.startswith("'") and var_value.endswith("'")):
                    variables[var_name] = var_value[1:-1]
                else:
                    # Intentar evaluar como expresión (número, operación, etc.)
                    variables[var_name] = eval(var_value, {"__builtins__": {}}, variables)
            except:
                variables[var_name] = var_value
            continue
            
        # Buscar llamadas a la función conjura con variables o texto
        conjura_match = re.match(r'conjura\((.+)\)', line)
        if conjura_match:
            content = conjura_match.group(1).strip()
            
            # Si es una cadena entre comillas
            if (content.startswith('"') and content.endswith('"')) or \
               (content.startswith("'") and content.endswith("'")):
                print(content[1:-1])
            # Si es una variable
            elif content in variables:
                print(variables[content])
            else:
                try:
                    # Intentar evaluar como expresión
                    result = eval(content, {"__builtins__": {}}, variables)
                    print(result)
                except:
                    print(f"Error: No se pudo evaluar '{content}'")

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