#!/usr/bin/env python
import sys
print("Python version:", sys.version)

try:
    print("[OK] Importing Flask...", flush=True)
    from flask import Flask
    print("[OK] Flask imported", flush=True)

    print("[OK] Importing LangChain...", flush=True)
    from langchain_ollama import ChatOllama
    print("[OK] LangChain imported", flush=True)

    print("[OK] Importing LangGraph...", flush=True)
    from langgraph.graph import StateGraph
    print("[OK] LangGraph imported", flush=True)

    print("[OK] Importing app module...", flush=True)
    import app
    print("[OK] App module imported successfully!", flush=True)

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
