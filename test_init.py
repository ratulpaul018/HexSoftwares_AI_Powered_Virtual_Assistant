print("Starting initialization test...")

try:
    print("1. Importing Flask...")
    from flask import Flask
    print("   OK")

    print("2. Importing LangChain tools...")
    from langchain.tools import tool
    print("   OK")

    print("3. Importing ChatOllama...")
    from langchain_ollama import ChatOllama
    print("   OK")

    print("4. Importing LangGraph...")
    from langgraph.prebuilt import create_react_agent
    print("   OK")

    print("5. Initializing ChatOllama (connecting to localhost:11434)...")
    llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")
    print("   OK - ChatOllama initialized")

    print("6. Testing LLM with simple message...")
    test_response = llm.invoke([{"role": "user", "content": "Say 'Hello'"}])
    print(f"   OK - LLM responded: {test_response.content[:50]}")

    print("\nAll tests passed! Agent can be created.")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
