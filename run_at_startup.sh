#!/bin/bash

cd dir2change
export FLASK_APP=flask_scope.py
flask run -p 80 -h '0.0.0.0' 2> flask.err >flask.out
