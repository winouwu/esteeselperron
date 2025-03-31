#!/usr/bin/env python3

import re
import sys

class EswinoInterpreter:
    def __init__(self):
        self.variables = {"true": True, "false": False}
        self.functions = {}
    
    def evaluate(self, expr):
        """Evalúa una expresión"""
        if isinstance(expr, str):
            # Si es una cadena con comillas, devuelve la cadena sin comillas
            if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
                return expr[1:-1]
            # Si es una variable, devuelve su valor
            elif expr in self.variables:
                return self.variables[expr]
            # Si es una expresión, evalúa usando eval
            try:
                return eval(expr, {"__builtins__": {}}, self.variables)
            except:
                return expr
        return expr
    
    def run_function(self, name, args):
        """Ejecuta una función definida por el usuario"""
        if name not in self.functions:
            print(f"Error: Función '{name}' no definida")
            return None
        
        # Guardar el contexto actual
        old_vars = self.variables.copy()
        
        # Configurar parámetros de la función
        func_def = self.functions[name]
        for i, param in enumerate(func_def["params"]):
            if i < len(args):
                self.variables[param] = args[i]
        
        # Ejecutar el cuerpo de la función
        result = None
        for line in func_def["body"]:
            # Si es una instrucción de retorno, devuelve el valor
            if line.startswith("regresa "):
                expr = line[8:].strip()
                result = self.evaluate(expr)
                break
            # Si no, procesa la línea normalmente
            self.process_line(line)
        
        # Restaurar contexto anterior
        self.variables = old_vars
        
        return result
    
    def process_line(self, line):
        """Procesa una línea de código eswino"""
        line = line.strip()
        
        # Ignorar líneas vacías y comentarios
        if not line or line.startswith("//"):
            return
        
        # Asignación de variable
        if line.startswith("alohomora "):
            match = re.match(r"alohomora\s+(\w+)\s*=\s*(.*)", line)
            if match:
                var_name = match.group(1)
                expr = match.group(2)
                self.variables[var_name] = self.evaluate(expr)
        
        # Impresión
        elif line.startswith("conjura("):
            match = re.match(r"conjura\((.*)\)", line)
            if match:
                expr = match.group(1)
                print(self.evaluate(expr))
        
        # Llamada a función
        elif re.match(r"^(\w+)\s*\(", line):
            match = re.match(r"^(\w+)\s*\((.*?)\)", line)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                args = []
                
                # Evaluar argumentos
                if args_str.strip():
                    for arg in args_str.split(","):
                        args.append(self.evaluate(arg.strip()))
                
                # Llamar a función
                self.run_function(func_name, args)
    
    def parse_function(self, lines, start_line):
        """Analiza una definición de función"""
        line = lines[start_line]
        match = re.match(r"hechizo\s+(\w+)\s*\((.*?)\):", line)
        if not match:
            return start_line + 1
        
        func_name = match.group(1)
        params_str = match.group(2)
        params = [p.strip() for p in params_str.split(",") if p.strip()]
        
        # Extraer el cuerpo de la función
        body = []
        i = start_line + 1
        while i < len(lines) and lines[i].strip() != "fin":
            body.append(lines[i])
            i += 1
        
        # Registrar la función
        self.functions[func_name] = {
            "params": params,
            "body": body
        }
        
        return i + 1  # Continuar después del 'fin'
    
    def run(self, code):
        """Ejecuta el código eswino"""
        # Eliminar comentarios y dividir en líneas
        code = re.sub(r"//.*", "", code)
        lines = [line for line in code.splitlines()]
        
        # Primer paso: Analizar todas las funciones
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("hechizo "):
                i = self.parse_function(lines, i)
            else:
                i += 1
        
        # Segundo paso: Ejecutar el programa principal
        for line in lines:
            line = line.strip()
            if not line.startswith("hechizo ") and line and line != "fin":
                self.process_line(line)

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python eswino.py <archivo.eswino>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], "r") as file:
            code = file.read()
        
        interpreter = EswinoInterpreter()
        interpreter.run(code)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{sys.argv[1]}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 