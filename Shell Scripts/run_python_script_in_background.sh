#!/bin/bash

# Start new Python process in background using Python from `conda` environment.
nohup /PATH/TO/miniconda3/condabin/conda run -n ENV_NAME python3 /PATH/TO/PYTHON_SCRIPT.PY &
