#!/bin/bash

echo Creando migrations
python kinesio/manage.py makemigrations users kinesioapp

echo Comienzo de migracion
python kinesio/manage.py migrate