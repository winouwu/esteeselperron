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
    
    # Función para sobrescribir el operador + para manejar concatenación de strings
    def custom_eval(expr, vars_dict):
        # Si hay operaciones de concatenación con cadenas, procesar manualmente
        if "+" in expr and ('"' in expr or "'" in expr or any(isinstance(vars_dict.get(var), str) for var in vars_dict)):
            # Dividir la expresión por el operador +
            parts = expr.split("+")
            result = ""
            
            for part in parts:
                part = part.strip()
                # Evaluar cada parte individualmente
                if part.startswith('"') and part.endswith('"'):
                    # Es una cadena literal
                    result += part[1:-1]
                elif part.startswith("'") and part.endswith("'"):
                    # Es una cadena literal con comillas simples
                    result += part[1:-1]
                elif part in vars_dict:
                    # Es una variable
                    result += str(vars_dict[part])
                else:
                    # Es una expresión
                    try:
                        val = eval(part, {"__builtins__": {}}, vars_dict)
                        result += str(val)
                    except:
                        # Si falla, simplemente agregar la parte sin procesar
                        result += part
            
            return result
        else:
            # Si no hay concatenación de cadenas, usar eval normal
            return eval(expr, {"__builtins__": {}}, vars_dict)
    
    # Eliminar comentarios multilínea
    code = re.sub(r'¡.*?!', '', code, flags=re.DOTALL)
    
    # Preparar líneas
    lines = []
    for line in code.splitlines():
        if '$' in line:
            line = line.split('$', 1)[0]
        lines.append(line)
    
    # Función para encontrar el fin de un bloque
    def find_block_end(start_index, block_type="any"):
        i = start_index
        depth = 1
        
        while i < len(lines) and depth > 0:
            current_line = lines[i].strip()
            
            if block_type == "if" and current_line == "sino:" and depth == 1:
                return i  # Si estamos buscando el fin de un if, sino: es un terminador a nivel 1
                
            if current_line.startswith('si ') or current_line.startswith('mientras ') or current_line.startswith('para '):
                depth += 1
            elif current_line == 'fin':
                depth -= 1
                
            i += 1
            if depth == 0:
                return i - 1  # Índice del 'fin'
        
        return i - 1  # En caso de no encontrar 'fin', devolver el último índice
    
    # Índice actual
    i = 0
    
    # Procesar el código línea por línea
    while i < len(lines):
        line = lines[i].strip()
        
        # Ignorar líneas vacías o comentarios
        if not line or line.startswith('//'):
            i += 1
            continue
        
        # Procesar condicional 'si'
        if line.startswith('si '):
            condition_match = re.match(r'si\s+(.+):', line)
            if condition_match:
                condition = condition_match.group(1)
                
                # Evaluar la condición
                try:
                    condition_result = eval(condition, {"__builtins__": {}}, variables)
                    
                    # Encontrar dónde termina este bloque si
                    end_if_idx = find_block_end(i + 1, "if")
                    
                    if condition_result:
                        # Ejecutar el bloque si
                        j = i + 1
                        while j < end_if_idx:
                            inner_line = lines[j].strip()
                            if inner_line and not inner_line.startswith('//') and inner_line != 'fin' and inner_line != 'sino:':
                                process_line(inner_line, variables, custom_eval)
                            j += 1
                        
                        # Saltar el bloque sino si existe
                        if end_if_idx < len(lines) and lines[end_if_idx].strip() == 'sino:':
                            end_block_idx = find_block_end(end_if_idx + 1)
                            i = end_block_idx + 1  # Saltar después del fin del bloque sino
                        else:
                            i = end_if_idx + 1  # Saltar después del fin
                    else:
                        # Condición falsa, buscar 'sino:'
                        if end_if_idx < len(lines) and lines[end_if_idx].strip() == 'sino:':
                            # Ejecutar el bloque sino
                            j = end_if_idx + 1
                            end_sino_idx = find_block_end(j)
                            
                            while j < end_sino_idx:
                                inner_line = lines[j].strip()
                                if inner_line and not inner_line.startswith('//') and inner_line != 'fin':
                                    process_line(inner_line, variables, custom_eval)
                                j += 1
                            
                            i = end_sino_idx + 1  # Continuar después del fin del bloque sino
                        else:
                            i = end_if_idx + 1  # Saltar al fin del bloque if
                except Exception as e:
                    print(f"Error evaluando condición: {e}")
                    i = find_block_end(i + 1) + 1  # Saltar el bloque completo
            else:
                i += 1
        
        # Procesar ciclo 'mientras'
        elif line.startswith('mientras '):
            condition_match = re.match(r'mientras\s+(.+):', line)
            if condition_match:
                condition = condition_match.group(1)
                
                # Encontrar el fin del bloque mientras
                end_while_idx = find_block_end(i + 1)
                
                # Extraer las líneas del cuerpo del ciclo para evitar ciclos infinitos
                while_body = []
                j = i + 1
                while j < end_while_idx:
                    inner_line = lines[j].strip()
                    if inner_line and not inner_line.startswith('//') and inner_line != 'fin':
                        while_body.append(inner_line)
                    j += 1
                
                # Ejecutar el ciclo con protección contra infinitos
                try:
                    iteration_count = 0
                    max_iterations = 1000
                    
                    while eval(condition, {"__builtins__": {}}, variables):
                        iteration_count += 1
                        if iteration_count > max_iterations:
                            print("¡Advertencia! Ciclo infinito detectado. Ejecución interrumpida.")
                            break
                        
                        # Ejecutar cada línea del cuerpo del ciclo
                        for body_line in while_body:
                            process_line(body_line, variables, custom_eval)
                    
                    i = end_while_idx + 1  # Continuar después del fin del ciclo
                except Exception as e:
                    print(f"Error en ciclo mientras: {e}")
                    i = end_while_idx + 1  # Saltar el bloque completo
            else:
                i += 1

        # Procesar ciclo 'para' (for)
        elif line.startswith('para '):
            # Sintaxis: para variable en rango(inicio, fin, paso):
            for_match = re.match(r'para\s+(\w+)\s+en\s+rango\(([^,]+)(?:,\s*([^,]+))?(?:,\s*([^)]+))?\):', line)
            if for_match:
                var_name = for_match.group(1)
                start_val = for_match.group(2)
                end_val = for_match.group(3)
                step_val = for_match.group(4)
                
                try:
                    # Evaluar parámetros del rango
                    if end_val is None:
                        # Si solo hay un valor, ese es el fin y el inicio es 0
                        start = 0
                        end = eval(start_val, {"__builtins__": {}}, variables)
                    else:
                        # Si hay dos valores, son inicio y fin
                        start = eval(start_val, {"__builtins__": {}}, variables)
                        end = eval(end_val, {"__builtins__": {}}, variables)
                    
                    # El paso es opcional, por defecto es 1
                    step = 1
                    if step_val is not None:
                        step = eval(step_val, {"__builtins__": {}}, variables)
                    
                    # Encontrar el fin del bloque para
                    end_for_idx = find_block_end(i + 1)
                    
                    # Extraer las líneas del cuerpo del ciclo
                    for_body = []
                    j = i + 1
                    while j < end_for_idx:
                        inner_line = lines[j].strip()
                        if inner_line and not inner_line.startswith('//') and inner_line != 'fin':
                            for_body.append(inner_line)
                        j += 1
                    
                    # Ejecutar el ciclo para
                    for value in range(start, end, step):
                        variables[var_name] = value
                        
                        # Ejecutar cada línea del cuerpo del ciclo
                        for body_line in for_body:
                            process_line(body_line, variables, custom_eval)
                    
                    i = end_for_idx + 1  # Continuar después del fin del ciclo
                except Exception as e:
                    print(f"Error en ciclo para: {e}")
                    i = find_block_end(i + 1) + 1  # Saltar el bloque completo
            else:
                i += 1
        
        # Saltar líneas 'sino:' y 'fin' sueltas
        elif line == 'sino:' or line == 'fin':
            i += 1
        
        # Procesar líneas normales
        else:
            process_line(line, variables, custom_eval)
            i += 1

