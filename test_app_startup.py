print("Testing app startup...")

try:
    print("1. Importing Flask...")
    from flask import Flask
    print("   OK")

    print("2. Importing ChatOllama...")
    from langchain_ollama import ChatOllama
    print("   OK")

    print("3. Testing create_react_agent import...")
    try:
        from langchain.agents import create_react_agent
        print("   OK - imported from langchain.agents")
    except ImportError:
        print("   FAILED - trying langgraph.prebuilt...")
        from langgraph.prebuilt import create_react_agent
        print("   OK - imported from langgraph.prebuilt")

    print("4. Creating ChatOllama...")
    llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")
    print("   OK")

    print("5. Testing @tool decorator...")
    from langchain.tools import tool

    @tool
    def test_tool(x: str) -> str:
        """Test tool"""
        return f"Got: {x}"

    print("   OK")

    print("6. Creating agent...")
    tools = [test_tool]
    agent = create_react_agent(llm, tools)
    print("   OK - Agent created!")

    print("\nSUCCESS: All checks passed!")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
