#! /bin/sh
source .venv/bin/activate
python3 src/main.py --threads 2 "$@"