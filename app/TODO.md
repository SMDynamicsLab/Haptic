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
* cambiar los bloques de lista a dic
* armar el grafico del error abs y signado entre la tray seguida y la real
* guardar trials invalidos etiquetados, que python interprete y agregue un trial mas
* si el hold falla que no haga timeout y guardar la posicion hasta que termine el trial (por valido o invalido)

## falta:
* beep de go al terminar de sostener el centro
* el sujeto lleva al centro sin perturbacion
* mandar mail preguntando fecha de informe de avance
* incorporar al plot promedio de los trials de un mismo sujeto (ejemplo 8 trials consecutivos)
* metodos de analisis de berniker fig 5 Estimating the sources of motor errors for adaptation and generalization
* referencia 4 para el error
* referencia 6 de berniker para curl (shadmehr)


# Grafico para un sujeto
* trayectorias (empezando en gris claro y yendo a negro)

# Grafico entre sujetos
* trayectorias: cada sujeto (con un color asociado) es una curva mostrando las primeras o ultimas 2 del bloque de cada angulo (2 graficos, uno para inicial y otro para final)
* error absoluto y error signado (cada sujeto es una trayectoria)
* distancia recorrida (serie de trials) (cada sujeto es una trayectoria)
* tiempo total  (serie de trials) (cada sujeto es una trayectoria)
* velocidad media (serie de trials) (cada sujeto es una trayectoria)
* restar tiempo de hold para la velocidad


ver codigo para calcular area: 
https://stackoverflow.com/questions/451426/how-do-i-calculate-the-area-of-a-2d-polygon
https://www.geeksforgeeks.org/area-of-a-polygon-with-given-n-ordered-vertices/
https://stackoverflow.com/questions/34326728/how-do-i-calculate-the-area-of-a-non-convex-polygon
buscar para nonsimple polygon

* cambiar colores de tool y target para que no coincidan con tool
* armar la demo (2 veces a cada angulo con y sin vmr)
    * ir a cada angulo sin y con vmr (hasta que lo haga correcto)
    * para reutilizar la estructura: pasar la lista sobre la que hace shuffle (poruqe queremos que por cada ang haga con y sin vrm), agregar que el limite 1.1 sea una var
    * mensaje de feedback (mas grande)
* agregar descansos
* curl force: paper de crisimagna y shadmehr, revisar instrucciones y restricciones de esos trials
    * tablas con desarrollo experimental aca https://journals.physiology.org/doi/full/10.1152/jn.00622.2002

# Correcciones despues del trial en lo de rodri:
## Hechos 
* parte de los ajustes que sea ajustar el sonido con los sonidos del experimento
* Settings de la compu para que no se apague 
* Brillo pantalla
* Girado de pantalla (vmr 180) (+ girado de instrucciones)
* En la demo 1 sin, 2 con vmr
* final mas suave, llevar al centro y que termine o algo asi
* graficos se guardan en lugar de abrirse
* Después del descanso aparece en el centro y falla (probar)

## Por hacer
* Escala del movimiento (escala real)
    * mi pantalla: 31cm * 18.5
    * en fullscreen width: 1366, height: 768
    * esfera roja: 95px  (=> 2.14 cm)
    * esfera gris: 64px  (=> 1.44 cm)
    * separacion entre esferas: 153px (=> 3.46)
    * de ppo esfera a final de la otra: 312 px (=> 7.05)
    * distancia entre el centro de la esferas 232.5 px (=> 5.259)
    * eDP-1 connected primary 1366x768+288+1080 (normal left inverted right x axis y axis) 309mm x 173mm (xrandr | grep ' connected')
* Alerta de application not responding al iniciar

## Por hacer (no tan urgentes)
* Timeout variable/adaptativo ?
* inercia
* pd maximun perpendicular errors
* zipear los archivos

----------------------
# Vmr temporal 
## HECHO:
* el primer sonido cuando sale para comparar mejor con la tarea de reaching
* probar con bloques de N = 12 * 6 
* agregar multiples sonidos, previamente generados por python y que lleguen como parametro. periodos: 444 666 (python indica cual usar y C++ carga todos al cargar el archivo)
* feedback sobre performance en otro label/grafico en pantalla que dure mas tiempo (usando ejemplo de 03-analytics) grafico con barrita para arriba/abajo de cada trial individual (tope superior dice demasiado lento y es el timeout, el tope inferior es la mitad del target) mirar los ejemplos de chai3d y sin numeros 
* hacer que desaparezca el feedback cuando empieza el "mantener" de la nueva trayectoria Y luego que aparezca al llegar al target

# Fuerza + temporal
* dependiente de la velocidad (como el de la bibliografia)
* agregar varias fuerzas:
    - proporcional a la velocidad pero perpendicular ~ fza magnetica (test6.cpp)
    - igual a el anteiror pero para el otro lado 
    - proporcional a la velocidad (y paralelo) ~ fza viscosa
    - igual anterior pero sentido opuesto
    - dependiente de la posicion (elastica con x-x0=x-centro)
* *Campo de fuerza + perturbacion temporal (usar test6.cpp)

# Detalles reproduccion temporal 
## Generales
* limite para que arranque (2s ) y despues un limite desde el primer sonido (2s)
* girar indicador de tiempos (rapido mas corto y lento mas largo)

## Exp Fuerza unicamente
* que la fuerza se apague fuera del trial
* si llega al borde que apague el campo y marque trial invalido y terminado
* alargar la distancia (mover el centro hacia abajo) 
* que la fuerza (el tipo) se pueda manejar desde python

------------------------
## POR HACER:
* redondear num samples para que abarque un num entero de periodos de la freq en append sinewave
* graficos para el asunto temporal : error con el periodo y el vmr
* buffer de la placa de sonido cuando el C reproduce el sonido / chequear chunks 


al final del trial que vaya al centro 
trial invalido si la fuerza sobrepasa el valor max del aparato (12) esto es en el analisis post
exp piloto de normal - f1 - normal -f2 ... - f6 - normal (todo con el mismo periodo ) -> probar cuanto tardaria
tener en cuenta q pasa si pasas el piso 
ver si cambiamos los valores estos a 1 *
    base->m_material->setMagnetMaxForce(0.8 * maxLinearForce);   
    base->m_material->setStiffness(0.5 * maxStiffness);
# lista de pasos a seguir en ambos exp
que el sujeto no lo suelte

-----------------
Probar sin feedback y con descanso entre bloques
    - 15 trials 
    - fuerzas 1, 2, 3 y 6 
    - 60 s espera entre bloques
-----------------
chequear error de area signado => esta OK

Probar sin feedback vmr y fuerza
    - 20 trials
    - 1 solo angulo
    - usar tiempos 333, 444 y 666 
    - bajar tiempo espera entre bloques (30s)
    - 6 bloques:
    distinto para los sujetos
    [
        periodo1 + sin vmr , periodo1 + vmr, periodo1 + sin vmr, 
        periodo2 + sin vmr , periodo2 + vmr, periodo2 + sin vmr, 
        periodo3 + sin vmr , periodo3 + vmr, periodo3 + sin vmr
    ]
    
mas adelante, contrabalnceado:
    [periodo2 + sin vmr , periodo2 + vmr, periodo2 + sin vmr, periodo1 + sin vmr , periodo1 + vmr, periodo1 + sin vmr]


