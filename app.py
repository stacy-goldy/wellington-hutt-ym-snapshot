import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="YM Snapshot", layout="wide", page_icon="⛪")
st.title("Wellington & Hutt Stake • YM Snapshot Tracker")

# Initialize session data
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []

wards = ["Wellington Ward", "Hataitai Ward", "Hutt Valley Ward", "Avalon Branch",
         "Lower Hutt Ward", "Upper Hutt Ward", "Wairarapa Ward"]

# ==================== SIDEBAR - NEW SNAPSHOT ====================
with st.sidebar:
    st.header("Submit New Snapshot")
    
    ward = st.selectbox("Ward / Unit", wards)
    
    # Safe month selector (last 12 months)
    months = []
    current = datetime.now()
    for i in range(12):
        d = current.replace(day=1) - pd.DateOffset(months=i)
        months.append(d.strftime("%Y-%m"))
    
    month = st.selectbox("Month", months, index=0)

    leadership = st.slider("1. Youth Leadership Check (1-5)", 1, 5, 3, 
                          help="How much are the youth presidencies actually planning and running activities?")

    st.write("**2. The Four Areas Check** (select all that apply)")
    spiritual = st.checkbox("Spiritual Growth")
    social = st.checkbox("Social Growth")
    physical = st.checkbox("Physical Growth")
    mental = st.checkbox("Mental Growth")

    support = st.text_area("3. Target Support Needed", 
                          placeholder="What is the #1 thing the Stake Presidency can help with next month?")

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
            "submitted_by": "Stake Leader",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.snapshots.insert(0, new_entry)
        st.success(f"Snapshot saved for **{ward}** ({month})")
        st.rerun()

# ==================== MAIN DASHBOARD ====================
df = pd.DataFrame(st.session_state.snapshots)

if not df.empty:
    st.subheader("📊 Stake Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Snapshots", len(df))
    col2.metric("Average Leadership", f"{df['leadership'].mean():.1f}/5")
    
    # Monthly Progress (most recent month)
    latest_month = df['month'].max()
    monthly_df = df[df['month'] == latest_month]
    monthly_avg = monthly_df['leadership'].mean() if not monthly_df.empty else 0
    col3.metric("Monthly Progress", f"{monthly_avg:.1f}/5", f"{latest_month}")

    # Charts
    st.subheader("Leadership Distribution")
    st.bar_chart(df['leadership'].value_counts().sort_index())

    st.subheader("Four Areas Coverage")
    area_data = {
        "Spiritual": df['spiritual'].sum(),
        "Social": df['social'].sum(),
        "Physical": df['physical'].sum(),
        "Mental": df['mental'].sum()
    }
    st.bar_chart(area_data)

    st.subheader("Ward Performance")
    ward_avg = df.groupby("ward")["leadership"].mean().round(1)
    st.bar_chart(ward_avg)

    st.subheader("All Snapshots")
    display_df = df.sort_values("date", ascending=False)
    st.dataframe(display_df, use_container_width=True)

else:
    st.info("No snapshots submitted yet. Use the sidebar to add the first one.")

st.caption("Data is saved in your browser session for now.")