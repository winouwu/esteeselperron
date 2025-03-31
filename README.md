# Compilador Eswino

Un simple compilador para archivos con extensión `.eswino` que ejecuta la función `conjura` para imprimir texto en la consola y permite la declaración de variables con `alohomora`.

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

## Ejemplos

### Ejemplo básico
El archivo de ejemplo `ejemplos/ejemplo.eswino` contiene:

```
conjura("Hola Mundo desde eswino!")
conjura("Esta es otra línea")
conjura("El compilador funciona!")
```

### Ejemplo con variables
El archivo `ejemplos/variables.eswino` muestra cómo trabajar con variables:

```
alohomora numero = 5
conjura(numero)
// Imprime: 5

alohomora texto = "Hola desde variable"
conjura(texto)
// Imprime: Hola desde variable
``` 