@echo off
title BTL CSATTT - Demo Cac Giai Thuat Bam
chcp 65001 >nul
color 0b

:MENU
cls
echo =====================================================================
echo           BAI TAP LON CO SO AN TOAN THONG TIN - NHOM 08
echo               De tai: Nghien cuu cac giai thuat bam
echo =====================================================================
echo.
echo   [1] Chay Server SHA-512       (Kiem tra tinh toan ven)
echo   [2] Chay Client SHA-512       (Gui text, file, anh, video)
echo   -------------------------------------------------------------------
echo   [3] Chay Server nan nhan      (Muc 5.3: Second Preimage)
echo   [4] Chay Tool tan cong        (Brute-force tim va cham tien to)
echo   -------------------------------------------------------------------
echo   [5] Mo phong Pass-the-Hash    (Chay gia lap NTLM Auth bang Python)
echo   [6] Mo Web Dashboard          (Giao dien truc quan tren trinh duyet)
echo   [7] Mo Kali Linux (WSL2)      (Thuc chien Impacket Pass-the-Hash)
echo   -------------------------------------------------------------------
echo   [0] Thoat
echo =====================================================================
set /p choice="Nhap lua chon cua ban [0-7]: "

if "%choice%"=="1" goto RUN_SERVER1
if "%choice%"=="2" goto RUN_CLIENT1
if "%choice%"=="3" goto RUN_SERVER2
if "%choice%"=="4" goto RUN_ATTACK2
if "%choice%"=="5" goto RUN_PTH
if "%choice%"=="6" goto RUN_WEB
if "%choice%"=="7" goto RUN_KALI
if "%choice%"=="0" exit
goto MENU

:RUN_SERVER1
echo Dang mo Server SHA-512 trong cua so moi...
start "Server SHA-512 (Port 12001)" cmd /k "cd /d "%~dp0sha512" && python server.py"
goto MENU

:RUN_CLIENT1
echo Dang mo Client SHA-512 trong cua so moi...
start "Client SHA-512" cmd /k "cd /d "%~dp0sha512" && python client.py"
goto MENU

:RUN_SERVER2
echo Dang mo Server nan nhan trong cua so moi...
start "Victim Server (Port 12002)" cmd /k "cd /d "%~dp0preimage" && python server.py"
goto MENU

:RUN_ATTACK2
echo Dang mo Tool tan cong tien anh trong cua so moi...
start "Attack Preimage" cmd /k "cd /d "%~dp0preimage" && python attack.py"
goto MENU

:RUN_PTH
cls
cd /d "%~dp0pth"
python pth_sim.py
echo.
pause
goto MENU

:RUN_WEB
echo Dang khoi dong Web Dashboard (Flask)...
start "Web Dashboard" cmd /k "cd /d "%~dp0web" && python app.py"
timeout /t 2 >nul
start http://127.0.0.1:5000
goto MENU

:RUN_KALI
echo Dang mo Kali Linux trong cua so moi...
start "Kali Linux (WSL2)" wsl.exe -d kali-linux -u root
goto MENU
