#!/usr/bin/env python3

import sys
import re

def compilar_eswino(codigo):
    """Compilador simple para el lenguaje eswino"""
    # Limpiar comentarios
    codigo = re.sub(r'¡.*?!', '', codigo, flags=re.DOTALL)
    
    # Separar líneas y quitar comentarios de una línea
    lineas = []
    for linea in codigo.splitlines():
        if '$' in linea:
            linea = linea.split('$', 1)[0]
        lineas.append(linea)
    
    # Variables
    variables = {
        "true": True,
        "false": False
    }
    
    # Parsear tokens
    tokens = parsear_lineas(lineas)
    
    # Ejecutar
    ejecutar(tokens, variables)

def parsear_lineas(lineas):
    """Convierte las líneas en tokens estructurados"""
    tokens = []
    indice = 0
    
    while indice < len(lineas):
        linea = lineas[indice].strip()
        indice += 1
        
        if not linea or linea.startswith('//'):
            continue
        
        # Condicional if
        if linea.startswith('si '):
            condicion = re.match(r'si\s+(.+):', linea).group(1).strip()
            bloque_si = []
            bloque_sino = None
            
            # Buscar el contenido del bloque si
            nivel = 1
            while indice < len(lineas):
                linea_interna = lineas[indice].strip()
                indice += 1
                
                if linea_interna.startswith('si ') or linea_interna.startswith('mientras '):
                    nivel += 1
                elif linea_interna == 'fin':
                    nivel -= 1
                    if nivel == 0:
                        break
                elif linea_interna == 'sino:' and nivel == 1:
                    # Cambiar a buscar bloque sino
                    nivel_sino = 1
                    bloque_sino = []
                    
                    while indice < len(lineas):
                        linea_sino = lineas[indice].strip()
                        indice += 1
                        
                        if linea_sino.startswith('si ') or linea_sino.startswith('mientras '):
                            nivel_sino += 1
                        elif linea_sino == 'fin':
                            nivel_sino -= 1
                            if nivel_sino == 0:
                                break
                        else:
                            bloque_sino.append(linea_sino)
                    
                    break
                else:
                    bloque_si.append(linea_interna)
            
            # Agregar el condicional a los tokens
            tokens.append({
                'tipo': 'si',
                'condicion': condicion,
                'bloque_si': bloque_si,
                'bloque_sino': bloque_sino
            })
        
        # Ciclo mientras
        elif linea.startswith('mientras '):
            condicion = re.match(r'mientras\s+(.+):', linea).group(1).strip()
            bloque_mientras = []
            
            # Buscar el contenido del bloque mientras
            nivel = 1
            while indice < len(lineas):
                linea_interna = lineas[indice].strip()
                indice += 1
                
                if linea_interna.startswith('si ') or linea_interna.startswith('mientras '):
                    nivel += 1
                elif linea_interna == 'fin':
                    nivel -= 1
                    if nivel == 0:
                        break
                else:
                    bloque_mientras.append(linea_interna)
            
            # Agregar el ciclo mientras a los tokens
            tokens.append({
                'tipo': 'mientras',
                'condicion': condicion,
                'bloque': bloque_mientras
            })
        
        # Variable o conjura
        elif linea.startswith('alohomora ') or linea.startswith('conjura('):
            tokens.append({
                'tipo': 'linea',
                'contenido': linea
            })
    
    return tokens

def ejecutar(tokens, variables):
    """Ejecuta los tokens del programa"""
    for token in tokens:
        if token['tipo'] == 'si':
            # Evaluar la condición
            try:
                condicion_valor = eval(token['condicion'], {"__builtins__": {}}, variables)
                
                if condicion_valor:
                    # Ejecutar el bloque si
                    ejecutar_lineas(token['bloque_si'], variables)
                elif token['bloque_sino']:
                    # Ejecutar el bloque sino
                    ejecutar_lineas(token['bloque_sino'], variables)
            except Exception as e:
                print(f"Error en condicional: {e}")
        
        elif token['tipo'] == 'mientras':
            # Ejecutar el ciclo mientras
            try:
                # Protección contra ciclos infinitos
                max_iteraciones = 1000
                iteraciones = 0
                
                while eval(token['condicion'], {"__builtins__": {}}, variables):
                    iteraciones += 1
                    
                    if iteraciones > max_iteraciones:
                        print("¡Advertencia! Posible ciclo infinito detectado. Ejecución interrumpida.")
                        break
                    
                    ejecutar_lineas(token['bloque'], variables)
            except Exception as e:
                print(f"Error en ciclo mientras: {e}")
        
        elif token['tipo'] == 'linea':
            ejecutar_linea(token['contenido'], variables)

def ejecutar_lineas(lineas, variables):
    """Ejecuta una lista de líneas de código"""
    for linea in lineas:
        if linea and not linea.startswith('//'):
            ejecutar_linea(linea, variables)

def ejecutar_linea(linea, variables):
    """Ejecuta una línea de código"""
    linea = linea.strip()
    
    # Ignorar líneas vacías o comentarios
    if not linea or linea.startswith('//'):
        return
    
    # Variable
    if linea.startswith('alohomora '):
        match = re.match(r'alohomora\s+(\w+)\s*=\s*(.+)', linea)
        if match:
            nombre = match.group(1)
            valor = match.group(2).strip()
            
            try:
                # Arreglo
                if valor.startswith('[') and valor.endswith(']'):
                    variables[nombre] = eval(valor, {"__builtins__": {}}, variables)
                # Cadena
                elif (valor.startswith('"') and valor.endswith('"')) or \
                     (valor.startswith("'") and valor.endswith("'")):
                    variables[nombre] = valor[1:-1]
                # Booleano
                elif valor.lower() == 'true':
                    variables[nombre] = True
                elif valor.lower() == 'false':
                    variables[nombre] = False
                # Expresión
                else:
                    variables[nombre] = eval(valor, {"__builtins__": {}}, variables)
            except Exception as e:
                print(f"Error al asignar variable: {e}")
    
    # Conjura
    elif linea.startswith('conjura('):
        match = re.match(r'conjura\((.+)\)', linea)
        if match:
            contenido = match.group(1).strip()
            
            try:
                # Cadena
                if (contenido.startswith('"') and contenido.endswith('"')) or \
                   (contenido.startswith("'") and contenido.endswith("'")):
                    print(contenido[1:-1])
                # Variable
                elif contenido in variables:
                    valor = variables[contenido]
                    if isinstance(valor, bool):
                        print("true" if valor else "false")
                    else:
                        print(valor)
                # Expresión
                else:
                    resultado = eval(contenido, {"__builtins__": {}}, variables)
                    if isinstance(resultado, bool):
                        print("true" if resultado else "false")
                    else:
                        print(resultado)
            except Exception as e:
                print(f"Error al imprimir: {e}")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python compilador_simple.py archivo.eswino")
        sys.exit(1)
    
    ruta_archivo = sys.argv[1]
    
    if not ruta_archivo.endswith('.eswino'):
        print("Error: El archivo debe tener extensión .eswino")
        sys.exit(1)
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            codigo = archivo.read()
            compilar_eswino(codigo)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_archivo}")
    except Exception as e:
        print(f"Error al ejecutar el programa: {e}")

if __name__ == "__main__":
    main() 