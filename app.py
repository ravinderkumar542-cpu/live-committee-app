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
    
    /* User Dashboard Styles */
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
    
    /* Admin Dashboard Styles */
    .admin-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
    }
    .admin-card h2 { margin: 0; color: #0056b3; font-size: 24px; }
    .admin-card p { margin: 0; color: #6c757d; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & SESSION STATE ---
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "9876543210": {"name": "Admin (संचालक)", "role": "admin", "payment_status": "Paid", "txn_id": "CASH"}
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

# Settings
TARGET_DAY = 25      
TARGET_HOUR = 9      
BID_DURATION = 15    
BASE_BID = 500       
BID_INCREMENT = 500  
TOTAL_CAPACITY = 10  # कुल मेंबर्स की जगह

# --- 3. TIMING LOGIC ---
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
        submit_login = st.form_submit_button("लॉग令 इन करें 🚀", use_container_width=True)
        
        if submit_login:
            if mobile in st.session_state['users_db']:
                st.session_state['logged_in'] = True
                st.session_state['current_user_name'] = st.session_state['users_db'][mobile]['name']
                st.session_state['current_role'] = st.session_state['users_db'][mobile]['role']
                st.session_state['current_mobile'] = mobile
                st.rerun()
            else:
                st.error("❌ यह नंबर रजिस्टर्ड नहीं है। कृपया एडमिन से संपर्क करें।")

# --- 5. ADMIN PANEL (PRO DASHBOARD) ---
def admin_page():
    # Top Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ Admin Control Room")
    with col2:
        if st.button("Logout 🚪", key="admin_logout"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.write(f"वेलकम बॉस, **{st.session_state['current_user_name']}**!")
    st.markdown("---")

    # Creating 3 Tabs for Professional Look
    tab1, tab2, tab3 = st.tabs(["📊 ओवरव्यू", "👥 मेंबर मैनेजमेंट", "💸 पेमेंट रिपोर्ट"])

    # ----------- TAB 1: OVERVIEW -----------
    with tab1:
        st.subheader("कमेटी का लाइव स्टेटस")
        status, _ = get_committee_status()
        
        # Calculate totals
        user_count = sum(1 for data in st.session_state['users_db'].values() if data['role'] == 'user')
        paid_count = sum(1 for data in st.session_state['users_db'].values() if data['role'] == 'user' and data['payment_status'] == 'Paid')
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='admin-card'><p>कुल मेंबर्स</p><h2>{user_count} / {TOTAL_CAPACITY}</h2></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='admin-card'><p>सबसे बड़ी बोली</p><h2>₹ {st.session_state['highest_bid']}</h2></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='admin-card'><p>पेमेंट आ गए</p><h2>{paid_count}</h2></div>", unsafe_allow_html=True)
            
        st.write("<br>", unsafe_allow_html=True)
        if status == "OPEN":
            st.success("🟢 लाइव बोली (Bidding) अभी चालू है!")
        elif status == "WAITING":
            st.warning("⏳ अभी बोली शुरू होने का इंतज़ार है।")
        else:
            st.error("🛑 इस महीने की बोली खत्म हो चुकी है।")

    # ----------- TAB 2: MEMBER MANAGEMENT -----------
    with tab2:
        st.subheader("मेंबर जोड़ें (Add New Member)")
        
        # Progress Bar for Capacity
        st.write(f"**कमेटी स्पेस:** {TOTAL_CAPACITY - user_count} जगह खाली हैं")
        st.progress(user_count / TOTAL_CAPACITY if TOTAL_CAPACITY > 0 else 0)
        
        with st.form("add_user_form", clear_on_submit=True):
            col_name, col_mob = st.columns(2)
            with col_name:
                new_name = st.text_input("मेंबर का पूरा नाम:")
            with col_mob:
                new_mobile = st.text_input("मोबाइल नंबर (10 अंक):", max_chars=10)
            
            submit_add = st.form_submit_button("✅ मेंबर सेव करें", use_container_width=True)
            
            if submit_add:
                if user_count >= TOTAL_CAPACITY:
                    st.error("⚠️ कमेटी फुल हो चुकी है! और मेंबर ऐड नहीं कर सकते।")
                elif len(new_mobile) == 10 and new_name:
                    # Added default payment status and txn_id for new members
                    st.session_state['users_db'][new_mobile] = {
                        "name": new_name, 
                        "role": "user", 
                        "payment_status": "Pending", 
                        "txn_id": ""
                    }
                    st.success(f"🎉 {new_name} सफलता से जुड़ गए हैं!")
                    st.rerun()
                else:
                    st.error("⚠️ कृपया सही नाम और 10 अंकों का मोबाइल नंबर डालें।")

        st.write("---")
        st.write("**मौजूदा मेंबर्स की लिस्ट:**")
        # Displaying users in a neat table format instead of plain text
        member_list = []
        for mob, data in st.session_state['users_db'].items():
            if data['role'] == 'user':
                member_list.append({"नाम": data['name'], "मोबाइल नंबर": mob})
        
        if member_list:
            st.table(pd.DataFrame(member_list))
        else:
            st.info("अभी तक कोई मेंबर ऐड नहीं किया गया है।")

    # ----------- TAB 3: PAYMENT REPORT -----------
    with tab3:
        st.subheader("मंथली पेमेंट कलेक्शन")
        
        pending_users = []
        paid_users = []
        
        for mob, data in st.session_state['users_db'].items():
            if data['role'] == 'user':
                if data['payment_status'] == 'Paid':
                    paid_users.append({"नाम": data['name'], "Txn ID": data['txn_id']})
                else:
                    pending_users.append({"नाम": data['name'], "मोबाइल": mob})
                    
        st.write("🟢 **जिनका पेमेंट आ गया (Paid):**")
        if paid_users:
            st.table(pd.DataFrame(paid_users))
        else:
            st.write("अभी किसी का पेमेंट नहीं आया है।")
            
        st.write("🔴 **जिनका पेमेंट बाकी है (Pending):**")
        if pending_users:
            st.table(pd.DataFrame(pending_users))
        else:
            st.write("सबका पेमेंट आ चुका है!")

    st.markdown("---")
    if st.button("👁️ यूज़र डैशबोर्ड (Member View) देखें"):
        st.session_state['current_role'] = 'user'
        st.rerun()

# --- 6. USER DASHBOARD (Live Bidding & Timer) ---
def dashboard_page():
    name = st.session_state['current_user_name']
    mobile = st.session_state['current_mobile']
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💸 Live Committee")
    with col2:
        if st.button("Logout 🚪", key="user_logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.markdown(f"### 👋 नमस्ते, {name}!")
    
    # Check if admin is viewing as user, give button to go back
    if st.session_state['users_db'][mobile]['role'] == 'admin':
        if st.button("🔙 एडमिन पैनल पर वापस जाएं"):
            st.session_state['current_role'] = 'admin'
            st.rerun()
            
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
