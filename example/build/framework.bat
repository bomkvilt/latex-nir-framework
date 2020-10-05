@echo off
pushd %~dp0
del framework
cmd /c mklink /D framework ..\..
popd
