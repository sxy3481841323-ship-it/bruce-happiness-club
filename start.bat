@echo off
cd /d "%~dp0"
echo Starting Bruce Happiness Club server on http://127.0.0.1:8781/ ...
where py >nul 2>nul && (
  py -3 scripts/dev_server.py --port 8781 --open
  goto :end
)
where python >nul 2>nul && (
  python scripts/dev_server.py --port 8781 --open
  goto :end
)
where python3 >nul 2>nul && (
  python3 scripts/dev_server.py --port 8781 --open
  goto :end
)
echo Python 3 not found. Please install Python 3 from https://www.python.org/
pause
:end
