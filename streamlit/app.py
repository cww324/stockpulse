"""
StockPulse Dashboard - Main Streamlit App
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="StockPulse",
    page_icon="📈",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_db_connection():
    """Create database connection."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    return create_engine(database_url)

def main():
    # Header
    st.title("📈 StockPulse")
    st.subheader("ML-Powered Stock Analysis Platform")

    # Sidebar
    st.sidebar.header("Settings")
    scoring_model = st.sidebar.radio(
        "Scoring Model",
        ["Rules-Based", "ML", "Hybrid"],
        index=2  # Default to Hybrid
    )

    # Main content
    st.markdown("---")

    # Database connection status
    st.header("System Status")

    col1, col2, col3 = st.columns(3)

    # Test database connection
    engine = get_db_connection()
    if engine:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM factor_weights"))
                count = result.scalar()
                col1.metric("Database", "✅ Connected")
                col2.metric("Factor Weights", f"{count} configured")
        except Exception as e:
            col1.metric("Database", "❌ Error")
            st.error(f"Database error: {e}")
    else:
        col1.metric("Database", "❌ Not configured")

    col3.metric("Scoring Model", scoring_model)

    st.markdown("---")

    # Factor weights from database
    st.header("Scoring Configuration")

    if engine:
        try:
            df = pd.read_sql(
                "SELECT factor_name, weight, description FROM factor_weights ORDER BY factor_name",
                engine
            )

            # Display as nice cards
            cols = st.columns(5)
            for idx, row in df.iterrows():
                with cols[idx % 5]:
                    st.metric(
                        label=row['factor_name'].title(),
                        value=f"{row['weight']*100:.0f}%"
                    )
                    st.caption(row['description'][:50] + "...")
        except Exception as e:
            st.error(f"Error loading factor weights: {e}")

    st.markdown("---")

    # Placeholder for rankings
    st.header("Top 25 Stocks")
    st.info("📊 Stock rankings will appear here once the ETL pipeline runs.")

    # Placeholder dataframe
    placeholder_data = {
        "Rank": range(1, 6),
        "Ticker": ["---", "---", "---", "---", "---"],
        "Company": ["Awaiting data...", "Awaiting data...", "Awaiting data...", "Awaiting data...", "Awaiting data..."],
        "Score": ["--", "--", "--", "--", "--"],
        "Sector": ["--", "--", "--", "--", "--"]
    }
    st.dataframe(pd.DataFrame(placeholder_data), use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption("StockPulse v0.1 | Built with Streamlit | Data updates weekly")

if __name__ == "__main__":
    main()
