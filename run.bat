@echo off
:loop
echo [%date% %time%] Khoi chay BOT AUTO CONTENT...
call .venv\Scripts\activate
python main.py
echo [%date% %time%] Script bi dung hoac crash. Se tu dong restart sau 10 giay...
timeout /t 10
goto loop
