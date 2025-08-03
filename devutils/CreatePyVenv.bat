@ECHO OFF
set THIS_PATH=%~0

set THIS_FOLDER=%~dp0
set SRC_PYTHON
set PENVSTP_VENV_PATH

for %%I in ("%THIS_FOLDER%..\..\Tools\Python\python.exe") do set "SRC_PYTHON=%%~fI"
for %%I in ("%THIS_FOLDER%..\..\Tools\penvstpPyVenv") do set "PENVSTP_VENV_PATH=%%~fI"


IF [%1] EQU [] (
  echo Source Python not provided
  call :usage
  echo Using: %SRC_PYTHON%
  pause
) else (
  set SRC_PYTHON=%1
)

IF [%2] EQU [] (
  echo VENV destination not provided
  call :usage
  echo Using: %PENVSTP_VENV_PATH%
  pause
) else (
  set PENVSTP_VENV_PATH=%2
)

%SRC_PYTHON% -m venv %PENVSTP_VENV_PATH%
SET PENVSTP_PYTHON=%PENVSTP_VENV_PATH%\scripts\python.exe
 
%PENVSTP_PYTHON% -m pip install -r %~dp0PythonRequirements.txt

goto end

:usage
echo ^> Usage: %THIS_PATH% [SOURCE_PYTHON [DESTIANTION_VENV_FOLDER_PATH]]
echo ^> Example: %THIS_PATH% python.exe .\Tools\penvstpPyVenv
goto :eof

:end

PAUSE
