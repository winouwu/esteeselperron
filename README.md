# Compilador Eswino

Un compilador para archivos con extensión `.eswino` que ejecuta la función `conjura` para imprimir texto en la consola, permite la declaración de variables con `alohomora` y soporta comentarios.

## Requisitos

- Python 3.x

## Uso

1. Crea un archivo con extensión `.eswino` con tu código
2. Ejecuta el compilador:

```
python compilador/compiler.py ejemplos/miarchivo.eswino
```

## Sintaxis

El compilador actualmente soporta:

### Impresión de texto
Usa la función `conjura` para imprimir texto o variables:

```
conjura("texto a imprimir")
conjura(variable)
```

### Declaración de variables
Usa `alohomora` para declarar variables:

```
alohomora nombre = valor
```

Ejemplos:
```
alohomora x = 5
alohomora mensaje = "Hola mundo"
alohomora suma = 10 + 20
```

### Arreglos
Puedes crear y utilizar arreglos:

```
alohomora numeros = [1, 2, 3, 4, 5]
alohomora nombres = ["Juan", "Pedro", "María"]
```

### Comentarios
Hay dos tipos de comentarios:

#### Comentarios de una línea
Usa el símbolo `$` para comentarios de una línea:

```
$ Este es un comentario de una línea
alohomora x = 10 $ Este también es un comentario
```

#### Comentarios multilínea
Usa `¡` para iniciar y `!` para terminar un comentario multilínea:

```
¡
Este es un comentario
que ocupa varias líneas
y será ignorado por el compilador
!
```

## Ejemplos

El repositorio incluye varios ejemplos:

- `ejemplos/ejemplo.eswino`: Ejemplo básico de impresión
- `ejemplos/variables.eswino`: Ejemplo de uso de variables
- `ejemplos/arreglos.eswino`: Ejemplo de uso de arreglos
- `ejemplos/operaciones.eswino`: Ejemplo de operaciones aritméticas
- `ejemplos/comentarios.eswino`: Ejemplo de uso de comentarios 