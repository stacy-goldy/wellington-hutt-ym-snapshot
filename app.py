import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="YM Snapshot", layout="wide", page_icon="⛪")

# Custom Header
st.markdown("""
    <h1 style='text-align: center; color: #002f6c; font-size: 2.8rem; margin-bottom: 0;'>
        Wellington & Hutt Stake
    </h1>
    <h2 style='text-align: center; color: #f59e0b; margin-top: 0; font-weight: 500;'>
        YM Snapshot Tracker
    </h2>
""", unsafe_allow_html=True)

st.markdown("---")

# Initialize data
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []

wards = ["Wellington Ward", "Hataitai Ward", "Hutt Valley Ward", "Avalon Branch",
         "Lower Hutt Ward", "Upper Hutt Ward", "Wairarapa Ward"]

# ==================== NEW SNAPSHOT FORM ====================
st.header("New YM Snapshot")

col1, col2 = st.columns(2)
with col1:
    ward = st.selectbox("Ward / Unit", wards)

with col2:
    # Month selector
    months = []
    current = datetime.now()
    for i in range(12):
        d = current.replace(day=1) - pd.DateOffset(months=i)
        months.append(d.strftime("%Y-%m"))
    month = st.selectbox("Month", months, index=0)

st.subheader("1. Youth Leadership Check (1-5)")
st.caption("**1 = entirely planned by adult leaders**, **5 = entirely planned by youth leaders**")
leadership = st.slider("", 1, 5, 3, label_visibility="collapsed")

st.subheader("2. The Four Areas Check")
st.caption("During this month, which of the four focus areas were activities centred around:")
col_a, col_b = st.columns(2)
with col_a:
    spiritual = st.checkbox("Spiritual Growth")
    social = st.checkbox("Social Growth")
with col_b:
    physical = st.checkbox("Physical Growth")
    mental = st.checkbox("Mental Growth")

st.subheader("3. Target Support Needed")
st.caption("What is the #1 thing our Stake Presidency can do to help next month?")
support = st.text_area("", placeholder="e.g. Training for presidency members, more activity ideas...", height=120)

if st.button("Submit YM Snapshot", type="primary", use_container_width=True):
    new_snap = {
        "id": len(st.session_state.snapshots) + 1,
        "ward": ward,
        "month": month,
        "leadership": leadership,
        "spiritual": spiritual,
        "social": social,
        "physical": physical,
        "mental": mental,
        "support": support,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    st.session_state.snapshots.insert(0, new_snap)
    st.success(f"✅ Snapshot saved for **{ward}** ({month})")
    st.rerun()

# ==================== DASHBOARD ====================
st.markdown("---")
st.header("Stake YM Dashboard")

df = pd.DataFrame(st.session_state.snapshots)

if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Snapshots", len(df))
    col2.metric("Average Leadership", f"{df['leadership'].mean():.1f}/5")
    
    latest_month = df['month'].max() if 'month' in df.columns else None
    if latest_month:
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

    st.subheader("Ward Leadership Heatmap")
    if 'ward' in df.columns:
        ward_avg = df.groupby("ward")["leadership"].mean().round(1)
        st.bar_chart(ward_avg)

else:
    st.info("No snapshots submitted yet.")

# ==================== ALL SNAPSHOTS ====================
st.markdown("---")
st.header("All YM Snapshots")

if not df.empty:
    display_df = df.sort_values("date", ascending=False)
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No snapshots yet.")