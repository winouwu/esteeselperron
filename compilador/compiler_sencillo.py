#!/usr/bin/env python3

import sys
import re

def interpret_eswino(code):
    """
    Interpreta código .eswino y ejecuta las instrucciones
    """
    # Diccionario para almacenar las variables
    variables = {}
    
    # Valores booleanos para usar en eval
    variables["true"] = True
    variables["false"] = False
    
    # Eliminar comentarios multilínea
    code = re.sub(r'¡.*?!', '', code, flags=re.DOTALL)
    
    # Preparar líneas
    lines = []
    for line in code.splitlines():
        if '$' in line:
            line = line.split('$', 1)[0]
        lines.append(line)
    
    # Índice actual
    i = 0
    
    # Procesar el código línea por línea
    while i < len(lines):
        line = lines[i].strip()
        
        # Imprimir para depurar
        print(f"Procesando línea {i+1}: {line}")
        
        # Ignorar líneas vacías o comentarios
        if not line or line.startswith('//'):
            i += 1
            continue
        
        # Procesar declaración de variable
        alohomora_match = re.match(r'alohomora\s+(\w+)\s*=\s*(.+)', line)
        if alohomora_match:
            var_name = alohomora_match.group(1)
            var_value = alohomora_match.group(2).strip()
            
            try:
                # Procesar según el tipo de valor
                if var_value.startswith('[') and var_value.endswith(']'):
                    # Arreglo
                    variables[var_name] = eval(var_value, {"__builtins__": {}}, variables)
                elif (var_value.startswith('"') and var_value.endswith('"')) or \
                     (var_value.startswith("'") and var_value.endswith("'")):
                    # Cadena
                    variables[var_name] = var_value[1:-1]
                elif var_value.lower() == "true":
                    # Booleano verdadero
                    variables[var_name] = True
                elif var_value.lower() == "false":
                    # Booleano falso
                    variables[var_name] = False
                else:
                    # Expresión
                    variables[var_name] = eval(var_value, {"__builtins__": {}}, variables)
                print(f"Variable '{var_name}' asignada con valor: {variables[var_name]}")
            except Exception as e:
                print(f"Error asignando variable '{var_name}': {e}")
            i += 1
            continue
        
        # Procesar función conjura
        conjura_match = re.match(r'conjura\((.+)\)', line)
        if conjura_match:
            content = conjura_match.group(1).strip()
            
            try:
                # Procesar según el tipo de contenido
                if (content.startswith('"') and content.endswith('"')) or \
                   (content.startswith("'") and content.endswith("'")):
                    # Cadena
                    print(content[1:-1])
                elif content in variables:
                    # Variable
                    value = variables[content]
                    if isinstance(value, bool):
                        print("true" if value else "false")
                    else:
                        print(value)
                else:
                    # Expresión
                    result = eval(content, {"__builtins__": {}}, variables)
                    if isinstance(result, bool):
                        print("true" if result else "false")
                    else:
                        print(result)
            except Exception as e:
                print(f"Error en conjura: {e}")
            i += 1
            continue
        
        # Si llegamos aquí, es una línea no reconocida
        print(f"ADVERTENCIA: Línea no reconocida: {line}")
        i += 1

def main():
    if len(sys.argv) < 2:
        print("Uso: python compiler_sencillo.py archivo.eswino")
        sys.exit(1)
        
    filename = sys.argv[1]
    if not filename.endswith('.eswino'):
        print("Error: El archivo debe tener la extensión .eswino")
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
            print(f"Archivo cargado: {filename}")
            print(f"Tamaño del código: {len(code)} caracteres")
            print("Iniciando interpretación del código...")
            interpret_eswino(code)
            print("Interpretación finalizada con éxito.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al interpretar el archivo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 