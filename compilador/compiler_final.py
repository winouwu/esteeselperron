#!/usr/bin/env python3

import sys
import re

def interpret_eswino(code):
    """
    Interpreta código .eswino y ejecuta las instrucciones
    """
    # Diccionario para almacenar las variables
    variables = {}
    # Diccionario para almacenar las funciones
    funciones = {}
    
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
                
            if current_line.startswith('si ') or current_line.startswith('mientras ') or current_line.startswith('para ') or current_line.startswith('hechizo '):
                depth += 1
            elif current_line == 'fin':
                depth -= 1
                
            i += 1
            if depth == 0:
                return i - 1  # Índice del 'fin'
        
        return i - 1  # En caso de no encontrar 'fin', devolver el último índice
    
    # Función para ejecutar una función definida por el usuario
    def ejecutar_funcion(func_name, args):
        # Verificar si la función existe
        if func_name not in funciones:
            print(f"Error: Función '{func_name}' no definida")
            return None
        
        # Obtener la definición de la función
        func_def = funciones[func_name]
        params = func_def["params"]
        body = func_def["body"]
        
        # Crear un nuevo ámbito para las variables
        old_vars = dict(variables)
        
        # Asignar argumentos a parámetros
        for i, param in enumerate(params):
            if i < len(args):
                variables[param] = args[i]
        
        # Ejecutar el cuerpo de la función
        result = None
        j = 0
        while j < len(body):
            line = body[j].strip()
            
            # Detectar instrucción de retorno
            if line.startswith('regresa '):
                return_match = re.match(r'regresa\s+(.+)', line)
                if return_match:
                    expr = return_match.group(1)
                    try:
                        result = custom_eval(expr, variables)
                        break  # Terminar ejecución de la función
                    except Exception as e:
                        print(f"Error en regresa: {e}")
                        break
            else:
                # Procesar línea normal de la función
                process_line(line, variables, custom_eval, ejecutar_funcion, funciones)
            
            j += 1
        
        # Restaurar el ámbito anterior
        variables.clear()
        variables.update(old_vars)
        
        return result
    
    # Índice actual
    i = 0
    
    # Procesar el código línea por línea
    while i < len(lines):
        line = lines[i].strip()
        
        # Ignorar líneas vacías o comentarios
        if not line or line.startswith('//'):
            i += 1
            continue
        
        # Procesar definición de función
        elif line.startswith('hechizo '):
            # Sintaxis: hechizo nombre_funcion(param1, param2, ...):
            func_match = re.match(r'hechizo\s+(\w+)\s*\((.*?)\):', line)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2).strip()
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                
                # Encontrar el fin de la función
                end_func_idx = find_block_end(i + 1)
                
                # Extraer el cuerpo de la función
                body = []
                j = i + 1
                while j < end_func_idx:
                    body.append(lines[j])
                    j += 1
                
                # Guardar la función
                funciones[func_name] = {
                    "params": params,
                    "body": body
                }
                
                i = end_func_idx + 1  # Continuar después del fin de la función
            else:
                i += 1
        
        # Procesar condicional 'si'
        elif line.startswith('si '):
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
                                process_line(inner_line, variables, custom_eval, ejecutar_funcion, funciones)
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
                                    process_line(inner_line, variables, custom_eval, ejecutar_funcion, funciones)
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
                            process_line(body_line, variables, custom_eval, ejecutar_funcion, funciones)
                    
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
                            process_line(body_line, variables, custom_eval, ejecutar_funcion, funciones)
                    
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
            process_line(line, variables, custom_eval, ejecutar_funcion, funciones)
            i += 1

def process_line(line, variables, custom_eval, ejecutar_funcion=None, funciones=None):
    """Procesa una línea de código eswino"""
    # Declaración de variable
    if line.startswith('alohomora '):
        var_match = re.match(r'alohomora\s+(\w+)\s*=\s*(.+)', line)
        if var_match:
            var_name = var_match.group(1)
            expr = var_match.group(2)
            try:
                variables[var_name] = custom_eval(expr, variables)
            except Exception as e:
                print(f"Error en asignación: {e}")
    
    # Impresión
    elif line.startswith('conjura('):
        print_match = re.match(r'conjura\((.*)\)', line)
        if print_match:
            expr = print_match.group(1)
            try:
                result = custom_eval(expr, variables)
                print(result)
            except Exception as e:
                print(f"Error en conjura: {e}")
    
    # Llamada a función
    elif re.match(r'(\w+)\s*\(', line):
        func_call_match = re.match(r'(\w+)\s*\((.*?)\)', line)
        if func_call_match:
            func_name = func_call_match.group(1)
            args_str = func_call_match.group(2).strip()
            
            # Evaluar los argumentos
            args = []
            if args_str:
                for arg in args_str.split(','):
                    try:
                        arg_value = custom_eval(arg.strip(), variables)
                        args.append(arg_value)
                    except Exception as e:
                        print(f"Error evaluando argumento: {e}")
                        args.append(None)
            
            # Ejecutar la función
            if func_name in variables and callable(variables[func_name]):
                # Si es una función predefinida
                try:
                    result = variables[func_name](*args)
                    return result
                except Exception as e:
                    print(f"Error al llamar a la función: {e}")
            elif ejecutar_funcion and funciones and func_name in funciones:
                # Si es una función definida por el usuario
                try:
                    return ejecutar_funcion(func_name, args)
                except Exception as e:
                    print(f"Error al ejecutar la función: {e}")

def main():
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("Uso: python compiler.py <archivo.eswino>")
        sys.exit(1)
    
    # Abrir el archivo
    try:
        with open(sys.argv[1], 'r') as file:
            code = file.read()
            interpret_eswino(code)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{sys.argv[1]}'")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main() 