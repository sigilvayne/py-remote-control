@echo off
set NSSM=C:\Script\agent\nssm-2.24\win64\nssm.exe
set SERVICE_NAME=AgentService
set EXECUTABLE=C:\Script\agent\agent.exe

echo Installing %SERVICE_NAME%...
"%NSSM%" install %SERVICE_NAME% "%EXECUTABLE%"

echo Setting service to start automatically...
sc config %SERVICE_NAME% start= auto

echo Starting service...
net start %SERVICE_NAME%

echo Done.
pause
