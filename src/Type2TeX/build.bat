@echo off
REM ----------| main
call :cmd_%1 %2 %3 %4 %5 %6 %7 %8 %9
exit 1

REM ----------| build script
:cmd_build
call pyinstaller --onefile  ^
    --distpath=../../app    ^
    --workpath=build        ^
    --name=type2tex         ^
    .\main.py
    exit 0

REM ----------| generate toks
:cmd_toks
    call python "utiles/findTokens.py" "mmltex/" "utiles/tokens.json"
    exit 0
