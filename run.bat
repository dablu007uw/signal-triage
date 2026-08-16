@echo off
REM Double-click this file to run the Signal Triage Digest.
REM It runs from whatever folder it lives in, so no typing needed.
cd /d "%~dp0"
python triage.py --input sample_data --output digest.md --expect slack,email,pfr
echo.
echo ============================================================
echo Done. Digest written to digest.md in this folder.
echo (Leave this window open and screenshot it for your submission.)
echo ============================================================
pause
