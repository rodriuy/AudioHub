#!/bin/bash
# Ruta absoluta a tu proyecto
DIR="/home/$(whoami)/Proyectos/AudioHub"
cd $DIR
# Ejecuta usando el python del entorno virtual directamente
# Ejecuta el entrypoint reorganizado
$DIR/venv/bin/python3 $DIR/app.py
