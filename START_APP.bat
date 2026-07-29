@echo off
title SVS Stock App
color 0A
echo.
echo  ==========================================
echo   Silver Violet Studios - Stock Portaal
echo  ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  FOUT: Python nie gevind nie.
    echo  Gaan na https://python.org, laai af en installeer.
    echo  Merk "Add Python to PATH" tydens installasie.
    pause & exit /b 1
)

:: Install packages
echo  Pakkette word nagegaan...
python -c "import tornado" >nul 2>&1
if errorlevel 1 ( pip install tornado --quiet )
python -c "import docx" >nul 2>&1
if errorlevel 1 ( pip install python-docx --quiet )
python -c "import openpyxl" >nul 2>&1
if errorlevel 1 ( pip install openpyxl --quiet )
python -c "import reportlab" >nul 2>&1
if errorlevel 1 ( pip install reportlab --quiet )

:: Init database if first run
if not exist "%USERPROFILE%\svs_stock.db" (
    echo  Databasis word opgeset...
    python db\init.py
)

echo.
echo  ==========================================
echo   App loop op:  http://localhost:3000
echo.
echo   Gilbert@HO  /  1111
echo   Sarie@HO    /  2222
echo   Marius@HO   /  3333
echo  ==========================================
echo.
python server.py
pause
