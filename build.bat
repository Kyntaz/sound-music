@echo off
CALL conda.bat activate ./venv
cd app
python -m eel start.py ui --hidden-import="sklearn.utils._cython_blas" --hidden-import="sklearn.neighbors.typedefs" --hidden-import="sklearn.neighbors.quad_tree" --hidden-import="sklearn.tree._utils" --noconsole --name "SoundMusic"