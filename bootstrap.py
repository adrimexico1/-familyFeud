import os
import sys
import subprocess
import venv
import shutil

def get_venv_python():
    """Retorna la ruta del ejecutable de python dentro del entorno virtual."""
    if sys.platform == "win32":
        return os.path.join(".venv", "Scripts", "python.exe")
    else:
        return os.path.join(".venv", "bin", "python")

def setup_virtual_environment():
    """Crea el entorno virtual e instala las dependencias necesarias."""
    venv_dir = ".venv"
    venv_python = get_venv_python()
    
    # 1. Crear el entorno virtual si no existe
    if not os.path.exists(venv_dir):
        print("Creando entorno virtual (.venv)...")
        venv.create(venv_dir, with_pip=True)
        print("Entorno virtual creado con éxito.")
    
    # 2. Verificar o instalar dependencias
    # Usamos PySide6 para la interfaz gráfica premium
    try:
        # Intentamos importar PySide6 usando el python del entorno virtual
        print("Verificando dependencias en el entorno virtual...")
        subprocess.run(
            [venv_python, "-c", "import PySide6"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("PySide6 ya está instalado.")
    except subprocess.CalledProcessError:
        print("Instalando dependencias (PySide6)... Esto puede tardar unos momentos.")
        try:
            subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            subprocess.run([venv_python, "-m", "pip", "install", "PySide6"], check=True)
            print("Dependencias instaladas con éxito.")
        except Exception as e:
            print(f"Error al instalar dependencias: {e}")
            sys.exit(1)

def run_app():
    """Ejecuta la aplicación principal."""
    venv_python = get_venv_python()
    main_script = os.path.join("src", "main.py")
    
    if not os.path.exists(main_script):
        print(f"Error: No se encontró el script principal en '{main_script}'.")
        sys.exit(1)
        
    print("Iniciando la aplicación...")
    # Ejecutamos la aplicación con el python del venv
    try:
        subprocess.run([venv_python, main_script])
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario.")

if __name__ == "__main__":
    # Asegurar que el directorio de trabajo es el del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    setup_virtual_environment()
    run_app()
