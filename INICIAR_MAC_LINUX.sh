#!/bin/sh
set -e
cd "$(dirname "$0")"
echo 'PROYECTO 20 — ENTRENADOR ULIMA'
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
