import streamlit as st
import pandas as pd

# 1. Page Configuration & Custom CSS (ऐप जैसा लुक देने के लिए)
st.set_page_config(page_title="Live Committee", page_icon="💸", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
    div[data-testid="metric-container"] {
        background-color: #f7f9fb;
        border: 1px solid #e6e6e9;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# 2. Database & State Management (पूरा काम करने वाला सिस्टम)
if 'users_db' not in st.session_state:
    # डिफ़ॉल्ट यूज़र्स (आप इन्हें बाद में अपने हिसाब से बदल सकते हैं)
    st.session_state['users_db'] = {
        "9876543210": {"name": "Admin", "role": "admin"},
        "9999999999": {"name": "Ravinder Kumar", "role": "user"},
        "8888888888": {"name": "Gopal Dhiman", "role": "user"}
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['current_user_name'] = ""
    st.session_state['current_role'] = ""
    st.session_state['current_mobile'] = ""

# ----------------- LOGIN PAGE -----------------
def login_page():
    st.title("🔐 Live Committee Login")
    st.write("अपना रजिस्टर्ड मोबाइल नंबर दर्ज करें:")
    
    mobile = st.text_input("📱 मोबाइल नंबर (10 अंक):", max_chars=10)
    
    if st.button("लॉग इन 🚀"):
        if mobile in st.session_state['users_db']:
            user_data = st.session_state['users_db'][mobile]
            st.session_state['logged_in'] = True
            st.session_state['current_user_name'] = user_data['name']
            st.session_state['current_role'] = user_data['role']
            st.session_state['current_mobile'] = mobile
            st.rerun()
        else:
            if len(mobile) == 10:
                st.error("❌ यह नंबर रजिस्टर्ड नहीं है। कृपया एडमिन से संपर्क करें।")
            else:
                st.warning("⚠️ कृपया 10 अंकों का सही मोबाइल नंबर डालें।")

# ----------------- ADMIN PANEL -----------------
def admin_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Admin Panel")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.markdown("### ➕ नए मेम्बर को जोड़ें (Invite)")
    with st.form("add_user_form", clear_on_submit=True):
        new_name = st.text_input("मेम्बर का नाम:")
        new_mobile = st.text_input("मोबाइल नंबर (10 अंक):", max_chars=10)
        
        if st.form_submit_button("✅ मेम्बर ऐड करें"):
            if len(new_mobile) == 10 and new_name:
                st.session_state['users_db'][new_mobile] = {"name": new_name, "role": "user"}
                st.success(f"🎉 {new_name} ({new_mobile}) को सफलता से जोड़ दिया गया है! अब वे लॉगिन कर सकते हैं।")
            else:
                st.error("कृपया सही नाम और 10 अंकों का नंबर डालें।")
                
    st.markdown("---")
    st.subheader("👥 सभी रजिस्टर्ड मेम्बर्स")
    for mob, data in st.session_state['users_db'].items():
        if data['role'] != 'admin':
            st.write(f"- **{data['name']}** (📱 {mob})")

# ----------------- USER DASHBOARD (अट्रैक्टिव डिज़ाइन) -----------------
def dashboard_page():
    name = st.session_state['current_user_name']
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💸 Live Committee")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.markdown(f"### 👋 नमस्ते, {name}!")
    st.write("आपकी कमेटी का ताज़ा अपडेट यहाँ है:")
    st.markdown("---")

    # 3 Color Box Layout
    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 कुल जमा", "₹ 44,000")
    c2.metric("🔴 बकाया", "₹ 3,192")
    c3.metric("🏆 विजेता", "Gopal")

    st.markdown("<br>", unsafe_allow_html=True)

    # Attractive Alert Logic
    if name == "Ravinder Kumar":
        st.warning("⏳ **ध्यान दें:** आपकी इस महीने की किश्त (₹ 3,192) पेंडिंग है। कृपया समय पर जमा करें।")
    else:
        st.success("🎉 शानदार! आपकी इस महीने की किश्त जमा हो चुकी है।")

    st.info("⏳ **अगली कमेटी:** अगली बोली खुलने में **8 दिन** बाकी हैं! तैयार रहें।")
    st.markdown("---")

    # Transaction History (Expanders)
    st.subheader("📜 आपकी ट्रांज़ैक्शन हिस्ट्री")
    with st.expander("✅ October 2026 - सफलतापूर्वक जमा"):
        st.write("**तारीख:** 15 Oct 2026 | **रकम:** ₹ 3,192 | **स्टेटस:** 🟢 Paid")
    with st.expander("⏳ November 2026 - पेंडिंग"):
        st.write("**तारीख:** 15 Nov 2026 | **रकम:** ₹ 3,192 | **स्टेटस:** 🔴 Pending")
        
    st.markdown("---")
    
    # Engagement Section
    st.subheader("🌟 Star Members (इस महीने)")
    st.caption("इन सदस्यों ने सबसे पहले किश्त जमा की है:")
    st.markdown("🥇 ✅ **Gopal Dhiman**")
    st.markdown("🥈 ✅ **Ankit Kumar**")
    st.markdown("🥉 ✅ **Sachin**")

# ----------------- MAIN APP ROUTING -----------------
if not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['current_role'] == 'admin':
        admin_page()
    else:
        dashboard_page()
