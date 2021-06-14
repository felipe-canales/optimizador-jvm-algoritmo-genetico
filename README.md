# optimizador-jvm-algoritmo-genetico

Algoritmo genético escrito en Python 3, que optimiza los parámetros de la máquina virtual de Java (JVM) para un programa.

# Como correr

`python eval.py file pop iters`

- `file`: archivo a optimizar junto con parámetros extras.
- `pop`: tamaño de la población.
- `iters`: iteraciones.

Ej: `python eval.py "../dacapo-9.12-MR1-bach.jar fop -C" 60 10`

Se pueden ver opciones adicionales con `-h`.
