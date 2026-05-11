import subprocess
import time
import os

os.chdir(r"c:\Latest Environment (16.04.25)\my_new_env\AI Assistant")

print("Starting Flask with debug output...")

# Start Flask and redirect output to a file
with open('flask_output.log', 'w') as logfile:
    proc = subprocess.Popen(
        ['python', 'app_debug.py'],
        stdout=logfile,
        stderr=subprocess.STDOUT,
        text=True
    )
    print(f"Flask started with PID: {proc.pid}")
    print("Logging to flask_output.log")

# Keep the script running
time.sleep(60)
