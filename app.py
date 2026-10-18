import streamlit as st
import streamlit.components.v1 as components
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

# --- 3. TIMING LOGIC ---
TARGET_DAY = 25      
TARGET_HOUR = 9      
BID_DURATION = 15    
BASE_BID = 500       
BID_INCREMENT = 500  

def get_committee_status():
    now = datetime.now()
    target_date = now.replace(day=TARGET_DAY, hour=TARGET_HOUR, minute=0, second=0, microsecond=0)
    
    if now.day > TARGET_DAY or (now.day == TARGET_DAY and now.hour > TARGET_HOUR + 1):
        if now.month == 12:
            target_date = target_date.replace(year=now.year + 1, month=1)
        else:
            target_date = target_date.replace(month=now.month + 1)

    if now < target_date:
        return "WAITING", target_date
    else:
        if st.session_state['bidding_end_time'] is None:
            st.session_state['bidding_end_time'] = target_date + timedelta(minutes=BID_DURATION)
            
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
            st.rerun()
            
    st.success(f"नमस्ते, {st.session_state['current_user_name']}!")
    
    st.markdown("### ➕ नया मेम्बर ऐड करें")
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
    st.subheader("👥 रजिस्टर्ड मेम्बर्स")
    for mob, data in st.session_state['users_db'].items():
        if data['role'] == 'user':
            st.info(f"👤 **{data['name']}** (📱 {mob})")
            
    if st.button("🔙 डैशबोर्ड देखें"):
        st.session_state['current_role'] = 'user'
        st.rerun()

# --- 6. USER DASHBOARD ---
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

    status, end_time = get_committee_status()
    now = datetime.now()

    if status == "WAITING":
        time_diff = end_time - now
        days, seconds = time_diff.days, time_diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        st.markdown(f"**⏳ कमेटी बोली (25 तारीख सुबह 9:00 बजे) शुरू होने में बचा समय:**")
        
        timer_html = f"""
        <div class="timer-box" id="wait-timer">
            ⏳ {days} दिन {hours} घंटे {minutes} मिनट
        </div>
        """
        components.html(timer_html, height=80)
        st.info("9:00 बजते ही यहाँ 15 मिनट का लाइव टाइमर अपने आप शुरू हो जाएगा।")

    elif status == "OPEN":
        st.markdown('<div class="bidding-open">🟢 Live Bidding चालू है!</div>', unsafe_allow_html=True)
        
        timer_html = f"""
        <div class="timer-box" id="live-timer">⏳ टाइमर लोड हो रहा है...</div>
        <script>
            var countDownDate = new Date("{end_time.strftime('%b %d, %Y %H:%M:%S')}").getTime();
            var x = setInterval(function() {{
                var now = new Date().getTime();
                var distance = countDownDate - now;
                
                if (distance < 0) {{
                    clearInterval(x);
                    document.getElementById("live-timer").innerHTML = "🛑 बोली का समय समाप्त!";
                    document.getElementById("live-timer").className = "timer-box";
                }} else {{
                    var m = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var s = Math.floor((distance % (1000 * 60)) / 1000);
                    
                    var timerElem = document.getElementById("live-timer");
                    timerElem.innerHTML = "⏳ " + m + " मिनट " + s + " सेकंड बचे हैं";
                    
                    if (distance <= 60000) {{
                        timerElem.className = "timer-box red-alert";
                    }} else {{
                        timerElem.className = "timer-box";
                    }}
                }}
            }}, 1000);
        </script>
        """
        components.html(timer_html, height=80)

        if len(st.session_state['bid_history']) > 0:
            st.write("💬 **अब तक की बोलियाँ:**")
            for bid in st.session_state['bid_history'][-3:]:
                st.write(f"👉 **{bid['user']}** ने **₹ {bid['amount']}** लगाए।")
        else:
            st.info("अभी तक किसी ने बोली नहीं लगाई है।")

        highest_bid = st.session_state['highest_bid']
        next_min_bid = BASE_BID if highest_bid == 0 else highest_bid + BID_INCREMENT
        
        st.write("")
        with st.form("bidding_form"):
            new_bid = st.number_input(f"अपनी बोली डालें (कम से कम ₹{next_min_bid}):", min_value=next_min_bid, step=BID_INCREMENT, value=next_min_bid)
            
            if st.form_submit_button("💰 बोली दर्ज करें", use_container_width=True):
                current_time = datetime.now()
                if current_time >= st.session_state['bidding_end_time']:
                    st.error("🛑 समय समाप्त हो चुका है! आपकी बोली दर्ज नहीं की जा सकती।")
                elif new_bid >= next_min_bid:
                    time_left = st.session_state['bidding_end_time'] - current_time
                    if time_left.total_seconds() <= 60:
                        st.session_state['bidding_end_time'] += timedelta(minutes=1)
                        
                    st.session_state['highest_bid'] = new_bid
                    st.session_state['bid_history'].append({"user": name, "amount": new_bid})
                    st.success("✅ बोली दर्ज हो गई!")
                    st.rerun()
                else:
                    st.error("⚠️ रकम सही नहीं है!")

    elif status == "CLOSED":
        st.markdown('<div class="winner-box">🛑 इस महीने की बोली समाप्त हो चुकी है!</div>', unsafe_allow_html=True)
        
        if len(st.session_state['bid_history']) > 0:
            winner = st.session_state['bid_history'][-1]
            st.markdown(f'''
            <div style="text-align:center; padding:20px; background-color:#d4edda; border-radius:10px;">
                🏆 <h3>विजेता: {winner['user']}</h3>
                रकम: <b>₹ {winner['amount']}</b>
            </div>
            ''', unsafe_allow_html=True)
            st.balloons()
        else:
            st.warning("किसी ने भी बोली नहीं लगाई।")

# --- 7. MAIN APP ROUTER ---
if not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['current_role'] == 'admin':
        admin_page()
    else:
        dashboard_page()
