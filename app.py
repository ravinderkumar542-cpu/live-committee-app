import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. PAGE CONFIGURATION & CSS ---
st.set_page_config(page_title="Live Committee", page_icon="💸", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
    
    .timer-box {
        font-size: 22px;
        font-weight: bold;
        color: #d9534f;
        text-align: center;
        padding: 15px;
        background-color: #ffeaea;
        border-radius: 10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: 0.3s;
    }
    /* आखिरी 1 मिनट का लाल और चमकता हुआ टाइमर */
    .red-alert {
        color: white !important;
        background-color: #dc3545 !important;
        animation: danger-blink 1s infinite;
    }
    @keyframes danger-blink { 
        50% { opacity: 0.6; background-color: #c82333; } 
    }
    
    .bidding-open {
        font-size: 20px;
        font-weight: bold;
        color: white;
        text-align: center;
        padding: 12px;
        background-color: #28a745;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .winner-box {
        font-size: 22px;
        font-weight: bold;
        color: #856404;
        text-align: center;
        padding: 15px;
        background-color: #fff3cd;
        border: 2px solid #ffeeba;
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & SESSION STATE ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "9876543210": {"name": "Admin (संचालक)", "role": "admin"}
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['current_user_name'] = ""
    st.session_state['current_role'] = ""
    st.session_state['current_mobile'] = ""
    
if 'bid_history' not in st.session_state:
    st.session_state['bid_history'] = [] 
if 'highest_bid' not in st.session_state:
    st.session_state['highest_bid'] = 0   
if 'bidding_end_time' not in st.session_state:
    st.session_state['bidding_end_time'] = None

# --- 3. TIMING & BIDDING LOGIC ---
TARGET_DAY = 25      # हर महीने की 25 तारीख
TARGET_HOUR = 9      # सुबह 9:00 बजे बोली शुरू होगी
BID_DURATION = 15    # 15 मिनट की लाइव बोली चलेगी
BASE_BID = 500       # मिनिमम बोली 500
BID_INCREMENT = 500  # हर बोली 500 के अंतर से लगेगी

def get_committee_status():
    now = datetime.now()
    target_date = now.replace(day=TARGET_DAY, hour=TARGET_HOUR, minute=0, second=0, microsecond=0)
    
    # अगर 25 तारीख निकल चुकी है, तो अगले महीने का सेट करें
    if now.day > TARGET_DAY or (now.day == TARGET_DAY and now.hour > TARGET_HOUR + 1):
        if now.month == 12:
            target_date = target_date.replace(year=now.year + 1, month=1)
        else:
            target_date = target_date.replace(month=now.month + 1)

    # अगर टाइम अभी 25 तारीख सुबह 9:00 बजे से पहले का है
    if now < target_date:
        return "WAITING", target_date
    else:
        # अगर 9 बज गए हैं, तो 15 मिनट का टाइमर स्टार्ट करें (सिर्फ पहली बार)
        if st.session_state['bidding_end_time'] is None:
            st.session_state['bidding_end_time'] = target_date + timedelta(minutes=BID_DURATION)
            
        # चेक करें कि क्या अभी 15 मिनट (या बढ़ा हुआ समय) बाकी है
        if now < st.session_state['bidding_end_time']:
            return "OPEN", st.session_state['bidding_end_time']
        else:
            return "CLOSED", st.session_state['bidding_end_time']

# --- 4. LOGIN PAGE ---
def login_page():
    st.title("🔐 Committee Login")
    st.write("कृपया अपना रजिस्टर्ड मोबाइल नंबर दर्ज करें:")
    
    with st.form("login_form"):
        mobile = st.text_input("📱 मोबाइल नंबर (10 अंक):", max_chars=10)
        submit_login = st.form_submit_button("लॉग इन करें 🚀", use_container_width=True)
        
        if submit_login:
            if mobile in st.session_state['users_db']:
                st.session_state['logged_in'] = True
                st.session_state['current_user_name'] = st.session_state['users_db'][mobile]['name']
                st.session_state['current_role'] = st.session_state['users_db'][mobile]['role']
                st.session_state['current_mobile'] = mobile
                st.rerun()
            else:
                st.error("❌ यह नंबर रजिस्टर्ड नहीं है। कृपया एडमिन से संपर्क करें।")

# --- 5. ADMIN PANEL ---
def admin_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Admin Panel")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
