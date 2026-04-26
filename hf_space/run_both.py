import subprocess
import sys
import time

print("Starting Uvicorn API Server...", flush=True)
uvicorn_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"])

print("Starting Telegram Bot...", flush=True)
bot_process = subprocess.Popen([sys.executable, "-u", "agents/telegram_bot.py"])

try:
    while True:
        if uvicorn_process.poll() is not None:
            print(f"Uvicorn crashed with exit code {uvicorn_process.returncode}", flush=True)
            sys.exit(uvicorn_process.returncode)
        if bot_process.poll() is not None:
            print(f"Telegram Bot crashed with exit code {bot_process.returncode}", flush=True)
            sys.exit(bot_process.returncode)
        time.sleep(1)
except KeyboardInterrupt:
    uvicorn_process.terminate()
    bot_process.terminate()
