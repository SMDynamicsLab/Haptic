# Primer intento de un trial de reaching (test4)
* un plano (con efecto magnetico fuerte)
* registrar la posicion (2D)
* el sujeto vuelve solo al punto de partida (donde empieza el trial) que podria ser magnetico 
* al colisionar que se acive mec de vuelta al origen (como en 06-images) y se apague cuando llegue al origen
* el sujeto indica cuando esta listo para el trial (haciendo click o tocando una tecla)


# Por hacer 

## el controlador en python
* script en python que grafique los trials 

## la comunicacion
* python tiene que informar nueva config de trial, c tiene que informar fin de los trials
* archivo/buffer informa numero de trial (c lee y borra?)
* guardar en variable y escribir a disco al final del trial 
* buscar doc sobre shared buffers python c++ (si no hacer con archivo)
* ver aprox cuanto esta consumiendo de cpu 

## resolver trials individuales
### Orden 0
* orden de los bloques (perturbado/no perturbado) esta predeterminado desde el inicio del script de c
* argumentos para c son el input y el output 
* queremos que python guarde el dat con los datos del sujeto (etc) 
* perturbacion es fza elastica (como en 01-mydevice) con el 0 en el start pero con direccion hacia el costado
* pantallita con instrucciones para el sujeto

### Orden 1 
* puede haber trials incorrectos entonces querriamos agregar trials al final si alguno falla  
* queremos ir cambiando las condiciones entre trials (despues de analizar el output)

# Para mas adelante 
* caracterizar el sistema, la frecuencia

# Hechos
* decision por CHAI3D por sobre el SDK de forcedimension porque los autores son los mismos y es open source y vienen muchas cosas graficas resueltas (y el SDK no compila)

