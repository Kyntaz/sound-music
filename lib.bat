@echo off
CALL conda.bat activate ./venv
cd src
python -i -c "import SoundMusic as sm"