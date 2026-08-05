@echo off
title BudgetWise Migration

call .venv\Scripts\activate

python -m flask --app run.py db migrate -m "%1"

pause