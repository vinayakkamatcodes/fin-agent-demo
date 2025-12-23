import streamlit as st
import os
import sys
import pandas as pd

# Add the current directory to Python path so we can import our agent
sys.path.append(os.path.dirname(__file__))

# Import the brain (agent_graph) AND the database logic (portfolio)
# We need 'portfolio' to draw the chart without asking the AI
from agent.graph import agent_graph, portfolio

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FinAgent Pro",
    page_icon="📈",
    layout="wide"  # Use wide mode for a dashboard feel
)

st.title("📈 FinAgent: AI Financial Analyst")
st.caption("Powered by Gemini, MCP, and RAG")

# --- SIDEBAR: SETTINGS & DASHBOARD ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key Input
    # We check if it's already in the environment (from code) or needs input
    if "GOOGLE_API_KEY" not in os.environ:
        google_api_key = st.text_input("Google API Key", type="password")
        if google_api_key:
            os.environ["GOOGLE_API_KEY"] = google_api_key
            st.success("Key Saved!")
    
    st.divider()
    
    # --- LIVE PORTFOLIO CHART ---
    st.subheader("📊 Live Portfolio")
    
    # 1. Fetch data directly from our SQLite DB
    trades = portfolio.list_trades()
    
    if trades:
        # 2. Convert list of dicts to a Pandas DataFrame
        df = pd.DataFrame(trades)
        
        # 3. Calculate "Total Value" for each trade
        df["Current Value"] = df["shares"] * df["price"]
        
        # 4. Group by Ticker (sums up multiple buys of the same stock)
        chart_data = df.groupby("ticker")["Current Value"].sum()
        
        # 5. Display Total Net Worth
        total_value = chart_data.sum()
        st.metric(label="Total Net Worth", value=f"${total_value:,.2f}")
        
        # 6. Draw the Bar Chart
        st.bar_chart(chart_data)
        
    else:
        st.info("No trades yet. Tell the AI to buy something!")

# --- MAIN LAYOUT (Columns) ---
# Left: Chat (wider), Right: Trade Log (narrower)
col1, col2 = st.columns([2, 1])

# --- COLUMN 1: CHAT INTERFACE ---
with col1:
    st.subheader("💬 Chat")

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I can track your trades and analyze market reports. Try saying 'I bought 10 AAPL at 150'."}
        ]

    # Display Chat History
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # User Input
    if prompt := st.chat_input("Type your financial command..."):
        # Check API Key
        if "GOOGLE_API_KEY" not in os.environ:
            st.warning("Please enter your Google API Key in the sidebar.")
            st.stop()

        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Get AI Response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing market data..."):
                try:
                    # Invoke the Agent
                    response = agent_graph.invoke({"messages": [("user", prompt)]})
                    ai_response = response["messages"][-1].content
                    
                    st.write(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                    # --- CRITICAL: REFRESH THE PAGE ---
                    # If the AI added a trade, we want the Chart in the sidebar 
                    # to update immediately.
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# --- COLUMN 2: RAW DATA TABLE ---
with col2:
    if trades:
        st.subheader("📋 Trade Log")
        # Show a clean table of the trades
        st.dataframe(
            df[["ticker", "shares", "price", "Current Value"]], 
            hide_index=True,
            use_container_width=True
        )