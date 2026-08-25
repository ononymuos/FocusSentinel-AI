@echo off
title FocusSentinel AI
cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
python main.py
pause
