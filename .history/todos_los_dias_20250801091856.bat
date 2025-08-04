@echo off
REM --- Ir a la carpeta del script ---
cd /d C:\Users\svega\Downloads\todos los dias
:inicio
REM --- Ejecutar el script ---
python prueba_selenium.py

REM --- Mantener la ventana abierta para ver logs ---
goto :inicio