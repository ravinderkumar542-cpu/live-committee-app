import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. Page Configuration & Custom CSS
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
    .timer-text {
        font-size: 24px;
        font-weight: bold;
        color: #d9534f;
        text-align: center;
        padding: 10px;
        background-color: #ffeaea;
        border-radius: 8px;
    }
    .bidding-open {
        font-size: 24px;
        font-weight: bold;
        color: #28a745;
        text-align: center;
        padding: 10px;
        background-color: #e6ffed;
        border-radius: 8px;
        animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker {
        50% { opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# 2. Database & State Management
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "9876543210": {"name": "Admin", "role": "admin"},
        "9999999999": {"name": "Ravinder Kumar", "role": "user"},
        "8888888888": {"name": "Gopal Dhiman", "role": "user"}
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['current_user_name'] = ""
    st.session_state['current_role'] = ""

# ----------------- TIMING & PRE-START LOGIC -----------------
# मान लीजिए हर महीने की 20 तारीख को कमेटी खुलती है और 3 दिन पहले (17 तारीख को) प्री-स्टार्ट होता है।
TARGET_DAY = 20
PRE_START_DAYS = 3

def get_committee_status():
    now = datetime.now()
    # इस महीने की टारगेट डेट निकालें
    target_date = now.replace(day=TARGET_DAY, hour=18, minute=0, second=0, microsecond=0) # शाम 6 बजे
    
    # अगर आज की तारीख 20 से ऊपर है, तो अगले महीने का टारगेट सेट करें
    if now > target_date:
        if now.month == 12:
            target_date = target_date.replace(year=now.year + 1, month=1)
        else:
            target_date = target_date.replace(month=now.month + 1)

    pre_start_date = target_date - timedelta(days=PRE_START_DAYS)
    
    if pre_start_date <= now <= target_date:
        return "OPEN", target_date
    elif now > target_date:
        return "CLOSED", target_date
    else:
        return "WAITING", pre_start_date

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
            st.rerun()
        else:
            st.error("❌ यह नंबर रजिस्टर्ड नहीं है या गलत है।")

# ----------------- ADMIN PANEL -----------------
def admin_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Admin Panel")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.markdown("### ➕ नए मेम्बर को जोड़ें")
    with st.form("add_user_form", clear_on_submit=True):
        new_name = st.text_input("मेम्बर का नाम:")
        new_mobile = st.text_input("मोबाइल नंबर (10 अंक):", max_chars=10)
        
        if st.form_submit_button("✅ मेम्बर ऐड करें"):
            if len(new_mobile) == 10 and new_name:
                st.session_state['users_db'][new_mobile] = {"name": new_name, "role": "user"}
                st.success(f"🎉 {new_name} को सफलता से जोड़ दिया गया है!")
            else:
                st.error("कृपया सही डिटेल्स डालें।")

# ----------------- USER DASHBOARD -----------------
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
    st.markdown("---")

    # 1. LIVE TIMER & AUTO PRE-START SECTION
    status, next_date = get_committee_status()
    now = datetime.now()
    
    if status == "OPEN":
        # ऑटोमैटिक प्री-स्टार्ट / ओपन स्टेट
        st.markdown('<div class="bidding-open">🟢 Bidding is OPEN! (प्री-स्टार्ट शुरू)</div>', unsafe_allow_html=True)
        st.info("आप अभी अपनी बोली (Bidding) लगा सकते हैं।")
        st.button("अपनी बोली लगाएँ 💰", use_container_width=True)
    
    elif status == "WAITING":
        # लाइव टाइमर (जावास्क्रिप्ट का उपयोग करके बिना पेज रिफ्रेश किये लाइव उलटी गिनती)
        time_diff = next_date - now
        days, seconds = time_diff.days, time_diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        st.markdown(f"**अगली बोली (Pre-Start) शुरू होने में बचा समय:**")
        
        # HTML/JS लाइव टाइमर ताकि बिना रिफ्रेश के चले
        timer_html = f"""
        <div class="timer-text" id="live-timer">
            ⏳ {days} दिन {hours} घंटे {minutes} मिनट
        </div>
        <script>
            var countDownDate = new Date("{next_date.strftime('%b %d, %Y %H:%M:%S')}").getTime();
            var x = setInterval(function() {{
                var now = new Date().getTime();
                var distance = countDownDate - now;
                var d = Math.floor(distance / (1000 * 60 * 60 * 24));
                var h = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var m = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var s = Math.floor((distance % (1000 * 60)) / 1000);
                document.getElementById("live-timer").innerHTML = "⏳ " + d + " दिन " + h + " घंटे " + m + " मिनट " + s + " सेकंड";
                if (distance < 0) {{
                    clearInterval(x);
                    document.getElementById("live-timer").innerHTML = "🟢 Bidding Starting... Refresh page!";
                }}
            }}, 1000);
        </script>
        """
        st.components.v1.html(timer_html, height=70)

    st.markdown("---")

    # 2. Metrics Design
    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 कुल जमा", "₹ 44,000")
    c2.metric("🔴 बकाया", "₹ 3,192")
    c3.metric("🏆 विजेता", "Gopal")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Transaction History
    st.subheader("📜 आपकी ट्रांज़ैक्शन हिस्ट्री")
    with st.expander("✅ October 2026 - सफलतापूर्वक जमा"):
        st.write("**तारीख:** 15 Oct 2026 | **रकम:** ₹ 3,192 | **स्टेटस:** 🟢 Paid")
    with st.expander("⏳ November 2026 - पेंडिंग"):
        st.write("**तारीख:** 15 Nov 2026 | **रकम:** ₹ 3,192 | **स्टेटस:** 🔴 Pending")
        
    st.markdown("---")
    
    # 4. Star Members
    st.subheader("🌟 Star Members")
    st.markdown("🥇 ✅ **Gopal Dhiman**")
    st.markdown("🥈 ✅ **Ankit Kumar**")

# ----------------- MAIN APP ROUTING -----------------
if not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['current_role'] == 'admin':
        admin_page()
    else:
        dashboard_page()
