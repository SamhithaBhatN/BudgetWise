@echo off
title BudgetWise Upgrade

call .venv\Scripts\activate

python -m flask --app run.py db upgrade

pause