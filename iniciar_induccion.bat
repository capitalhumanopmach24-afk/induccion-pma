@echo off
cd /d "%~dp0"
if not exist ".venv" (
  echo Preparando por primera vez, esto tarda unos minutos...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)
rem Puerto 8502 para no chocar con el dashboard de Asistencia (8501)
streamlit run app.py --server.port 8502
pause
