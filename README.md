# Práctica para sistemas distrbuidos

Aplicación blockchain para la práctica opcional de la asignatura Sistemas Distribuidos de la Universidad de Salamanca.  
  
La práctica consiste en un sistema médico distribuido basado en blockchain e implementado en
python. Su función es la de guardar un registro médico para los pacientes, en el que cada trasnacción 
de la cadena representa una entrada en su historial. Esta cadena además se encuentra repartida de forma 
distribuida entre todos los nodos de la red, que llevan a cabo una función de consenso para que todos
dispongan de la misma información.

## Pasos previos
#### Requisitos:
Es necesario instalar lo siguiente en el ordenador para poder ejecutar la aplicación correctamente:
> $ sudo apt-get update  
> $ sudo apt-get install git  
> $ sudo apt-get install python3-venv  
> $ sudo apt-get install python3-pip

## Cómo ejecutar la aplicación:
Una vez instalado todo lo necesario para que funcione la aplicación, sólo será necesario ejecutar los siguientes comandos:
> $ git clone https://github.com/calabres97/MediChain.git  
> $ cd MediChain  
> $ chmod +x launch.sh  
> $ ./launch.sh $IP_ORDENADOR

### Adicional:
Si se desea arrancar un nodo más para que se una a la red blockchain cuando esta ya está iniciada, necesitará ejecutar 
la siguiente órden:
> $ flask run --host=0.0.0.0 --port=$PUERTO_DESEADO &  

Una vez arrancado el nodo deberás registrarlo dentro de la aplicación en el apartado de registrar nuevos nodos.

## Enlaces de acceso a la aplicación:

Frontend de la aplicación: http://dirIp:5000/ENDPOINT  
Backend de la aplicación: http://dirIp:8000/ENDPOINT (el puerto puede variar en función de su configuración)

## Integrantes del equipo:
Enrique Hernández Calabrés  
Daniel Alcón Martín

