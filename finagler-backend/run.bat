@echo off
if not exist .venv312\Scripts\python.exe py -3.12 -m venv .venv312
if not exist .venv312\Scripts\python.exe exit /b 1
call .venv312\Scripts\activate.bat
python -m pip install -q -r requirements.txt
if not exist .env copy .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
