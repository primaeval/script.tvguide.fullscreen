@echo off
set url=%*
echo %*
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"

set dt=%YYYY%%MM%%DD%%HH%%Min%%Sec%
echo %dt%
echo %dt% %url% >> C:\Kodi16.1\portable_data\userdata\recordings.txt 

rem c:\utils\ffmpeg.exe -i %* -map 0:p:1 -c copy C:\Kodi16.1\portable_data\userdata\out.ts
c:\utils\ffmpeg.exe -y -i %*  -c copy  -t 04:00:00 C:\Kodi16.1\portable_data\userdata\%dt%.avi
rem set /p DUMMY=Hit ENTER to continue...
