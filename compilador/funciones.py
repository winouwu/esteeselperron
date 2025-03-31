#!/usr/bin/env python3

import re
import sys

def compile_eswino(filename):
    """Compila un archivo eswino"""
    # Leer el archivo
    with open(filename, 'r', encoding='utf-8') as file:
        code = file.read()
    
    print("Archivo cargado correctamente.")
    
    # Variables y funciones globales
    variables = {
        'true': True,
        'false': False
    }
    funciones = {}
    
    # Eliminar comentarios
    code = re.sub(r'//.*', '', code)
    
    # Dividir el código en líneas
    lines = [line.strip() for line in code.split('\n')]
    
    print(f"Total de líneas: {len(lines)}")
    
    # Función para encontrar el final de un bloque
    def find_block_end(start_index, indent_level=0):
        i = start_index
        while i < len(lines):
            if lines[i].strip() == 'fin':
                return i
            i += 1
        return -1
    
    # Evaluar expresiones
    def evaluar(expr):
        try:
            # Si la expresión contiene una concatenación de strings
            if "+" in expr and ('"' in expr or "'" in expr or any(isinstance(variables.get(v), str) for v in re.findall(r'\b\w+\b', expr) if v in variables)):
                parts = expr.split('+')
                result = ""
                for part in parts:
                    part = part.strip()
                    if part.startswith('"') and part.endswith('"'):
                        result += part[1:-1]
                    elif part.startswith("'") and part.endswith("'"):
                        result += part[1:-1]
                    elif part in variables:
                        result += str(variables[part])
                    else:
                        try:
                            val = eval(part, {"__builtins__": {}}, variables)
                            result += str(val)
                        except:
                            result += part
                return result
            # Si no hay concatenación, evaluar normalmente
            return eval(expr, {"__builtins__": {}}, variables)
        except Exception as e:
            print(f"Error al evaluar '{expr}': {e}")
            return None
    
    # Ejecutar una función
    def ejecutar_funcion(nombre, args):
        print(f"Ejecutando función: {nombre} con argumentos: {args}")
        if nombre not in funciones:
            print(f"Error: Función '{nombre}' no definida")
            return None
        
        # Guardar el estado actual de las variables
        old_vars = variables.copy()
        
        # Configurar los parámetros
        func_info = funciones[nombre]
        params = func_info['params']
        body = func_info['body']
        
        # Asignar los argumentos a los parámetros
        for i, param in enumerate(params):
            if i < len(args):
                variables[param] = args[i]
        
        # Ejecutar el cuerpo de la función
        result = None
        i = 0
        while i < len(body):
            line = body[i]
            print(f"Ejecutando línea de función: {line}")
            
            # Verificar si es un return
            if line.startswith('regresa '):
                expr = line[8:].strip()
                result = evaluar(expr)
                print(f"Retornando valor: {result}")
                break
            
            # Procesar línea normal
            i = ejecutar_linea(line, body, i)
            i += 1
        
        # Restaurar el estado anterior
        variables.clear()
        variables.update(old_vars)
        
        return result
    
    # Procesar una línea de código
    def ejecutar_linea(line, lines=None, current_index=0):
        # Ignorar líneas vacías
        if not line.strip():
            return current_index
        
        print(f"Procesando línea: {line}")
        
        # Definición de función
        if line.startswith('hechizo '):
            match = re.match(r'hechizo\s+(\w+)\s*\((.*?)\):', line)
            if match:
                func_name = match.group(1)
                params_str = match.group(2)
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                
                # Encontrar el cuerpo de la función
                body_start = current_index + 1
                body_end = find_block_end(body_start)
                
                if body_end == -1:
                    print(f"Error: No se encontró el fin de la función '{func_name}'")
                    return len(lines) - 1
                
                # Guardar la función
                funciones[func_name] = {
                    'params': params,
                    'body': lines[body_start:body_end]
                }
                
                print(f"Función definida: {func_name} con parámetros: {params}")
                
                return body_end
        
        # Asignación de variable
        elif line.startswith('alohomora '):
            match = re.match(r'alohomora\s+(\w+)\s*=\s*(.*)', line)
            if match:
                var_name = match.group(1)
                expr = match.group(2)
                variables[var_name] = evaluar(expr)
                print(f"Variable asignada: {var_name} = {variables[var_name]}")
        
        # Impresión
        elif line.startswith('conjura('):
            match = re.match(r'conjura\((.*)\)', line)
            if match:
                expr = match.group(1)
                result = evaluar(expr)
                print(f"Resultado de conjura: {result}")
        
        # Condicional
        elif line.startswith('si '):
            match = re.match(r'si\s+(.*?):', line)
            if match and lines:
                condition = match.group(1)
                result = evaluar(condition)
                print(f"Evaluando condición: {condition} = {result}")
                
                if result:
                    # Procesar bloque si
                    i = current_index + 1
                    while i < len(lines) and lines[i] != 'fin' and not lines[i].startswith('sino:'):
                        i = ejecutar_linea(lines[i], lines, i)
                        i += 1
                else:
                    # Buscar bloque sino si existe
                    i = current_index + 1
                    while i < len(lines) and not lines[i].startswith('sino:') and lines[i] != 'fin':
                        i += 1
                    
                    if i < len(lines) and lines[i].startswith('sino:'):
                        i += 1
                        while i < len(lines) and lines[i] != 'fin':
                            i = ejecutar_linea(lines[i], lines, i)
                            i += 1
                
                # Encontrar el fin del bloque si-sino
                i = current_index + 1
                depth = 1
                while i < len(lines) and depth > 0:
                    if lines[i].startswith('si '):
                        depth += 1
                    elif lines[i] == 'fin':
                        depth -= 1
                    i += 1
                
                return i - 1
        
        # Ciclo mientras
        elif line.startswith('mientras '):
            match = re.match(r'mientras\s+(.*?):', line)
            if match and lines:
                condition = match.group(1)
                
                # Encontrar el cuerpo del ciclo
                body_start = current_index + 1
                body_end = find_block_end(body_start)
                
                if body_end == -1:
                    print("Error: No se encontró el fin del ciclo mientras")
                    return len(lines) - 1
                
                # Ejecutar el ciclo
                iterations = 0
                max_iterations = 1000
                
                while evaluar(condition) and iterations < max_iterations:
                    i = body_start
                    while i < body_end:
                        i = ejecutar_linea(lines[i], lines, i)
                        i += 1
                    
                    iterations += 1
                
                if iterations >= max_iterations:
                    print("Advertencia: Se alcanzó el límite de iteraciones para el ciclo mientras")
                
                return body_end
        
        # Ciclo para
        elif line.startswith('para '):
            match = re.match(r'para\s+(\w+)\s+en\s+rango\((.*?)\):', line)
            if match and lines:
                var_name = match.group(1)
                range_params = match.group(2).split(',')
                
                # Determinar inicio, fin y paso
                start, end, step = 0, 0, 1
                
                try:
                    if len(range_params) == 1:
                        end_val = evaluar(range_params[0].strip())
                        if end_val is None:
                            print(f"Error: El valor de fin para el rango no puede ser None")
                            return current_index + 1
                        end = int(end_val)
                    elif len(range_params) == 2:
                        start_val = evaluar(range_params[0].strip())
                        end_val = evaluar(range_params[1].strip())
                        if start_val is None or end_val is None:
                            print(f"Error: Los valores de inicio o fin para el rango no pueden ser None")
                            return current_index + 1
                        start = int(start_val)
                        end = int(end_val)
                    elif len(range_params) == 3:
                        start_val = evaluar(range_params[0].strip())
                        end_val = evaluar(range_params[1].strip())
                        step_val = evaluar(range_params[2].strip())
                        if start_val is None or end_val is None or step_val is None:
                            print(f"Error: Los valores de inicio, fin o paso para el rango no pueden ser None")
                            return current_index + 1
                        start = int(start_val)
                        end = int(end_val)
                        step = int(step_val)
                    
                    # Encontrar el cuerpo del ciclo
                    body_start = current_index + 1
                    body_end = find_block_end(body_start)
                    
                    if body_end == -1:
                        print("Error: No se encontró el fin del ciclo para")
                        return len(lines) - 1
                    
                    print(f"Ciclo para: rango({start}, {end}, {step})")
                    
                    # Ejecutar el ciclo
                    for i in range(start, end, step):
                        variables[var_name] = i
                        
                        j = body_start
                        while j < body_end:
                            j = ejecutar_linea(lines[j], lines, j)
                            j += 1
                    
                    return body_end
                except Exception as e:
                    print(f"Error en ciclo para: {e}")
                    return find_block_end(current_index + 1)
        
        # Llamada a función
        elif re.match(r'(\w+)\s*\(', line):
            match = re.match(r'(\w+)\s*\((.*?)\)', line)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                
                # Evaluar argumentos
                args = []
                if args_str.strip():
                    for arg in args_str.split(','):
                        args.append(evaluar(arg.strip()))
                
                # Llamar a la función
                print(f"Llamando a función: {func_name} con argumentos: {args}")
                return_val = ejecutar_funcion(func_name, args)
                if return_val is not None:
                    print(f"Valor devuelto por la función: {return_val}")
                return current_index
        
        return current_index
    
    # Primer paso: Procesar todas las definiciones de funciones
    print("=== Procesando definiciones de funciones ===")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('hechizo '):
            i = ejecutar_linea(line, lines, i)
        i += 1
    
    print(f"Funciones definidas: {list(funciones.keys())}")
    
    # Segundo paso: Procesar el resto de las líneas
    print("=== Procesando el resto del código ===")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith('hechizo ') and line.strip():
            i = ejecutar_linea(line, lines, i)
        i += 1

def main():
    if len(sys.argv) != 2:
        print("Uso: python funciones.py <archivo.eswino>")
        sys.exit(1)
    
    try:
        compile_eswino(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 