@echo off

set "SCRIPT_DIR=%~dp0"
echo Script directory: %SCRIPT_DIR%

call Scripts\activate

if exist chatty.env.bat (
    call chatty.env.bat
)
python bot.py