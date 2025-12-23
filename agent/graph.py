import os
import getpass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
# Add this import
import sys
# (Assuming lines 15-16 exist for path appending)
sys.path.append(os.path.join(os.path.dirname(__file__), '../server'))
from portfolio_server import PortfolioServer
from rag_tool import ask_market_analyst  # <--- NEW IMPORT

# --- 1. SETUP API KEY ---
# It will ask for your key if not found in environment variables
if "GOOGLE_API_KEY" not in os.environ:
    pass # set it in .env

# --- 2. CONNECT TO OUR TOOLS ---
# We import the EXACT same logic our MCP server uses.
# This ensures our Agent and our MCP Server are always in sync.
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../server'))
from portfolio_server import PortfolioServer

# Initialize the logic
portfolio = PortfolioServer("live_portfolio.db")

# Wrap them as LangChain Tools so the Agent can understand them
@tool
def add_trade_tool(ticker: str, shares: int, price: float) -> str:
    """Adds a trade to the portfolio. Use this when the user buys stock."""
    return portfolio.add_trade(ticker, shares, price)

@tool
def list_trades_tool() -> str:
    """Lists all trades. Use this to see what the user owns."""
    trades = portfolio.list_trades()
    return str(trades)

tools = [add_trade_tool, list_trades_tool, ask_market_analyst]

# --- 3. SETUP THE MODEL (GEMINI) ---
# We use 'gemini-1.5-flash' because it is fast and cheap (free tier)
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# --- 4. CREATE THE AGENT GRAPH ---
# LangGraph has a pre-built function 'create_react_agent' that makes 
# the "Think -> Act -> Loop" structure automatically.
agent_graph = create_react_agent(model, tools)

# --- 5. RUN FUNCTION (To test it) ---
def run_chat():
    print("--- FinAgent (Gemini) Started ---")
    print("Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        
        # Stream the events so we can see what the agent is doing
        events = agent_graph.stream(
            {"messages": [("user", user_input)]},
            stream_mode="values"
        )
        
        for event in events:
            # The last message in the list is the latest response
            event["messages"][-1].pretty_print()

if __name__ == "__main__":
    run_chat()