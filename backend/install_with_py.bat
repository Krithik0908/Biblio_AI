@echo off
cd /d "C:\Users\DELL\Desktop\biblioAI\backend"

echo Installing Bibleo packages with py command...
echo Python version: 
py --version
echo.

py -m pip install --upgrade pip

py -m pip install sqlalchemy==2.0.23
py -m pip install fastapi==0.104.1
py -m pip install uvicorn[standard]==0.24.0
py -m pip install aiosqlite==0.19.0
py -m pip install python-jose[cryptography]==3.3.0
py -m pip install passlib[bcrypt]==1.7.4
py -m pip install email-validator==2.1.1
py -m pip install python-dotenv==1.0.0

echo.
echo ✅ Installation complete!
echo.
echo Run: py -m uvicorn app.main:app --reload
pause