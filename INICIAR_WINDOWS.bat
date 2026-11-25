@echo off
cd /d "%~dp0"
where py >NUL 2>NUL
if %errorlevel%==0 (
  set "PY=py"
) else (
  set "PY=python"
)
echo ============================================
echo    PROYECTO 20 - ENTRENADOR ULIMA
echo ============================================
echo Instalando o comprobando Streamlit...
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo ERROR: No se pudo instalar Streamlit. Comprueba Python e Internet.
  pause
  exit /b 1
)
echo.
echo Abriendo http://localhost:8501
%PY% -m streamlit run app.py
pause
