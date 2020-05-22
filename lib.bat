@echo off
CALL conda.bat activate ./venv
cd app
python -i -c "import SoundMusic as sm"