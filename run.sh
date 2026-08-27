#!/bin/bash
# Ir al directorio del script
cd "$(dirname "$0")"

# Ejecutar el bootstrap con python o python3
if command -v python3 &>/dev/null; then
    python3 bootstrap.py
elif command -v python &>/dev/null; then
    python bootstrap.py
else
    echo "Error: Python no está instalado en este sistema. Por favor instala Python 3 para ejecutar el programa."
    read -p "Presiona Enter para salir..."
fi
