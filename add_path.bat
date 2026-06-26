@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo %PATH% | findstr /i "%SCRIPT_DIR%" >nul
if %errorlevel% equ 0 (
    echo [OK] Folder already in current PATH.
) else (
    echo [INFO] Adding folder to current PATH for this session...
    set "PATH=%SCRIPT_DIR%;%PATH%"
)

set "USER_PATH="
for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH 2^>nul') do set "USER_PATH=%%a %%b"
if "%USER_PATH%"=="" set "USER_PATH="

echo %USER_PATH% | findstr /i "%SCRIPT_DIR%" >nul
if %errorlevel% equ 0 (
    echo [OK] Folder already in permanent User PATH.
) else (
    echo [INFO] Adding folder to permanent User PATH...
    if not "%USER_PATH%"=="" (
        setx PATH "%SCRIPT_DIR%;%USER_PATH%"
    ) else (
        setx PATH "%SCRIPT_DIR%"
    )
    echo [OK] Added permanently. Restart terminal if needed for changes to take effect globally.
)

python -m src.pseudogen %*

if %errorlevel% neq 0 (
    echo [WARN] Module 'src.pseudogen' not found, trying 'pseudogen'...
    python -m pseudogen %*
)
