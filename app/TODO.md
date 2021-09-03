# Analisis previo
* decision por CHAI3D por sobre el SDK de forcedimension porque los autores son los mismos y es open source y vienen muchas cosas graficas resueltas (y el SDK no compila)

# Tests
## Primer intento de un trial de reaching (test4)
* un plano (con efecto magnetico fuerte)
* registrar la posicion (2D)
* el sujeto vuelve solo al punto de partida (donde empieza el trial) que podria ser magnetico 
* al colisionar que se acive mec de vuelta al origen (como en 06-images) y se apague cuando llegue al origen
* el sujeto indica cuando esta listo para el trial (haciendo click o tocando una tecla)

## Trial de reaching perturbado (test5)
### Simulacion
* perturbacion es fza elastica (como en 01-mydevice) con el 0 en el start pero con direccion hacia el costado (en Y)
* pantallita que muestra la fuerza (despues se puede cambiar a que muestre instrucciones)
### Comunicacion python-C
* descarte las shared libraries porque agregaban complejidad innecesaria al manejo de la simulacion (y al compilado)
* argumentos para c son el input y el output (no los usa)
* la ejecucion se inicia desde python
* inclui un parser de space-separated doubles que actualiza un vector de doubles
* el parser se llama en C cuando el archivo es modificado (usando stat st_mtime)
* el parser se puede incluir en el loop haptico sin problemas
* el script de python abre un proceso para correr el ejecutable de c y despues se queda mirando si un file se modifica
* ver aprox cuanto esta consumiendo de cpu 


# Por hacer 
## guardar datos
* archivo de 3 cols x y z desp de cada trial
* en el archivo que tenga info del sujeto (python pasa esa info)

## el controlador en python
* script en python que grafique los trials 

## la comunicacion
* python tiene que informar nueva config de trial, c tiene que informar fin de los trials
* archivo/buffer informa numero de trial (c lee y borra?)
* guardar en variable y escribir a disco al final del trial 
* buscar doc sobre shared buffers python c++ (si no hacer con archivo)

## resolver trials individuales
### Orden 0
* orden de los bloques (perturbado/no perturbado) esta predeterminado desde el inicio del script de c
* queremos que python guarde el dat con los datos del sujeto (etc) 

### Orden 1 
* puede haber trials incorrectos entonces querriamos agregar trials al final si alguno falla  
* queremos ir cambiando las condiciones entre trials (despues de analizar el output)

### fuerzas 
* campos vectoriales (dep de la pos)
* campos dep de la velocidad (coriolis y dep del angulo)

# Papers 
* Collins, J. J., & De Luca, C. J. (1995). The effects of visual input on open-loop and closed-loop postural control mechanisms. Experimental brain research, 103(1), 151-163.
    * herramienta para caracterizar todos los trials como equivalentes (open/closed loop)
* https://www.jneurosci.org/content/14/5/3208.short
    * entender estructura basica (qué ve el sujeto, en que orden, perturbado, mezcla, etc)
    * sacar la parte de los campos en coords relativas (angulares)
    * fase de adaptacion y aftereffects 
    * sacar la parte de generalizacion (dejar para mas adelante)
    * como hacen los promedios espaciales (temporal y componen o interpolan)

# Para mas adelante 
* caracterizar el sistema, la frecuencia
* timer o similar para no tener al script de python con un sleep
* mejorar el parser (str/value pairs)
