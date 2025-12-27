import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
import base64

# Page config
st.set_page_config(
    page_title="AI Cyber Safety Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = 'victim'
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Language support
LANGUAGES = {
    'en': 'English',
    'hi': 'हिन्दी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'ml': 'മലയാളം',
    'kn': 'ಕನ್ನಡ',
    'mr': 'मराठी',
    'bn': 'বাংলা',
    'gu': 'ગુજરાતી',
    'pa': 'ਪੰਜਾਬੀ',
    'or': 'ଓଡ଼ିଆ',
    'ur': 'اردو'
}

# Sidebar for navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shield.png", width=80)
    st.title("🛡️ AI Cyber Safety")
    
    # Language selector
    selected_lang = st.selectbox(
        "Language / भाषा",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.language)
    )
    st.session_state.language = selected_lang
    
    # Role selector
    role = st.radio(
        "Select Role",
        ["👤 Victim", "👮 Police Officer", "🤖 AI Analyst"],
        index=0 if st.session_state.role == 'victim' else 1
    )
    
    if "Victim" in role:
        st.session_state.role = 'victim'
    elif "Police" in role:
        st.session_state.role = 'police'
    else:
        st.session_state.role = 'analyst'
    
    # Navigation
    st.markdown("---")
    st.markdown("### Navigation")
    
    if st.session_state.role == 'victim':
        page = st.radio(
            "Go to",
            ["🏠 Dashboard", "📝 Report Incident", "🔍 Check Evidence", "📊 My Reports"]
        )
    elif st.session_state.role == 'police':
        page = st.radio(
            "Go to",
            ["👮 Police Dashboard", "📋 FIR Kits", "🚨 High Risk Cases", "📈 Analytics"]
        )
    else:
        page = st.radio(
            "Go to",
            ["📊 AI Analytics", "🤖 Model Performance", "🔗 Blockchain View", "⚙️ Settings"]
        )
    
    # User info
    st.markdown("---")
    if st.session_state.user_id:
        st.success(f"Logged in as User: {st.session_state.user_id[:8]}")
        if st.button("Logout"):
            st.session_state.user_id = None
            st.rerun()
    else:
        st.info("Not logged in")

# Main content based on role and page
if st.session_state.role == 'victim':
    if "Dashboard" in page:
        show_victim_dashboard()
    elif "Report Incident" in page:
        show_report_incident()
    elif "Check Evidence" in page:
        show_evidence_check()
    else:
        show_my_reports()

elif st.session_state.role == 'police':
    if "Police Dashboard" in page:
        show_police_dashboard()
    elif "FIR Kits" in page:
        show_fir_kits()
    elif "High Risk Cases" in page:
        show_high_risk_cases()
    else:
        show_police_analytics()

else:
    if "AI Analytics" in page:
        show_ai_analytics()
    elif "Model Performance" in page:
        show_model_performance()
    elif "Blockchain View" in page:
        show_blockchain_view()
    else:
        show_settings()

def show_victim_dashboard():
    """Victim Dashboard with Report Readiness Score"""
    
    st.title("👤 Victim Dashboard")
    
    # Risk Score Card
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Report Readiness Score",
            value="85%",
            delta="+5% from yesterday"
        )
    
    with col2:
        st.metric(
            label="Risk Level",
            value="MEDIUM",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Evidence Collected",
            value="3 items",
            delta="+1 today"
        )
    
    # Progress bar for readiness
    st.markdown("### 📊 Report Preparation Progress")
    readiness_score = 85  # This would come from backend
    
    progress_html = f"""
    <div style="background-color: #f0f2f6; border-radius: 10px; padding: 5px; margin: 10px 0;">
        <div style="background: linear-gradient(90deg, #4CAF50 {readiness_score}%, #f0f2f6 {readiness_score}%); 
                    border-radius: 10px; height: 30px; text-align: center; line-height: 30px; color: white; font-weight: bold;">
            {readiness_score}% Complete
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # Checklist for readiness
    st.markdown("### ✅ Checklist for Complete Report")
    
    checklist_items = [
        ("Basic Information", True),
        ("Incident Description", True),
        ("Evidence Attached", True),
        ("Risk Assessment", True),
        ("Police Station Selected", False),
        ("Consent Given", True)
    ]
    
    for item, completed in checklist_items:
        emoji = "✅" if completed else "❌"
        color = "green" if completed else "red"
        st.markdown(f'<span style="color:{color}">{emoji} {item}</span>', unsafe_allow_html=True)
    
    # Real-time threat detection
    st.markdown("### 🔍 Real-time Threat Detection")
    
    with st.expander("Scan Your Messages", expanded=True):
        message_input = st.text_area(
            "Paste suspicious messages to analyze:",
            height=100,
            placeholder="Enter chat messages, emails, or any concerning text..."
        )
        
        if st.button("Analyze for Threats", type="primary"):
            if message_input:
                # Call AI analysis API
                analysis_result = analyze_text_ai(message_input)
                
                # Display results
                st.markdown("#### Analysis Results")
                
                # Risk score gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=analysis_result['risk_score'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Risk Score"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "green"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 80
                        }
                    }
                ))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show indicators
                st.markdown("#### 🚨 Key Indicators Found")
                for indicator in analysis_result.get('key_indicators', []):
                    st.warning(f"⚠️ {indicator}")
                
                # Recommendation
                st.markdown("#### 💡 Recommendation")
                rec = analysis_result.get('recommended_action', 'MONITOR_CLOSELY')
                if rec == 'IMMEDIATE_ESCALATION':
                    st.error("🚨 IMMEDIATE ESCALATION REQUIRED - Contact authorities now!")
                elif rec == 'SCHEDULE_POLICE_REVIEW':
                    st.warning("⚠️ Schedule police review - High risk detected")
                else:
                    st.success("✅ Situation appears safe, but monitor closely")
                
                # Save to evidence button
                if st.button("💾 Save as Evidence"):
                    evidence_id = save_evidence(message_input, "chat_log")
                    st.success(f"Evidence saved with ID: {evidence_id}")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚨 Emergency Report", type="primary", use_container_width=True):
            st.switch_page("pages/2_👮_Police_Dashboard.py")
    
    with col2:
        if st.button("📁 Upload Evidence", use_container_width=True):
            uploaded_files = st.file_uploader(
                "Upload screenshots or documents",
                type=['png', 'jpg', 'jpeg', 'pdf', 'txt'],
                accept_multiple_files=True
            )
            if uploaded_files:
                for file in uploaded_files:
                    st.success(f"Uploaded: {file.name}")
    
    with col3:
        if st.button("📞 Helpline Numbers", use_container_width=True):
            st.info("""
            **Emergency Helplines:**
            - Police: 100
            - Women Helpline: 1091
            - Cyber Crime: 1930
            - Child Abuse: 1098
            """)

def show_police_dashboard():
    """Police Dashboard with FIR Kits"""
    
    st.title("👮 Police Dashboard")
    
    # Police station info
    st.markdown("### 🏢 Police Station Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Cases", "24", "+3 today")
    
    with col2:
        st.metric("High Risk", "8", "↑ 25%")
    
    with col3:
        st.metric("FIR Generated", "12", "80% complete")
    
    with col4:
        st.metric("Avg Response Time", "2.4h", "↓ 0.5h")
    
    # High priority cases
    st.markdown("### 🚨 High Priority Cases")
    
    # Mock data - in production would come from API
    high_risk_cases = [
        {"id": "CASE-001", "risk": 95, "type": "Death Threat", "time": "2h ago", "evidence": "Complete"},
        {"id": "CASE-002", "risk": 88, "type": "Cyber Bullying", "time
