@echo off
set NSSM=C:\Script\agent\nssm-2.24\win64\nssm.exe
set SERVICE_NAME=AgentService

echo Stopping service %SERVICE_NAME%...
net stop %SERVICE_NAME%

echo Removing service %SERVICE_NAME%...
"%NSSM%" remove %SERVICE_NAME% confirm

echo Done.
pause
