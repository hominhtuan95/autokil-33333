@echo off
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller
py -m PyInstaller --onefile --windowed --name AutoSkill_3Skill_Aegis_V25 AutoSkill_3Skill_Aegis_V25.py
if errorlevel 1 (echo Build failed & pause & exit /b 1)
echo EXE created in dist\AutoSkill_3Skill_Aegis_V25.exe
pause
