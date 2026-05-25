import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="YM Snapshot", layout="wide", page_icon="⛪")
st.title("Wellington & Hutt Stake • YM Snapshot Tracker")

# ==================== GOOGLE SHEETS SETUP ====================
if 'gsheet' not in st.session_state:
    st.session_state.gsheet = None

# Try to connect to Google Sheets
try:
    import gspread
    from google.oauth2.service_account import Credentials
    
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(
        creds_dict, 
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open("YM_Snapshots")          # Make sure sheet name matches
    worksheet = sh.sheet1
    st.session_state.gsheet = worksheet
    st.success("✅ Connected to Google Sheets")
except Exception as e:
    st.warning("⚠️ Google Sheets is not connected yet.")
    st.info("""
    **How to connect Google Sheets:**
    1. Create a Google Sheet named **YM_Snapshots**
    2. Go to Streamlit → Manage App → Secrets
    3. Add your service account credentials under `gcp_service_account`
    """)

# Load data
def load_data():
    if st.session_state.gsheet:
        try:
            data = st.session_state.gsheet.get_all_records()
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

wards = ["Wellington Ward", "Hataitai Ward", "Hutt Valley Ward", "Avalon Branch",
         "Lower Hutt Ward", "Upper Hutt Ward", "Wairarapa Ward"]

# ==================== SIDEBAR - NEW SNAPSHOT ====================
with st.sidebar:
    st.header("Submit New Snapshot")
    
    ward = st.selectbox("Ward / Unit", wards)
    
    # Month selector
    current_month = datetime.now().strftime("%Y-%m")
    months = []
    for i in range(12):
        d = datetime.now().replace(day=1) - pd.DateOffset(months=i)
        months.append(d.strftime("%Y-%m"))
    month = st.selectbox("Month", months, index=0)

    leadership = st.slider("1. Youth Leadership Check (1-5)", 1, 5, 3)

    st.write("**2. The Four Areas Check**")
    spiritual = st.checkbox("Spiritual Growth")
    social = st.checkbox("Social Growth")
    physical = st.checkbox("Physical Growth")
    mental = st.checkbox("Mental Growth")

    support = st.text_area("3. Target Support Needed", 
                          placeholder="What is the #1 thing the Stake Presidency can help with?")

    if st.button("Submit Snapshot", type="primary"):
        if st.session_state.gsheet is None:
            st.error("Google Sheets not connected. Please set up secrets first.")
        else:
            new_row = [
                ward, month, leadership, spiritual, social, physical, mental, 
                support, datetime.now().strftime("%Y-%m-%d %H:%M")
            ]
            st.session_state.gsheet.append_row(new_row)
            st.success(f"✅ Snapshot saved for **{ward}** ({month})")
            st.rerun()

# ==================== MAIN DASHBOARD ====================
if not df.empty:
    st.subheader("📊 Stake Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Snapshots", len(df))
    col2.metric("Average Leadership", f"{df['leadership'].mean():.1f}/5" if 'leadership' in df.columns else "—")
    
    if 'month' in df.columns:
        latest_month = df['month'].max()
        monthly_avg = df[df['month'] == latest_month]['leadership'].mean()
        col3.metric("Monthly Progress", f"{monthly_avg:.1f}/5", latest_month)

    # Charts
    if 'leadership' in df.columns:
        st.subheader("Leadership Distribution")
        st.bar_chart(df['leadership'].value_counts().sort_index())

    st.subheader("Four Areas Coverage")
    area_data = {}
    for col in ['spiritual', 'social', 'physical', 'mental']:
        if col in df.columns:
            area_data[col.capitalize()] = df[col].sum()
    if area_data:
        st.bar_chart(area_data)

    st.subheader("Ward Performance")
    if 'ward' in df.columns and 'leadership' in df.columns:
        ward_avg = df.groupby("ward")["leadership"].mean().round(1)
        st.bar_chart(ward_avg)

    st.subheader("All Snapshots")
    st.dataframe(df.sort_values("date", ascending=False) if 'date' in df.columns else df, use_container_width=True)

else:
    st.info("No snapshots yet. Use the sidebar to submit the first one.")

st.caption("Data is stored in Google Sheets • Shared with all stake leaders")