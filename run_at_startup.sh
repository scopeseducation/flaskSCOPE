#!/bin/bash

cd /home/pi/flask_scope_v2.3
export FLASK_APP=flask_scope.py
flask run -p 80 -h '0.0.0.0' 2> flask.err >flask.out
