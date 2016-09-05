@echo off
set url=%*
echo %*
for /f "tokens=2,3,4 delims=/ " %%f in ('date /t') do set d=%%h%%g%%f
for /f "tokens=1,2,3 delims=: " %%f in ('echo %time%') do set t=%%f%%g%%h
set dt=%d%%t%
echo %dt%

echo %dt% %url% >> C:\Kodi16.1\portable_data\userdata\recordings.txt 

rem c:\utils\ffmpeg.exe -i %* -map 0:p:1 -c copy C:\Kodi16.1\portable_data\userdata\out.ts
c:\utils\ffmpeg.exe -y -i %*  -c copy  -t 04:00:00 C:\Kodi16.1\portable_data\userdata\%dt%.ts
rem set /p DUMMY=Hit ENTER to continue...