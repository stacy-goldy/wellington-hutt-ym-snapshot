import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="YM Snapshot", layout="wide", page_icon="⛪")
st.title("Wellington & Hutt Stake • YM Snapshot Tracker")

# Initialize data
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []

wards = ["Wellington Ward", "Hataitai Ward", "Hutt Valley Ward", "Avalon Branch",
         "Lower Hutt Ward", "Upper Hutt Ward", "Wairarapa Ward"]

# ==================== SIDEBAR - NEW SNAPSHOT ====================
with st.sidebar:
    st.header("Submit New Snapshot")
    
    ward = st.selectbox("Ward / Unit", wards)
    
    # Month selector
    months = []
    current = datetime.now()
    for i in range(12):
        d = current.replace(day=1) - pd.DateOffset(months=i)
        months.append(d.strftime("%Y-%m"))
    month = st.selectbox("Month", months, index=0)

    # Updated Leadership Section with clear guide text
    st.write("**1. Youth Leadership Check (1-5)**")
    st.caption("**How involved were quorum members in activity planning:** 1 = entirely planned by adult leaders, 5 = entirely planned by youth leaders")
    
    # Custom styled slider with visible numbers
    leadership = st.slider("", 1, 5, 3, label_visibility="collapsed")
    
    # Display numbers below slider
    cols = st.columns(5)
    for i, col in enumerate(cols, 1):
        if i == leadership:
            col.markdown(f"<p style='text-align:center; color:#ef4444; font-weight:bold;'>{i}</p>", unsafe_allow_html=True)
        else:
            col.markdown(f"<p style='text-align:center; color:#6b7280;'>{i}</p>", unsafe_allow_html=True)

    st.write("**2. The Four Areas Check**")
    st.caption("During this month, which of the four focus areas were activities centred around:")
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
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.snapshots.insert(0, new_entry)
        st.success(f"✅ Snapshot saved for **{ward}** ({month})")
        st.rerun()

# ==================== MAIN DASHBOARD ====================
df = pd.DataFrame(st.session_state.snapshots)

if not df.empty:
    st.subheader("📊 Stake Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Snapshots", len(df))
    col2.metric("Average Leadership", f"{df['leadership'].mean():.1f}/5")
    
    if 'month' in df.columns:
        latest_month = df['month'].max()
        monthly_avg = df[df['month'] == latest_month]['leadership'].mean()
        col3.metric("Monthly Progress", f"{monthly_avg:.1f}/5", latest_month)

    st.subheader("Leadership Distribution")
    st.bar_chart(df['leadership'].value_counts().sort_index())

    st.subheader("Four Areas Coverage")
    area_data = {
        "Spiritual": df['spiritual'].sum() if 'spiritual' in df.columns else 0,
        "Social": df['social'].sum() if 'social' in df.columns else 0,
        "Physical": df['physical'].sum() if 'physical' in df.columns else 0,
        "Mental": df['mental'].sum() if 'mental' in df.columns else 0
    }
    st.bar_chart(area_data)

    st.subheader("Ward Performance")
    if 'ward' in df.columns and 'leadership' in df.columns:
        ward_avg = df.groupby("ward")["leadership"].mean().round(1)
        st.bar_chart(ward_avg)

    st.subheader("All Snapshots")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

else:
    st.info("No snapshots yet. Use the sidebar to submit the first one.")

st.caption("All data is saved in your browser session.")