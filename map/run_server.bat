@echo off

start /d nginx\ /b nginx.exe
start /d nginx\php /b php-cgi.exe -b 127.0.0.1:9000 -c C:\Users\Tam\OneDrive\foodsharing\map\nginx\php\php.ini