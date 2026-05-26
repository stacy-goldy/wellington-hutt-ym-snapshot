import streamlit as st
import pandas as pd
from datetime import datetime
import json

st.set_page_config(page_title="YM Snapshot", layout="wide", page_icon="⛪")

# Custom CSS to match the HTML design
st.markdown("""
<style>
    .main-header {
        background-color: #002f6c;
        color: white;
        padding: 2rem 0;
        text-align: center;
        border-radius: 0 0 20px 20px;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #002f6c;
        color: white;
        border-radius: 1rem;
        height: 3.5rem;
        font-size: 1.1rem;
    }
    .nav-button {
        background: none;
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-size: 0.95rem;
    }
    .nav-active {
        border-bottom: 3px solid #f8b400;
        font-weight: bold;
    }
    .snapshot-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 1rem;
    }
    .heatmap-box {
        padding: 1.25rem;
        border-radius: 1rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .heatmap-box:hover {
        transform: scale(1.03);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0

wards = ["Wellington Ward", "Hataitai Ward", "Hutt Valley Ward", "Avalon Branch",
         "Lower Hutt Ward", "Upper Hutt Ward", "Wairarapa Ward"]

# Header
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:2.5rem;">Wellington & Hutt Stake</h1>
    <p style="margin:0; font-size:1.4rem; color:#f8b400;">YM Snapshot Tracker</p>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("📋 NEW SNAPSHOT", use_container_width=True, type="primary" if st.session_state.current_tab == 0 else "secondary"):
        st.session_state.current_tab = 0
        st.rerun()
with col2:
    if st.button("📊 DASHBOARD", use_container_width=True, type="primary" if st.session_state.current_tab == 1 else "secondary"):
        st.session_state.current_tab = 1
        st.rerun()
with col3:
    if st.button("📋 ALL SNAPSHOTS", use_container_width=True, type="primary" if st.session_state.current_tab == 2 else "secondary"):
        st.session_state.current_tab = 2
        st.rerun()

# ====================== TAB 0: NEW SNAPSHOT ======================
if st.session_state.current_tab == 0:
    st.markdown("### Ward YM Snapshot")
    st.caption("One snapshot per unit per month")

    with st.form("snapshot_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            ward = st.selectbox("Ward / Unit", wards, key="ward_input")
        with col_b:
            # Month options
            now = datetime.now()
            months = []
            for i in range(12):
                d = now.replace(day=1) - pd.DateOffset(months=i)
                val = d.strftime("%Y-%m")
                text = d.strftime("%B %Y")
                months.append((val, text))
            
            month_options = [m[1] for m in months]
            month_values = [m[0] for m in months]
            selected_month_idx = st.selectbox("Month", range(len(month_options)), 
                                            format_func=lambda x: month_options[x], index=0)
            selected_month = month_values[selected_month_idx]

        st.markdown("**1. Youth Leadership Check (1-5)**")
        st.caption("How involved were quorum members in activity planning?: 1 = entirely planned by adult leaders, 5 = entirely planned by youth leaders")
        
        leadership_score = st.slider("", 1, 5, 3, key="leadership_slider", label_visibility="collapsed")
        
        st.markdown("**2. The Four Areas Check**")
        st.caption("During this month, which of the four focus areas were activities centred around?")
        
        col_c, col_d = st.columns(2)
        with col_c:
            spiritual = st.checkbox("Spiritual Growth", key="spiritual_check")
            social = st.checkbox("Social Growth", key="social_check")
        with col_d:
            physical = st.checkbox("Physical Growth", key="physical_check")
            mental = st.checkbox("Mental Growth", key="mental_check")

        support = st.text_area("3. Target Support Needed", 
                              placeholder="What is the #1 thing Stake leaders can do to help next month?",
                              key="support_input")

        submitted = st.form_submit_button("Submit YM Snapshot", type="primary")

        if submitted:
            # Check for duplicate
            existing = any(s['ward'] == ward and s['month'] == selected_month for s in st.session_state.snapshots)
            if existing:
                st.error(f"A snapshot already exists for {ward} in {selected_month}.")
            else:
                new_snap = {
                    "id": int(datetime.now().timestamp() * 1000),
                    "ward": ward,
                    "month": selected_month,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "leadership": leadership_score,
                    "areas": {
                        "spiritual": spiritual,
                        "social": social,
                        "physical": physical,
                        "mental": mental
                    },
                    "support": support.strip()
                }
                st.session_state.snapshots.insert(0, new_snap)
                st.success(f"✅ Snapshot saved for **{ward}** ({selected_month})")
                st.rerun()

# ====================== TAB 1: DASHBOARD ======================
elif st.session_state.current_tab == 1:
    snapshots = st.session_state.snapshots
    total = len(snapshots)
    
    st.markdown("### Stake YM Dashboard")
    
    # Summary Cards
    col1, col2, col3 = st.columns(3)
    
    avg_leadership = round(sum(s['leadership'] for s in snapshots) / total, 1) if total > 0 else 0
    
    # Latest month average
    latest_month = snapshots[0]['month'] if snapshots else None
    monthly_avg = 0
    if latest_month:
        month_snaps = [s for s in snapshots if s['month'] == latest_month]
        monthly_avg = round(sum(s['leadership'] for s in month_snaps) / len(month_snaps), 1) if month_snaps else 0

    with col1:
        st.metric("Total Snapshots", total)
    with col2:
        st.metric("Overall Average", f"{avg_leadership}/5")
    with col3:
        st.metric("Monthly Progress", f"{monthly_avg}/5", latest_month or "—")

    # Charts
    if total > 0:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Leadership Distribution")
            leadership_counts = pd.Series([s['leadership'] for s in snapshots]).value_counts().sort_index()
            st.bar_chart(leadership_counts)
        
        with col_chart2:
            st.subheader("Four Areas Coverage")
            area_counts = {
                "Spiritual": sum(1 for s in snapshots if s['areas']['spiritual']),
                "Social": sum(1 for s in snapshots if s['areas']['social']),
                "Physical": sum(1 for s in snapshots if s['areas']['physical']),
                "Mental": sum(1 for s in snapshots if s['areas']['mental'])
            }
            area_df = pd.DataFrame.from_dict(area_counts, orient='index', columns=['Count'])
            st.bar_chart(area_df)
        
        # Heatmap
        st.subheader("Ward Leadership Heatmap")
        heatmap_cols = st.columns(4)
        
        for i, ward in enumerate(wards):
            ward_snaps = [s for s in snapshots if s['ward'] == ward]
            avg = round(sum(s['leadership'] for s in ward_snaps) / len(ward_snaps), 1) if ward_snaps else None
            
            color_intensity = int((avg - 1) * 25) if avg else 10
            bg_color = f"hsl({color_intensity}, 85%, 55%)" if avg else "#e5e7eb"
            text_color = "white" if avg and avg > 3 else "black"
            
            with heatmap_cols[i % 4]:
                st.markdown(f"""
                <div class="heatmap-box" style="background-color: {bg_color}; color: {text_color};">
                    <div style="font-weight:600; font-size:0.95rem;">{ward}</div>
                    <div style="font-size:2.2rem; font-weight:bold;">{avg if avg else '—'}</div>
                </div>
                """, unsafe_allow_html=True)

# ====================== TAB 2: ALL SNAPSHOTS ======================
elif st.session_state.current_tab == 2:
    st.markdown("### All YM Snapshots")
    snapshots = st.session_state.snapshots.copy()
    
    if not snapshots:
        st.info("No snapshots yet. Submit one using the **NEW SNAPSHOT** tab.")
    else:
        # Sort by date descending
        snapshots.sort(key=lambda x: x['date'], reverse=True)
        
        for snap in snapshots:
            areas_list = [k.capitalize() for k, v in snap['areas'].items() if v]
            areas_str = " • ".join(areas_list) if areas_list else "None"
            
            with st.container():
                st.markdown(f"""
                <div class="snapshot-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:1.3rem; font-weight:700;">{snap['ward']}</span>
                            <span style="margin-left:1rem; color:#666;">{snap['month']}</span>
                        </div>
                        <button onclick="deleteSnapshot({snap['id']})" 
                                style="background:#fee2e2; color:#b91c1c; border:none; padding:0.4rem 1rem; border-radius:9999px; cursor:pointer;">
                            Delete
                        </button>
                    </div>
                    <div style="margin-top:1rem; font-size:1.1rem;">
                        Leadership: <span style="color:#002f6c; font-weight:700;">{snap['leadership']}/5</span>
                    </div>
                    <div style="margin-top:0.5rem; font-size:0.95rem;">
                        <strong>Areas:</strong> {areas_str}
                    </div>
                """, unsafe_allow_html=True)
                
                if snap['support']:
                    st.markdown(f"""
                        <div style="margin-top:1rem; padding:1rem; background:#fef3c7; border-radius:1rem; font-size:0.95rem;">
                            <strong>Support Needed:</strong><br>{snap['support']}
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.caption("All data is stored locally in your browser • Private to this device")