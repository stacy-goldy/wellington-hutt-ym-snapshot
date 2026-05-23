import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="YM Snapshot", layout="wide")
st.title("Wellington & Hutt Stake • YM Snapshot Tracker")

# Initialize data
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []

wards = ["Wellington Ward", "Hataitai Ward", "Hutt Valley Ward", "Avalon Branch", 
         "Lower Hutt Ward", "Upper Hutt Ward", "Wairarapa Ward"]

# Sidebar - New Snapshot
with st.sidebar:
    st.header("New Snapshot")
    ward = st.selectbox("Ward / Unit", wards)
    month = st.selectbox("Month", 
                        [datetime.now().strftime("%Y-%m")] + 
                        [(datetime.now().replace(month=datetime.now().month-i if datetime.now().month-i > 0 else 12, year=datetime.now().year if datetime.now().month-i > 0 else datetime.now().year-1)).strftime("%Y-%m") 
                         for i in range(1, 12)])

    leadership = st.slider("1. Youth Leadership Check (1-5)", 1, 5, 3)
    st.caption("How much are youth presidencies planning & executing activities?")

    st.write("**2. Four Areas Check**")
    spiritual = st.checkbox("Spiritual Growth")
    social = st.checkbox("Social Growth")
    physical = st.checkbox("Physical Growth")
    mental = st.checkbox("Mental Growth")

    support = st.text_area("3. Target Support Needed", placeholder="What can the Stake Presidency help with?")

    if st.button("Submit Snapshot", type="primary"):
        new_entry = {
            "ward": ward,
            "month": month,
            "leadership": leadership,
            "spiritual": spiritual,
            "social": social,
            "physical": physical,
            "mental": mental,
            "support": support,
            "submitted_by": "User",  # Can be enhanced with login later
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        st.session_state.snapshots.insert(0, new_entry)
        st.success(f"Snapshot saved for {ward} ({month})")
        st.rerun()

# Main Dashboard
df = pd.DataFrame(st.session_state.snapshots)

if not df.empty:
    st.subheader("Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Snapshots", len(df))
    col2.metric("Average Leadership", f"{df['leadership'].mean():.1f}/5")
    col3.metric("Monthly Progress", f"{df.groupby('month')['leadership'].mean().iloc[-1]:.1f}/5")

    # Charts
    fig1 = px.bar(df, x="leadership", title="Leadership Score Distribution")
    st.plotly_chart(fig1, use_container_width=True)

    # Heatmap
    heatmap = df.groupby("ward")["leadership"].mean().reset_index()
    fig2 = px.bar(heatmap, x="ward", y="leadership", title="Ward Leadership Heatmap")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("All Snapshots")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

else:
    st.info("No snapshots yet. Use the sidebar to submit the first one.")

st.caption("Data is saved in session for now. For permanent storage, we can connect Google Sheets later.")