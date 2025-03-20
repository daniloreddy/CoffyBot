@echo off

set "SCRIPT_DIR=%~dp0"
echo Script directory: %SCRIPT_DIR%

call %SCRIPT_DIR%\coffy-env\Scripts\activate

if exist chatty.env.bat (
    call chatty.env.bat
)
python chatty.db.py