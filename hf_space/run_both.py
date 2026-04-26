import subprocess
import sys
import os

print("Starting Uvicorn API Server...")
uvicorn_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"])

print("Starting Telegram Bot...")
# Running the bot separately cleanly isolates its Asyncio Event Loop from Bash Background '&' signaling bugs
bot_process = subprocess.Popen([sys.executable, "agents/telegram_bot.py"])

try:
    uvicorn_process.wait()
except KeyboardInterrupt:
    uvicorn_process.terminate()
    bot_process.terminate()
