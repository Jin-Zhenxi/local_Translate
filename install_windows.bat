@echo off
title Real-Time Translator Installer

echo ===================================================
echo   Real-Time Translator - Windows Installer
echo ===================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.10+ from python.org and ensure "Add to PATH" is checked.
    pause
    exit /b
)

:: Create the local configuration from the portable template.
if not exist config.ini (
    echo [Setup] Creating config.ini from config.ini.example...
    copy /Y config.ini.example config.ini >nul
)

:: Ensure Git LFS materialized both runtime models.
if not exist "models\faster-whisper-base.en\model.bin" goto fetch_models
if not exist "models\opus-mt-en-zh-int8\model.bin" goto fetch_models
for %%F in ("models\faster-whisper-base.en\model.bin") do if %%~zF LSS 1000000 goto fetch_models
for %%F in ("models\opus-mt-en-zh-int8\model.bin") do if %%~zF LSS 1000000 goto fetch_models
goto models_ready

:fetch_models
echo [Setup] Fetching runtime models with Git LFS...
git lfs version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git LFS is required. Install Git for Windows with Git LFS, then run this installer again.
    pause
    exit /b 1
)
git lfs install
git lfs pull
if not exist "models\faster-whisper-base.en\model.bin" goto model_error
if not exist "models\opus-mt-en-zh-int8\model.bin" goto model_error
for %%F in ("models\faster-whisper-base.en\model.bin") do if %%~zF LSS 1000000 goto model_error
for %%F in ("models\opus-mt-en-zh-int8\model.bin") do if %%~zF LSS 1000000 goto model_error
goto models_ready

:model_error
echo [ERROR] Runtime models are missing or are still Git LFS pointer files.
echo Run "git lfs pull" in this repository and try again.
pause
exit /b 1

:models_ready
echo [Setup] Runtime models are ready.

:: Create Virtual Environment
if not exist .venv (
    echo [1/3] Creating virtual environment .venv...
    python -m venv .venv
) else (
    echo [1/3] Virtual environment already exists.
)

:: Activate and Install
echo [2/3] Activating environment and installing dependencies...
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

:: Check FFmpeg (Optional check, hard to verify in bat easily without which, but we can warn)
echo [3/4] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] FFmpeg is not found in PATH.
    echo Whisper requires FFmpeg to process audio.
    echo Please download FFmpeg from https://ffmpeg.org/download.html and add it to your PATH.
    echo.
) else (
    echo FFmpeg found.
)

:: Check Virtual Audio Device
echo [4/4] Checking virtual audio device...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s | findstr /C:"VB-Audio" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Virtual audio device is NOT installed.
    echo VB-CABLE is required to capture system audio, for example games, meetings, or videos.
    echo.
    echo Please download and install VB-CABLE from:
    echo   https://vb-audio.com/Cable/
    echo.
    echo After installation:
    echo   1. Set VB-CABLE as your default playback device
    echo   2. Configure your real speakers to listen to VB-CABLE
    echo   3. Or use Voicemeeter for advanced audio routing
    echo.
) else (
    echo Virtual audio device VB-Audio found.
)

echo.
echo ===================================================
echo   Installation Complete! 
echo   Run 'start_windows.bat' to launch the app.
echo ===================================================
pause
