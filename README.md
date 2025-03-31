# Compilador Eswino

Un simple compilador para archivos con extensión `.eswino` que ejecuta la función `conjura` para imprimir texto en la consola.

## Requisitos

- Python 3.x

## Uso

1. Crea un archivo con extensión `.eswino` con tu código
2. Ejecuta el compilador:

```
python compiler.py miarchivo.eswino
```

## Sintaxis

El compilador actualmente soporta la función `conjura` para imprimir texto:

```
conjura("texto a imprimir")
```

## Ejemplo

El archivo de ejemplo `ejemplo.eswino` contiene:

```
conjura("Hola Mundo desde eswino!")
conjura("Esta es otra línea")
conjura("El compilador funciona!")
```

Al ejecutar `python compiler.py ejemplo.eswino`, el resultado será:

```
Hola Mundo desde eswino!
Esta es otra línea
El compilador funciona!
``` 