@echo off
:inicio
:: Mantener ventana abierta
title Todos los dias formulario automatizado
echo ==========================================
echo   INICIANDO AUTOMATIZACION DE FORMULARIO
echo ==========================================
:: Ir a la carpeta del script
cd /d "C:\Users\svega\Downloads\todos los dias"

:: Ejecutar el script

python prueba_selenium.py

echo.
echo ==========================================
echo  AUTOMATIZACION FORMULARIO FINALIZADA
echo ==========================================
goto :inicio