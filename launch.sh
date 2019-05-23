#!/bin/bash

python3 -m venv venv

. venv/bin/activate

pip3 install -r requirements.txt

export FLASK_APP=server.py
PORT=8000

read -p '¿Cuantos nodos quieres que tenga la red? ' NODES
flask run --host=0.0.0.0 --port $PORT & > /dev/null 2>&1

if test $NODES -gt 1
then
	for (( i=1; i<=$(($NODES-1)); i++ ))
	do
		NEW_PORT=$(($PORT+$i))
		flask run --host=0.0.0.0 --port $NEW_PORT & > /dev/null 2>&1
		sleep 1
		curl -X POST \
		http://$1:$NEW_PORT/add_with_existing_peer \
		-H 'Content-Type: application/json' \
		-d '{"node_ip": "http://'"$1"':'"$PORT"'"}' \
		& > /dev/null 2>&1
	done
fi

python3 main.py & > /dev/null 2>&1
