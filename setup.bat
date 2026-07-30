@echo off
cd /d "%~dp0"
"C:\Users\MR\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_initial_data
python manage.py setup_roles
python manage.py generate_yearly_sample_data
python manage.py check
