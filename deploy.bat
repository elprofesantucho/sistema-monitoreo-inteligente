@echo off
chcp 65001 >nul
echo.
echo ===============================================
echo  SISTEMA MONITOREO INTELIGENTE - EEST N14
echo ===============================================
echo.
echo Proyecto: Sistema de riego automatico con ESP32
echo Sensores: DHT22, 4x suelo, pantalla TFT, puente H
echo Dashboard: Streamlit para monitoreo en tiempo real
echo.
echo ?Que accion deseas realizar?
echo 1 - INICIALIZAR GIT y subir por primera vez
echo 2 - SOLO ACTUALIZAR cambios existentes
echo 3 - EJECUTAR DASHBOARD Streamlit
echo.
set /p opcion="Elige opcion [1-3]: "

if "%opcion%"=="1" goto PRIMERA_VEZ
if "%opcion%"=="2" goto ACTUALIZAR
if "%opcion%"=="3" goto DASHBOARD

:PRIMERA_VEZ
echo.
echo  Inicializando repositorio Git...
git init
echo.
echo  Creando archivo .gitignore...
(
echo # Python
echo __pycache__/
echo *.pyc
echo venv/
echo env/
echo.
echo # PlatformIO
echo .pio/
echo .pioenvs/
echo .piolibdeps/
echo.
echo # Datos y archivos temporales
echo *.csv
echo *.json
echo dashboard_streamlit/data/
echo *.log
echo.
echo # Sistema
echo .DS_Store
echo Thumbs.db
) > .gitignore
echo.
echo  Agregando archivos al repositorio...
git add .
echo.
echo  Creando commit inicial...
git commit -m "Sistema Monitoreo Inteligente EEST N14"
echo.
echo.
echo  ?REPOSITORIO LISTO!
echo.
echo  Para SUBIR a GitHub, ejecuta estos comandos:
echo.
echo git remote add origin https://github.com/TU_USUARIO/sistema-monitoreo-inteligente.git
echo git branch -M main
echo git push -u origin main
echo.
goto :END

:ACTUALIZAR
echo.
echo  Actualizando cambios en GitHub...
git add .
git commit -m "Actualizacion: %date% %time%"
git push origin main
echo  Cambios subidos exitosamente!
goto :END

:DASHBOARD
echo.
echo  Iniciando Dashboard Streamlit...
cd dashboard_streamlit
if exist "requirements.txt" (
   echo Instalando dependencias...
   pip install -r requirements.txt
)
streamlit run app.py
cd ..

:END
echo.
pause
