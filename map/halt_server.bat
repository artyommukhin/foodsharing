@echo off

start /d nginx /b nginx.exe -s quit
taskkill /IM php-cgi.exe /f > nul