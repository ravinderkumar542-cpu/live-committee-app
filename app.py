import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. PAGE CONFIGURATION (सबसे ऊपर होना ज़रूरी है) ---
st.set_page_config(page_title="Live Committee", page_icon="💸", layout="centered")

# --- 2. CUSTOM NATIVE APP CSS (वेबसाइट वाले लुक को हटाने के लिए) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    
    /* Metric Box Styling (बॉक्सेस को सुंदर बनाने के लिए) */
    div[data-testid="metric-container"] {
        background-color: #f7f9fb;
        border: 1px solid #e6e6e9;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* Timer & Alerts Styling */
    .timer-text {
        font-size: 20px;
        font-weight: bold;
        color: #d9534f;
        text-align: center;
        padding: 12px;
        background-color: #ffeaea;
        border-radius: 10px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
    }
    .bidding-open {
        font-size: 22px;
        font-weight: bold;
        color: #155724;
        text-align: center;
        padding: 12px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker {
        50% { opacity: 0.4; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE & SESSION STATE (सिक्योर लॉगिन के लिए) ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "9876543210": {"name": "Admin (Sanchalak)", "role": "admin"},
        "9999999999": {"name": "Ravinder Kumar", "role": "user"},
        "8888888888": {"name": "Gopal Dhiman", "role": "user"}
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['current_user_name'] = ""
    st.session_state['current_role'] = ""
    st.session_state['current_mobile'] = ""

# --- 4. CORE LOGIC: TIMER & BIDDING STATUS ---
TARGET_DAY = 20  # हर महीने की 20 तारीख को कमेटी होती है
PRE_START_DAYS = 3  # 3 दिन पहले (17 तारीख से) बोली शुरू हो जाएगी

def get_committee_status():
    now = datetime.now()
    target_date = now.replace(day=TARGET_DAY, hour=18, minute=0, second=0, microsecond=0)
    
    # अगर तारीख निकल चुकी है, तो अगले महीने का टारगेट सेट करें
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

# --- 5. LOGIN PAGE ---
def login_page():
    st.title("🔐 Live Committee")
    st.markdown("### सुरक्षित लॉगिन")
    st.write("कृपया अपना रजिस्टर्ड मोबाइल नंबर दर्ज करें:")
    
    # Form इस्तेमाल किया है ताकि एंटर दबाने पर भी काम करे
    with st.form("login_form"):
        mobile = st.text_input("📱 मोबाइल नंबर (10 अंक):", max_chars=10)
        submit_login = st.form_submit_button("लॉग इन करें 🚀", use_container_width=True)
        
        if submit_login:
            if mobile in st.session_state['users_db']:
                user_data = st.session_state['users_db'][mobile]
                st.session_state['logged_in'] = True
                st.session_state['current_user_name'] = user_data['name']
                st.session_state['current_role'] = user_data['role']
                st.session_state['current_mobile'] = mobile
                st.rerun()
            else:
                st.error("❌ यह नंबर रजिस्टर्ड नहीं है। कृपया एडमिन से संपर्क करें।")

# --- 6. ADMIN PANEL ---
def admin_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Admin Panel")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.success(f"वेलकम, {st.session_state['current_user_name']}!")
    
    st.markdown("### ➕ नए मेम्बर को जोड़ें")
    with st.form("add_user_form", clear_on_submit=True):
        new_name = st.text_input("मेम्बर का नाम:")
        new_mobile = st.text_input("मोबाइल नंबर (10 अंक):", max_chars=10)
        submit_add = st.form_submit_button("✅ मेम्बर ऐड करें", use_container_width=True)
        
        if submit_add:
            if len(new_mobile) == 10 and new_name:
                st.session_state['users_db'][new_mobile] = {"name": new_name, "role": "user"}
                st.success(f"🎉 {new_name} को सफलता से जोड़ दिया गया है!")
            else:
                st.error("⚠️ कृपया सही नाम और 10 अंकों का मोबाइल नंबर डालें।")
                
    st.markdown("---")
    st.subheader("👥 रजिस्टर्ड मेम्बर्स की सूची")
    for mob, data in st.session_state['users_db'].items():
        if data['role'] != 'admin':
            st.info(f"👤 **{data['name']}** (📱 {mob})")

# --- 7. USER DASHBOARD (MASTER UI) ---
def dashboard_page():
    name = st.session_state['current_user_name']
    
    # Header & Logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💸 Live Committee")
    with col2:
        if st.button("Logout 🚪"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.markdown(f"### 👋 नमस्ते, {name}!")
    st.markdown("---")

    # TIMER & BIDDING LOGIC
    status, next_date = get_committee_status()
    now = datetime.now()
    
    if status == "OPEN":
        st.markdown('<div class="bidding-open">🟢 Bidding is OPEN! (प्री-स्टार्ट शुरू)</div>', unsafe_allow_html=True)
        st.write("")
        
        # Secure Bidding Form (अब ब्लैंक स्क्रीन नहीं आएगी)
        with st.form("bidding_form", clear_on_submit=True):
            st.write("#### 💰 अपनी बोली (Bid) दर्ज करें")
            bid_amount = st.number_input("बोली की रकम (₹):", min_value=0, step=100)
            submit_bid = st.form_submit_button("बोली कन्फर्म करें ✅", use_container_width=True)
            
            if submit_bid:
                if bid_amount > 0:
                    st.success(f"🎉 शानदार! आपकी ₹ {bid_amount:,.0f} की बोली सफलतापूर्वक दर्ज हो गई है।")
                    st.balloons() # सेलिब्रेशन इफ़ेक्ट
                else:
                    st.error("⚠️ कृपया 0 से बड़ी रकम डालें!")
                    
    elif status == "WAITING":
        time_diff = next_date - now
        days, seconds = time_diff.days, time_diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        st.markdown(f"**⏳ अगली बोली शुरू होने में बचा समय:**")
        
        # Live Javascript Timer (बिना रिफ्रेश के चलेगा)
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
                    document.getElementById("live-timer").innerHTML = "🟢 Bidding Starting... Please Refresh Page!";
                }}
            }}, 1000);
        </script>
        """
        st.components.v1.html(timer_html, height=70)

    st.markdown("---")

    # METRICS UI
    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 कुल जमा", "₹ 44,000")
    c2.metric("🔴 बकाया", "₹ 3,192")
    c3.metric("🏆 विजेता", "Gopal")

    st.markdown("<br>", unsafe_allow_html=True)

    # SMART ALERTS
    if name == "Ravinder Kumar":
        st.warning("⚠️ **ध्यान दें:** आपकी इस महीने की किश्त (₹ 3,192) पेंडिंग है। कृपया समय पर जमा करें।")
    else:
        st.success("✅ शानदार! आपकी इस महीने की किश्त जमा हो चुकी है।")

    st.markdown("---")

    # TRANSACTION HISTORY
    st.subheader("📜 आपकी ट्रांज़ैक्शन हिस्ट्री")
    with st.expander("✅ October 2026 - सफलतापूर्वक जमा"):
        st.markdown("**तारीख:** 15 Oct 2026<br>**रकम:** ₹ 3,192<br>**स्टेटस:** 🟢 Paid", unsafe_allow_html=True)
    with st.expander("⏳ November 2026 - पेंडिंग"):
        st.markdown("**तारीख:** 15 Nov 2026<br>**रकम:** ₹ 3,192<br>**स्टेटस:** 🔴 Pending", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # STAR MEMBERS
    st.subheader("🌟 Star Members (Top)")
    st.caption("इन सदस्यों ने सबसे पहले किश्त जमा की है:")
    st.markdown("🥇 ✅ **Gopal Dhiman**")
    st.markdown("🥈 ✅ **Ankit Kumar**")
    st.markdown("🥉 ✅ **Sachin**")

# --- 8. MAIN APP ROUTER ---
if not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['current_role'] == 'admin':
        admin_page()
    else:
        dashboard_page()
