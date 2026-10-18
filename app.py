import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Live Committee", page_icon="💸", layout="centered")

# --- 2. CUSTOM NATIVE APP CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    
    div[data-testid="metric-container"] {
        background-color: #f7f9fb;
        border: 1px solid #e6e6e9;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    .bidding-open {
        font-size: 20px;
        font-weight: bold;
        color: #155724;
        text-align: center;
        padding: 12px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        animation: blinker 1.5s linear infinite;
        margin-bottom: 15px;
    }
    @keyframes blinker {
        50% { opacity: 0.5; }
    }
    .winner-box {
        font-size: 20px;
        font-weight: bold;
        color: #856404;
        text-align: center;
        padding: 15px;
        background-color: #fff3cd;
        border: 2px solid #ffeeba;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .txn-text {
        font-size: 12px;
        color: #6c757d;
        margin-left: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE & SESSION STATE ---
# डेटाबेस में अब 'txn_id' (ट्रांज़ैक्शन डिटेल) भी जोड़ दी गई है
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "9876543210": {"name": "Admin (संचालक)", "role": "admin", "payment_status": "Paid", "txn_id": "CASH"},
        "9999999999": {"name": "Ravinder Kumar", "role": "user", "payment_status": "Pending", "txn_id": ""},
        "8888888888": {"name": "Gopal Dhiman", "role": "user", "payment_status": "Paid", "txn_id": "UPI9876543210"},
        "7777777777": {"name": "Ankit Kumar", "role": "user", "payment_status": "Pending", "txn_id": ""},
        "6666666666": {"name": "Sachin", "role": "user", "payment_status": "Pending", "txn_id": ""}
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
if 'winner_name' not in st.session_state:
    st.session_state['winner_name'] = "Gopal (पिछला)"

# कमेटी की सेटिंग
TOTAL_POOL = 50000       
TOTAL_MEMBERS = 10       
BASE_BID = 500           
BID_INCREMENT = 500      

# --- 4. LOGIN PAGE ---
def login_page():
    st.title("🔐 Live Committee")
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
                st.error("❌ यह नंबर रजिस्टर्ड नहीं है।")

# --- 5. ADMIN PANEL ---
def admin_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Admin Panel")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.success(f"वेलकम, {st.session_state['current_user_name']}!")
    
    st.markdown("### 📊 पेमेंट और ट्रांज़ैक्शन रिपोर्ट")
    st.write("यहाँ एडमिन सभी मेम्बर्स का पेमेंट स्टेटस और उनकी ट्रांज़ैक्शन डिटेल्स देख सकते हैं:")
    
    # एडमिन के लिए पेमेंट ट्रैकिंग टेबल
    for mob, data in st.session_state['users_db'].items():
        if data['role'] == 'user':
            if data['payment_status'] == 'Paid':
                st.success(f"✅ **{data['name']}** | नंबर: {mob} \n\n 📝 **Txn Detail:** {data['txn_id']}")
            else:
                st.error(f"⏳ **{data['name']}** | नंबर: {mob} \n\n 📝 **Txn Detail:** अभी पेमेंट नहीं किया")
                
    st.markdown("---")
    if st.button("🔙 डैशबोर्ड पर जाएं (Member View)"):
        st.session_state['current_role'] = 'user'
        st.rerun()

# --- 6. USER DASHBOARD (MASTER UI) ---
def dashboard_page():
    name = st.session_state['current_user_name']
    mobile = st.session_state['current_mobile']
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💸 Live Committee")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.markdown(f"### 👋 नमस्ते, {name}!")
    st.markdown("---")

    # ------------------ LIVE BIDDING ROOM ------------------
    st.markdown('<div class="bidding-open">🟢 Live Bidding Room OPEN</div>', unsafe_allow_html=True)
    
    st.write("💬 **बोली का लाइव रिकॉर्ड:**")
    chat_container = st.container(height=200)
    with chat_container:
        if len(st.session_state['bid_history']) == 0:
            st.info("अभी तक किसी ने बोली नहीं लगाई है। सबसे पहली बोली लगाएँ!")
        else:
            for bid in st.session_state['bid_history']:
                if bid['user'] == name:
                    with st.chat_message("user", avatar="🙋‍♂️"):
                        st.write(f"आपने **₹ {bid['amount']}** की बोली लगाई।")
                else:
                    with st.chat_message("assistant", avatar="👤"):
                        st.write(f"**{bid['user']}** ने **₹ {bid['amount']}** की बोली लगाई।")

    highest_bid = st.session_state['highest_bid']
    next_min_bid = BASE_BID if highest_bid == 0 else highest_bid + BID_INCREMENT
    
    with st.form("bidding_form", clear_on_submit=True):
        st.markdown(f"📈 **अगली न्यूनतम बोली:** ₹ {next_min_bid}")
        new_bid = st.number_input("अपनी बोली चुनें (₹):", min_value=next_min_bid, step=BID_INCREMENT, value=next_min_bid)
        
        if st.form_submit_button("💰 अपनी बोली दर्ज करें", use_container_width=True):
            if new_bid >= next_min_bid:
                st.session_state['highest_bid'] = new_bid
                st.session_state['winner_name'] = name 
                st.session_state['bid_history'].append({"user": name, "amount": new_bid})
                st.success("✅ आपकी बोली सफलता से दर्ज हो गई!")
                st.rerun()
            else:
                st.error(f"⚠️ बोली कम से कम ₹ {next_min_bid} होनी चाहिए!")

    st.markdown("---")

    # ------------------ WINNER & EMI CALCULATION ------------------
    current_winner = st.session_state['winner_name']
    discounted_pool = TOTAL_POOL - highest_bid
    emi_per_person = int(discounted_pool / TOTAL_MEMBERS)

    st.markdown(f'''
    <div class="winner-box">
        🏆 करंट विजेता: <b>{current_winner}</b> (बोली: ₹ {highest_bid})<br>
        💳 इस महीने की EMI: <b>₹ {emi_per_person}</b> / मेम्बर
    </div>
    ''', unsafe_allow_html=True)

    # ------------------ PAYMENT & TRANSACTION SYSTEM ------------------
    st.subheader("💳 आपका पेमेंट स्टेटस")
    
    user_status = st.session_state['users_db'][mobile]['payment_status']
    
    if user_status == "Pending":
        st.warning(f"⏳ आपको इस महीने **₹ {emi_per_person}** जमा करने हैं।")
        
        # पेमेंट कन्फर्मेशन फॉर्म (ट्रांज़ैक्शन डिटेल के साथ)
        with st.form("payment_form"):
            st.write("पैसे भेजने के बाद नीचे अपनी ट्रांज़ैक्शन डिटेल (UPI / UTR) दर्ज करें:")
            txn_detail = st.text_input("📝 ट्रांज़ैक्शन ID / UPI Ref:")
            
            if st.form_submit_button("पैसे जमा करें (Pay Now) 💸", use_container_width=True):
                if txn_detail.strip() == "":
                    st.error("⚠️ कृपया पेमेंट की ट्रांज़ैक्शन ID (UPI Ref) जरूर डालें!")
                else:
                    st.session_state['users_db'][mobile]['payment_status'] = "Paid"
                    st.session_state['users_db'][mobile]['txn_id'] = txn_detail
                    st.success("✅ आपका पेमेंट और ट्रांज़ैक्शन सफलता से दर्ज हो गया है!")
                    st.balloons()
                    st.rerun()
    else:
        st.success(f"✅ शानदार! आपने इस महीने की किश्त जमा कर दी है।")
        st.info(f"📝 **आपकी ट्रांज़ैक्शन ID:** {st.session_state['users_db'][mobile]['txn_id']}")

    st.markdown("---")

    # ------------------ ALL MEMBERS PAYMENT LIST (LIVE) ------------------
    st.subheader("👥 सभी मेम्बर्स का पेमेंट स्टेटस")
    st.write("पारदर्शिता के लिए सभी मेम्बर्स की ट्रांज़ैक्शन डिटेल्स यहाँ देखें:")
    
    for mob, data in st.session_state['users_db'].items():
        if data['role'] == 'user':
            if data['payment_status'] == 'Paid':
                st.markdown(f"✅ **{data['name']}** - जमा हो गए")
                st.markdown(f"<div class='txn-text'>📝 Txn ID: {data['txn_id']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"⏳ **{data['name']}** - <span style='color:red;'>बाकी हैं</span>", unsafe_allow_html=True)

# --- 7. MAIN APP ROUTER ---
if not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['current_role'] == 'admin':
        admin_page()
    else:
        dashboard_page()
