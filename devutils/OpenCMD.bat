@ECHO OFF
set THIS=%~0
set THIS_FOLDER=%~dp0

set PENVSTP_VENV_PATH=%THIS_FOLDER%..\..\tools\penvstpPyVenv

IF [%1] EQU [] (
  echo VENV destination not provided
  call :usage
  echo Using: %PENVSTP_VENV_PATH%
) else (
  set PENVSTP_VENV_PATH=%1
)

SET PATH=^
%PENVSTP_VENV_PATH%\Scripts\;^
%PATH%
  :: Existing %PATH% at the end because it might contain %userprofile%\AppData\Local\Microsoft\WindowsApps with some executable shortcuts to the app store, e.g. python.exe

goto end

:usage
echo ^> Usage: %THIS% [DESTIANTION_VENV_FOLDER_PATH]
echo ^> Example: %THIS% .\tools\penvstpPyVenv
goto :eof

:end
CD %THIS_FOLDER%\..\

cmd /k