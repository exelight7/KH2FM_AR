@echo off
setlocal
cd /d "%~dp0"
"%~dp0tools\node.exe" "%~dp0scripts\manual.cjs" verify %*
set "result=%errorlevel%"
echo.
pause
exit /b %result%
