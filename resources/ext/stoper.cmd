echo %*
rem c:\utils\ffmpeg.exe -i %*
rem set /p DUMMY=Hit ENTER to continue...
rem c:\utils\ffmpeg.exe -i %* -map 0:p:1 -c copy C:\Kodi16.1\portable_data\userdata\out.ts
rem c:\utils\ffmpeg.exe -y -i %*  -c copy  C:\Kodi16.1\portable_data\userdata\out.ts
rem set /p DUMMY=Hit ENTER to continue...

@echo off &setlocal

set "process=ffmpeg.exe"

for /f "tokens=2" %%i in ('tasklist /nh /fi "imagename eq %process%" 2^>nul') do set PID=%%i
taskkill /F /pid %PID%