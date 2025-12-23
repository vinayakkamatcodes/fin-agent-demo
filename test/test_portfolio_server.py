import pytest
import sqlite3
import os

# We are importing the server class we haven't written yet.
# This will cause an ImportError, which is our first "Failure".
# We assume our server file will be named 'portfolio_server.py' inside the 'server' folder.
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../server'))
from portfolio_server import PortfolioServer

DB_PATH = "test_portfolio.db"

@pytest.fixture
def clean_db():
    """Setup: Create a fresh DB path before test. Teardown: Delete it after."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield DB_PATH
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_initialize_database(clean_db):
    """Test 1: Does the server create the table correctly?"""
    # Initialize our Server
    server = PortfolioServer(clean_db)
    
    # Check if the file was created
    assert os.path.exists(clean_db)
    
    # Connect and check if table 'trades' exists
    conn = sqlite3.connect(clean_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades';")
    table_exists = cursor.fetchone()
    conn.close()
    
    assert table_exists is not None, "Table 'trades' was not created."

def test_add_and_list_trade(clean_db):
    """Test 2: Can we add a trade and see it?"""
    server = PortfolioServer(clean_db)
    
    # Add a trade (Ticker, Amount, Price)
    result = server.add_trade("AAPL", 10, 150.00)
    assert "success" in result.lower()
    
    # List trades to verify
    trades = server.list_trades()
    assert len(trades) == 1
    assert trades[0]['ticker'] == "AAPL"
    assert trades[0]['shares'] == 10
    assert trades[0]['price'] == 150.00