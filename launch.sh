#!/bin/bash

cd MediChain

python3 -m venv venv

. venv/bin/activate

export FLASK_APP=server.py
PORT=8000

read -p '¿Cuantos nodos quieres que tenga la red? ' NODES
flask run --port $PORT & > /dev/null 2>&1

if test $NODES -gt 1
then
	for (( i=1; i<$NODES; i++ ))
	do
		NEW_PORT=$(($PORT+$i))
		flask run --port $NEW_PORT & > /dev/null 2>&1
		curl -X POST \
		http://127.0.0.1:$PORT/add_with_existing_peer \
		-H 'Content-Type: application/json' \
		-d '{"node_ip": "http://127.0.0.1:'"$NEW_PORT"'"}' \
		& > /dev/null 2>&1
	done
fi

python3 main.py & > /dev/null 2>&1