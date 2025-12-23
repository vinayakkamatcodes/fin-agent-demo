from mcp.server.fastmcp import FastMCP
from portfolio_server import PortfolioServer

# 1. Initialize the MCP Server
# This name "Financial Advisor" is what the AI will see as the source of tools
mcp = FastMCP("Financial Advisor")

# 2. Initialize your database logic
# We use a persistent file so data is saved between runs
portfolio = PortfolioServer("live_portfolio.db")

# 3. Expose the "add_trade" function as an AI Tool
@mcp.tool()
def add_trade(ticker: str, shares: int, price: float) -> str:
    """
    Adds a stock trade to the portfolio. 
    Use this when the user mentions buying shares.
    """
    # We simply call the logic we already tested!
    return portfolio.add_trade(ticker, shares, price)

# 4. Expose the "list_trades" function as an AI Tool
@mcp.tool()
def list_trades() -> str:
    """
    Lists all trades currently in the portfolio.
    Use this when the user asks what they own or for a summary.
    """
    trades = portfolio.list_trades()
    return str(trades)

# 5. Run the server
if __name__ == "__main__":
    mcp.run()