def process_line(line, variables, custom_eval):
    """Procesa una línea de código eswino"""
    line = line.strip()
    
    # Ignorar líneas vacías o comentarios
    if not line or line.startswith('//'):
        return
    
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
            # Verificar si es una expresión con concatenación de cadenas
            elif "+" in var_value and ('"' in var_value or "'" in var_value or any(isinstance(variables.get(var), str) for var in variables)):
                variables[var_name] = custom_eval(var_value, variables)
            else:
                # Expresión normal
                variables[var_name] = eval(var_value, {"__builtins__": {}}, variables)
        except Exception as e:
            print(f"Error asignando variable '{var_name}': {e}")
        return
    
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
                elif isinstance(value, list):
                    # Si es una lista, dar formato especial
                    elements = [str(e) if not isinstance(e, bool) else ("true" if e else "false") for e in value]
                    print(f"[{', '.join(elements)}]")
                else:
                    print(value)
            elif "+" in content:
                # Posible concatenación
                result = custom_eval(content, variables)
                print(result)
            else:
                # Expresión
                result = eval(content, {"__builtins__": {}}, variables)
                if isinstance(result, bool):
                    print("true" if result else "false")
                else:
                    print(result)
        except Exception as e:
            print(f"Error en conjura: {e}")
        return

def main():
    if len(sys.argv) < 2:
        print("Uso: python compiler_final.py archivo.eswino")
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