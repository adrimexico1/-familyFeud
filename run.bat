@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>nul

:: ============================================
::   Cien Trakas Dijeron - Lanzador Portable
::   Solo da doble clic para jugar.
:: ============================================

:: Configuracion
set PYTHON_VERSION=3.11.9
set PYTHON_DIR=%~dp0python
set PYTHON_EXE=%PYTHON_DIR%\python.exe
set PYTHON_ZIP=python-%PYTHON_VERSION%-embed-amd64.zip
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_ZIP%
set GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py

:: Ir al directorio del script
cd /d "%~dp0"

echo.
echo  ========================================
echo       100 MEXICANOS DIJERON
echo       Iniciando...
echo  ========================================
echo.

:: -----------------------------------------------
:: PASO 1: Verificar si ya tenemos Python local
:: -----------------------------------------------
if exist "%PYTHON_EXE%" goto :check_deps

echo  [1/4] Descargando Python %PYTHON_VERSION% (portable)...
echo         Esto solo se hace la PRIMERA vez.
echo         No se instala nada en tu sistema.
echo.

:: Intentar descargar con curl (disponible en Windows 10/11)
where curl >nul 2>nul
if %errorlevel% equ 0 (
    echo         Usando curl para descargar...
    curl -L -o "%PYTHON_ZIP%" "%PYTHON_URL%"
    if !errorlevel! equ 0 goto :download_ok
    echo         curl fallo, intentando con PowerShell...
)

:: Intentar con PowerShell (metodo 1: Invoke-WebRequest con -UseBasicParsing)
echo         Usando PowerShell para descargar...
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%' -UseBasicParsing"
if %errorlevel% equ 0 (
    if exist "%PYTHON_ZIP%" goto :download_ok
)

:: Intentar con PowerShell (metodo 2: WebClient - mas compatible)
echo         Intentando metodo alternativo...
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%')"
if %errorlevel% equ 0 (
    if exist "%PYTHON_ZIP%" goto :download_ok
)

:: Intentar con certutil (disponible en TODAS las versiones de Windows)
echo         Intentando con certutil...
certutil -urlcache -split -f "%PYTHON_URL%" "%PYTHON_ZIP%"
if %errorlevel% equ 0 (
    if exist "%PYTHON_ZIP%" goto :download_ok
)

:: Si nada funciono
echo.
echo  ERROR: No se pudo descargar Python.
echo.
echo  Posibles soluciones:
echo    1. Verifica tu conexion a internet
echo    2. Descarga Python manualmente desde:
echo       %PYTHON_URL%
echo    3. Coloca el archivo "%PYTHON_ZIP%" en esta carpeta
echo       y ejecuta este archivo de nuevo.
echo.
pause
exit /b 1

:download_ok
echo         Descarga completada.
echo.

:: -----------------------------------------------
:: PASO 2: Descomprimir Python
:: -----------------------------------------------
echo  [2/4] Descomprimiendo Python...

if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
if %errorlevel% neq 0 (
    echo  ERROR: No se pudo descomprimir Python.
    echo.
    pause
    exit /b 1
)
del "%PYTHON_ZIP%" 2>nul

:: -----------------------------------------------
:: PASO 3: Configurar Python portable + pip
:: -----------------------------------------------
echo  [3/4] Configurando Python portable...

:: Habilitar site-packages (el embed lo trae desactivado por defecto)
for %%f in ("%PYTHON_DIR%\python*._pth") do (
    powershell -ExecutionPolicy Bypass -Command "(Get-Content '%%f') -replace '#import site','import site' | Set-Content '%%f'"
)

:: Descargar get-pip.py
echo         Instalando pip...
where curl >nul 2>nul
if %errorlevel% equ 0 (
    curl -L -o "%~dp0get-pip.py" "%GET_PIP_URL%"
) else (
    powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GET_PIP_URL%', '%~dp0get-pip.py')"
)

"%PYTHON_EXE%" "%~dp0get-pip.py" --no-warn-script-location >nul 2>nul
if %errorlevel% neq 0 (
    echo  ERROR: No se pudo instalar pip.
    echo.
    pause
    exit /b 1
)
del "%~dp0get-pip.py" 2>nul

echo         Python portable listo.
echo.

:: -----------------------------------------------
:: PASO 4: Verificar / instalar dependencias
:: -----------------------------------------------
:check_deps
"%PYTHON_EXE%" -c "import PySide6" 2>nul
if %errorlevel% neq 0 (
    echo  [4/4] Instalando dependencias (PySide6)...
    echo         Esto puede tardar unos minutos la primera vez...
    echo.
    "%PYTHON_EXE%" -m pip install PySide6 --no-warn-script-location
    if !errorlevel! neq 0 (
        echo.
        echo  ERROR: No se pudieron instalar las dependencias.
        echo  Verifica tu conexion a internet e intenta de nuevo.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo         Dependencias instaladas correctamente.
    echo.
)

:: -----------------------------------------------
:: PASO 5: Ejecutar la aplicacion
:: -----------------------------------------------
echo  Iniciando el juego...
echo.

"%PYTHON_EXE%" src\main.py 2>&1

echo.
if %errorlevel% neq 0 (
    echo  ====================================================
    echo  Ocurrio un error al ejecutar la aplicacion.
    echo  Si el problema persiste, borra la carpeta "python"
    echo  y ejecuta este archivo de nuevo.
    echo  ====================================================
) else (
    echo  El juego se cerro correctamente.
)
echo.
echo  Presiona cualquier tecla para cerrar esta ventana...
pause >nul

endlocal
