#!/usr/bin/env python
import subprocess
import sys
import os

os.chdir(r"c:\Latest Environment (16.04.25)\my_new_env\AI Assistant")

print("Running Flask app directly to capture errors...")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "app.py"],
    capture_output=True,
    text=True,
    timeout=20
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print("\nReturn code:", result.returncode)
