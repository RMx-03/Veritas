@echo off
REM Quick activation script for Windows
call venv\Scripts\activate.bat

echo Virtual environment activated!
echo Current Python: 
python --version
echo.
echo Available commands:
echo   uvicorn main:app --reload --host 0.0.0.0 --port 8000  (start server)
echo   python test_api.py                                    (test API)
echo   deactivate                                            (exit venv)
echo.
