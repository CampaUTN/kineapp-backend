#!/bin/bash
python kinesio/manage.py makemigrations kinesioapp
python kinesio/manage.py migrate