@echo off
REM ----------| main
call :cmd_%1 %2 %3 %4 %5 %6 %7 %8 %9
exit 0

REM ----------| build equations
:cmd_eqs
    for /d %%i in (.\sections\*) do call ".\app\type2tex.bat" "%%i\eqs"
    exit /B 0
REM ----------| 
