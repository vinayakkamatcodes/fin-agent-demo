import sqlite3

class PortfolioServer:
    def __init__(self, db_path="portfolio.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the trades table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                shares INTEGER NOT NULL,
                price REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add_trade(self, ticker: str, shares: int, price: float) -> str:
        """Adds a trade to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trades (ticker, shares, price) VALUES (?, ?, ?)",
                (ticker.upper(), shares, price)
            )
            conn.commit()
            conn.close()
            return f"Successfully added {shares} shares of {ticker} at ${price}."
        except Exception as e:
            return f"Error adding trade: {str(e)}"

    def list_trades(self) -> list[dict]:
        """Returns all trades."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This lets us access columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades")
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to a list of regular dictionaries
        return [dict(row) for row in rows]