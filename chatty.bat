@echo off

set "SCRIPT_DIR=%~dp0"
echo Script directory: %SCRIPT_DIR%

cd %SCRIPT_DIR%\..
call Scripts\activate

cd bot
if exist chatty.env.bat (
    call chatty.env.bat
)
python bot.py