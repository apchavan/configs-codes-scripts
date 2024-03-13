#!/bin/bash

# Kill existing process of Dash.
script_name=/FULL/PATH/TO/PYTHON_SCRIPT.PY
ps -ef | grep $script_name | grep -v grep | awk '{print $2}' | xargs kill -9
