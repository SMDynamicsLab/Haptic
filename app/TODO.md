# Analisis previo
* decision por CHAI3D por sobre el SDK de forcedimension porque los autores son los mismos y es open source y vienen muchas cosas graficas resueltas (y el SDK no compila)

* en el while de python: 
no sleep 99% CPU
time.sleep(0.001) #~9% CPU
time.sleep(0.01) # ~2% CPU

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
### guardar datos
* archivo de 3 cols x y z desp de cada trial
* en el archivo que tenga info del sujeto (python pasa esa info)
### el controlador en python
* script en python que grafique los trials 
### la comunicacion
* python tiene que informar nueva config de trial, c tiene que informar fin de los trials
* archivo/buffer informa numero de trial (c lee y borra?)
* guardar en variable y escribir a disco al final del trial 
* buscar doc sobre shared buffers python c++ (si no hacer con archivo)

# Por hacer 
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

# Del paper
* The cursor was a square of size 2 x 2 mm’ on a computer monitor and indicated the position of the handle of the manipulandum. Targets were specified by a square of size 8 x 8 mm’.
*  After the subject had moved to the target, the next target, again chosen at a random direction and at 10 cm, was presented. All targets were kept with in the confines of the 15 x 15 cm workspace.
* A target set consisted of 250 such sequential reaching movements.
* For 48 randomly chosen members of the target set, hereafter referred to as
the no-vision target set, the cursor position during the movement was
blanked, removing visual feedback during the reaching period.
* Dots are 10 msec apart. (en los graficos)
* graficos: avg +- std de la trayectoria

# test6:
* punto inicial / punto final
* el target puede ser random dentro de 8 angulos 
* que el cursor se pueda activar/desactivar visualmente
* que entre a una zona en lugar de chocar con una pared
* sigue siendo que vuelve a su posicion original
* bloque sin fuerza (16 trials de direcciones al azar) training adaptacion al aparato (con feedback visual)
* bloque sin fuerza sin feedback
* bloque con fuerza sin feedback
* bloque sin fuerza (para ver after effects) sin feedback

# info 
* hapticDevice->getPosition / tool->getDeviceGlobalPos() = (0.075, 0.075, 0.075)
* hapticDevice->getLinearVelocity / tool->getDeviceGlobalLinVel()  = (0.075, 0.075, 0.075)
* object->getGlobalPos() es comparable a tool->getDeviceGlobalPos()
* [hapticDevice->getPosition] = [m]
* [hapticDevice->getLinearVelocity(linearVelocity] = [m/s]
* [force] = [N]
* [B] = [N.sec/m]
* tool->getDeviceGlobalForce() = tool->getDeviceLocalForce() = hapticDevice->getForce


# Para la prox
* con el campo y trayectorias del paper comparar las trayectorias (subplot por posicion)
* descartar trial si tarda mas de 2 segundos  (en el paper es limite 0.65) 
* terminar el trial si se queda quieto (cerca del target por 500ms )

* arreglar el plot (subplot por pos)
* armar array [0,1,2,3,4,5]*N/6 y permutarlo al azar
* input/output files con timestamp
* arreglar que siempre sale el mismo angulo!

# Nuevo test:
* visuomotor rotation (ver paper del mail)
* 3 bloques (sin, con, sin)
* girar el vector "up" en la orientacion del cursor a un angulo definido (siempre el mismo)

# vmr 
* mantener en el centro 500ms (en tamaño ejemplo de https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0026020 section 4)
* luego arranca tiempo random (uniforme) entre 200 y 800ms que suena un beep de go y el centro desaparece
* timeout (tiempo limite 2s) para llegar al target
* mantener cerca del target por 500ms , luego sonido de exito (o fracaso) y desaparece el target
* tiempo random entre 500 y 1.5s vuelve a aparecer el centro
* el sujeto lleva al centro y lo mantiene y vuelve a empezar 


* si el trial termino que se cierre
* plotear correctamente cada intento
* activar/ desactivar vmr a traves de las variables
* agregar timestamp en el csv de data
## falta:
* beep de go al terminar de sostener el centro
* el sujeto lleva al centro sin perturbacion?

* armar el grafico del error abs y signado entre la tray seguida y la real
* guardar trials invalidos etiquetados, que python interprete y agregue un trial mas
* si el hold falla que no haga timeout y guardar la posicion hasta que termine el trial (por valido o invalido)

* mandar mail preguntando fecha de informe de avance

* incorporar al plot promedio de los trials de un mismo sujeto (ejemplo 8 trials consecutivos)
* metodos de analisis de berniker fig 5 Estimating the sources of motor errors for adaptation and generalization

* referencia 4 para el error
* referencia 6 de berniker para curl (shadmehr)
* cambiar los bloques de lista a dict, ejemplo:
dict:
{
0:{ 
[]
[]
[]
}
1:{
[]
[]
[]
}
}
for block in dict:
  initial_block_len = len(block)
  while (i < len(block) AND (i < initial_block_len *1.1)  : 
    trial = block[i]
    si el trial es incorrecto : agrega el mismo trial al final
    i +=1