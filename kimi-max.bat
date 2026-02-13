@echo off
chcp 65001 >nul
title Kimi CLI - Max Power
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   🔥 INICIANDO KIMI CLI - MODO MAXIMO PODER                     ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Verificar PowerShell 7+
powershell -Command "if ($PSVersionTable.PSVersion.Major -lt 7) { exit 1 }" 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Se requiere PowerShell 7 o superior
    echo    Descarga desde: https://github.com/PowerShell/PowerShell/releases
    pause
    exit /b 1
)

:: Ejecutar script PowerShell con todos los argumentos
powershell -ExecutionPolicy Bypass -File "%~dp0kimi-max.ps1" %*

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error al ejecutar Kimi CLI
    pause
)
