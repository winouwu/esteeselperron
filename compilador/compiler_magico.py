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

    # Función para manejar errores
    def conjuro_fallido(mensaje):
        print(f"¡Caray! Conjuro fallido: {mensaje}")
        return None
    
    # Funciones mágicas para listas
    def agregar_elemento(lista, elemento):
        if not isinstance(lista, list):
            return conjuro_fallido("No es un pergamino (lista)")
        lista.append(elemento)
        return lista
    
    def extraer_elemento(lista, indice=None):
        if not isinstance(lista, list):
            return conjuro_fallido("No es un pergamino (lista)")
        if not lista:
            return conjuro_fallido("¡El pergamino está vacío!")
        
        if indice is None:  # Por defecto, extraer el último
            return lista.pop()
        
        try:
            return lista.pop(indice)
        except IndexError:
            return conjuro_fallido("¡Índice fuera de los límites del pergamino!")
    
    def primer_elemento(lista):
        if not isinstance(lista, list):
            return conjuro_fallido("No es un pergamino (lista)")
        if not lista:
            return conjuro_fallido("¡El pergamino está vacío!")
        
        return lista[0]
    
    def ultimo_elemento(lista):
        if not isinstance(lista, list):
            return conjuro_fallido("No es un pergamino (lista)")
        if not lista:
            return conjuro_fallido("¡El pergamino está vacío!")
        
        return lista[-1]
    
    # Función para concatenar cualquier tipo
    def concatenar_magico(a, b):
        return str(a) + str(b)
    
    # Registrar funciones mágicas
    variables["agregar_magia"] = agregar_elemento
    variables["extraer_magia"] = extraer_elemento
    variables["primer_secreto"] = primer_elemento
    variables["ultimo_secreto"] = ultimo_elemento
    variables["__concat__"] = concatenar_magico
    
    # Eliminar comentarios multilínea
    code = re.sub(r'¡.*?!', '', code, flags=re.DOTALL)
    
    # Preparar líneas
    lines = []
    for line in code.splitlines():
        if '$' in line:
            line = line.split('$', 1)[0]
        lines.append(line)
    
    # Función para evaluar expresiones con soporte para concatenación
    def custom_eval(expr, vars_dict):
        try:
            # Detectar llamadas a métodos mágicos
            method_match = re.search(r'(\w+)\.(\w+)\((.*?)\)', expr)
            if method_match:
                obj_name = method_match.group(1)
                method_name = method_match.group(2)
                args_str = method_match.group(3).strip()
                
                # Verificar si el objeto existe
                if obj_name not in vars_dict:
                    print(f"¡Caray! No se encontró el objeto '{obj_name}'")
                    return expr
                
                obj = vars_dict[obj_name]
                
                # Mapear nombres mágicos a métodos reales
                method_map = {
                    "agregar": "agregar_magia",
                    "extraer": "extraer_magia",
                    "primero": "primer_secreto",
                    "ultimo": "ultimo_secreto"
                }
                
                if method_name in method_map:
                    magic_method = method_map[method_name]
                    
                    # Preparar argumentos
                    args = []
                    args.append(obj)  # El objeto como primer argumento
                    
                    if args_str:
                        for arg in args_str.split(','):
                            arg = arg.strip()
                            try:
                                # Evaluar el argumento como literal o expresión
                                if (arg.startswith('"') and arg.endswith('"')) or \
                                   (arg.startswith("'") and arg.endswith("'")):
                                    args.append(arg[1:-1])  # String literal
                                else:
                                    # Intentar evaluar como expresión
                                    args.append(eval(arg, {"__builtins__": {}}, vars_dict))
                            except Exception as e:
                                print(f"¡Caray! Error al evaluar argumento: {e}")
                                return expr
                    
                    # Llamar al método mágico
                    try:
                        result = vars_dict[magic_method](*args)
                        vars_dict[obj_name] = obj  # Actualizar el objeto si fue modificado
                        return result
                    except Exception as e:
                        print(f"¡Caray! Error al llamar al método mágico: {e}")
                        return expr
                else:
                    print(f"¡Caray! Método mágico desconocido: '{method_name}'")
                    return expr
            
            # Verificar si es una expresión con operador +
            if '+' in expr and not expr.startswith('+') and not expr.endswith('+'):
                # Buscar strings en la expresión
                has_string = False
                for part in re.split(r'[+\-*/()]', expr):
                    part = part.strip()
                    if part and (
                       (part.startswith('"') and part.endswith('"')) or 
                       (part.startswith("'") and part.endswith("'")) or
                       (part in vars_dict and isinstance(vars_dict[part], str))):
                        has_string = True
                        break
                
                if has_string:
                    # Dividir por el operador + y evaluar cada parte por separado
                    parts = []
                    for part in expr.split('+'):
                        part = part.strip()
                        if not part:
                            continue
                        try:
                            # Evaluar cada parte
                            if (part.startswith('"') and part.endswith('"')) or \
                               (part.startswith("'") and part.endswith("'")):
                                parts.append(part[1:-1])  # String literal
                            else:
                                # Verificar si es una llamada a método
                                method_match = re.search(r'(\w+)\.(\w+)\((.*?)\)', part)
                                if method_match:
                                    # Procesar la llamada a método recursivamente
                                    parts.append(custom_eval(part, vars_dict))
                                else:
                                    # Evaluar como expresión normal
                                    parts.append(eval(part, {"__builtins__": {}}, vars_dict))
                        except:
                            parts.append(part)  # Si falla, mantener la parte como está
                    
                    # Concatenar todas las partes como strings
                    result = ""
                    for part in parts:
                        result += str(part)
                    return result
            
            # Evaluar normalmente si no es concatenación ni método mágico
            return eval(expr, {"__builtins__": {}}, vars_dict)
        except Exception as e:
            print(f"Error evaluando expresión: {e}")
            return expr  # Devolver la expresión sin procesar
    
    # Función para encontrar el fin de un bloque
    def find_block_end(start_index, block_type="any"):
        i = start_index
        depth = 1
        
        while i < len(lines) and depth > 0:
            current_line = lines[i].strip()
            
            if block_type == "if" and current_line == "sino:" and depth == 1:
                return i  # Si estamos buscando el fin de un if, sino: es un terminador a nivel 1
                
            if current_line.startswith('si ') or current_line.startswith('mientras '):
                depth += 1
            elif current_line == 'fin':
                depth -= 1
                
            i += 1
            if depth == 0:
                return i - 1  # Índice del 'fin'
        
        return i - 1  # En caso de no encontrar 'fin', devolver el último índice
    
    # Procesar línea
    def process_line(line, variables):
        """Procesa una línea de código eswino"""
        line = line.strip()
        
        # Para depuración (comentado para tener una salida más limpia)
        # print(f"Procesando: {line}")
        
        # Ignorar líneas vacías o comentarios
        if not line or line.startswith('//'):
            return
        
        # Procesar llamadas a métodos mágicos
        method_match = re.match(r'(\w+)\.(\w+)\((.*?)\)', line)
        if method_match:
            obj_name = method_match.group(1)
            method_name = method_match.group(2)
            
            # Verificar si el objeto existe
            if obj_name not in variables:
                print(f"¡Caray! No se encontró el objeto '{obj_name}'")
                return
            
            obj = variables[obj_name]
            
            # Mapear nombres mágicos a métodos reales
            method_map = {
                "agregar": "agregar_magia",
                "extraer": "extraer_magia",
                "primero": "primer_secreto",
                "ultimo": "ultimo_secreto"
            }
            
            if method_name in method_map:
                magic_method = method_map[method_name]
                args_str = method_match.group(3).strip()
                
                # Preparar argumentos
                args = []
                args.append(obj)  # El objeto como primer argumento
                
                if args_str:
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        try:
                            # Evaluar el argumento
                            if (arg.startswith('"') and arg.endswith('"')) or \
                               (arg.startswith("'") and arg.endswith("'")):
                                args.append(arg[1:-1])  # String literal
                            else:
                                args.append(custom_eval(arg, variables))
                        except Exception as e:
                            print(f"¡Caray! Error al evaluar argumento: {e}")
                            return
                
                # Llamar al método mágico
                try:
                    result = variables[magic_method](*args)
                    variables[obj_name] = obj  # Actualizar el objeto si fue modificado
                    return
                except Exception as e:
                    print(f"¡Caray! Error al llamar al método mágico: {e}")
                    return
            else:
                print(f"¡Caray! Método mágico desconocido: '{method_name}'")
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
                    variables[var_name] = custom_eval(var_value, variables)
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
                    variables[var_name] = custom_eval(var_value, variables)
            except Exception as e:
                print(f"Error asignando variable '{var_name}': {e}")
            return
        
        # Procesar asignación de resultado de método mágico
        method_assign_match = re.match(r'alohomora\s+(\w+)\s*=\s*(\w+)\.(\w+)\((.*?)\)', line)
        if method_assign_match:
            var_name = method_assign_match.group(1)
            obj_name = method_assign_match.group(2)
            method_name = method_assign_match.group(3)
            args_str = method_assign_match.group(4).strip()
            
            # Verificar si el objeto existe
            if obj_name not in variables:
                print(f"¡Caray! No se encontró el objeto '{obj_name}'")
                return
            
            obj = variables[obj_name]
            
            # Mapear nombres mágicos a métodos reales
            method_map = {
                "agregar": "agregar_magia",
                "extraer": "extraer_magia",
                "primero": "primer_secreto",
                "ultimo": "ultimo_secreto"
            }
            
            if method_name in method_map:
                magic_method = method_map[method_name]
                
                # Preparar argumentos
                args = []
                args.append(obj)  # El objeto como primer argumento
                
                if args_str:
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        try:
                            # Evaluar el argumento
                            if (arg.startswith('"') and arg.endswith('"')) or \
                               (arg.startswith("'") and arg.endswith("'")):
                                args.append(arg[1:-1])  # String literal
                            else:
                                args.append(custom_eval(arg, variables))
                        except Exception as e:
                            print(f"¡Caray! Error al evaluar argumento: {e}")
                            return
                
                # Llamar al método mágico y asignar resultado
                try:
                    result = variables[magic_method](*args)
                    variables[obj_name] = obj  # Actualizar el objeto si fue modificado
                    variables[var_name] = result  # Asignar el resultado a la variable
                except Exception as e:
                    print(f"¡Caray! Error al llamar al método mágico: {e}")
                return
            else:
                print(f"¡Caray! Método mágico desconocido: '{method_name}'")
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
                    print(f">>> {content[1:-1]}")
                elif content in variables:
                    # Variable
                    value = variables[content]
                    if isinstance(value, bool):
                        print(f">>> {'true' if value else 'false'}")
                    else:
                        print(f">>> {value}")
                else:
                    # Expresión
                    result = custom_eval(content, variables)
                    if isinstance(result, bool):
                        print(f">>> {'true' if result else 'false'}")
                    else:
                        print(f">>> {result}")
            except Exception as e:
                print(f"Error en conjura: {e}")
            return
        
        # Si llegamos aquí, es una línea no reconocida
        print(f"ADVERTENCIA: Línea no reconocida: {line}")
    
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
                    condition_result = custom_eval(condition, variables)
                    
                    # Encontrar dónde termina este bloque si
                    end_if_idx = find_block_end(i + 1, "if")
                    
                    if condition_result:
                        # Ejecutar el bloque si
                        j = i + 1
                        while j < end_if_idx:
                            inner_line = lines[j].strip()
                            if inner_line and not inner_line.startswith('//') and inner_line != 'fin' and inner_line != 'sino:':
                                process_line(inner_line, variables)
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
                                    process_line(inner_line, variables)
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
                
                # Extraer las líneas del cuerpo del ciclo
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
                    
                    while custom_eval(condition, variables):
                        iteration_count += 1
                        if iteration_count > max_iterations:
                            print("¡Advertencia! Ciclo infinito detectado. Ejecución interrumpida.")
                            break
                        
                        # Ejecutar cada línea del cuerpo del ciclo
                        for body_line in while_body:
                            process_line(body_line, variables)
                    
                    i = end_while_idx + 1  # Continuar después del fin del ciclo
                except Exception as e:
                    print(f"Error en ciclo mientras: {e}")
                    i = end_while_idx + 1  # Saltar el bloque completo
            else:
                i += 1
        
        # Saltar líneas 'sino:' y 'fin' sueltas
        elif line == 'sino:' or line == 'fin':
            i += 1
        
        # Procesar líneas normales
        else:
            process_line(line, variables)
            i += 1

def main():
    if len(sys.argv) < 2:
        print("Uso: python compiler_magico.py archivo.eswino")
        sys.exit(1)
        
    filename = sys.argv[1]
    if not filename.endswith('.eswino'):
        print("Error: El archivo debe tener la extensión .eswino")
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
            print(f"\n=== Iniciando interpretación del archivo: {filename} ===")
            print(f"Tamaño del código: {len(code)} caracteres")
            interpret_eswino(code)
            print("\n=== Interpretación finalizada con éxito ===")
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