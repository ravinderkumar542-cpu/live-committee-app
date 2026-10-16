import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
from datetime import datetime

st.set_page_config(page_title="Live Committee App", page_icon="💸", layout="wide")

# ----------------- FIREBASE CONNECTION -----------------
if not firebase_admin._apps:
    try:
        firebase_secrets = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://committee-app-88cab-default-rtdb.firebaseio.com/' 
        })
    except Exception as e:
        st.error(f"❌ Firebase Error: {e}")
# -------------------------------------------------------

# Session State for Login Tracking
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'mobile' not in st.session_state:
    st.session_state.mobile = ""

st.title("💸 Live Committee & Bidding Platform")

# Sidebar navigation - NAYA HISTORY PAGE ADD KIYA HAI
page = st.sidebar.radio("Navigation", ["👤 Member Panel (Live Bidding)", "🛠️ Admin Panel", "📜 History & Records"])

# ------------------- ADMIN PANEL -------------------
if page == "🛠️ Admin Panel":
    admin_pass = st.sidebar.text_input("Admin Passcode", type="password")
    
    if admin_pass == "admin123":
        st.header("🛠️ Admin Dashboard")
        
        tab1, tab2 = st.tabs(["🚀 Start & Manage Committee", "👥 Add/Manage Members"])
        
        # TAB 1: START OR ARCHIVE COMMITTEE
        with tab1:
            try:
                current_data = db.reference('current_committee').get()
                # Agar committee complete ho chuki hai, toh Archive ka button dikhayen
                if current_data and current_data.get('status') == 'Completed':
                    st.success("🎉 Pichli Committee safaltapurvak poori ho chuki hai!")
                    st.warning("⚠️ Nayi committee shuru karne se pehle purani ko History mein save karein.")
                    
                    if st.button("📁 Archive & Reset Committee"):
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        T = current_data['total_pool']
                        B = current_data['highest_bid']
                        M = current_data['total_members']
                        F = current_data['app_fee']
                        
                        # History mein data push karein
                        db.reference('history').push({
                            'date': timestamp,
                            'total_pool': T,
                            'highest_bid': B,
                            'highest_bidder': current_data['highest_bidder'],
                            'emi': ((T - B) / M) + F,
                            'admin_fee': F * M,
                            'winner_received': T - B
                        })
                        # Current committee ko delete kar dein taki nayi shuru ho sake
                        db.reference('current_committee').delete()
                        st.success("✅ Committee Archived! Ab aap nayi boli shuru kar sakte hain.")
                        st.rerun()
            except Exception as e:
                pass

            st.divider()
            st.subheader("Setup New Committee")
            with st.form("setup_committee"):
                col1, col2 = st.columns(2)
                with col1:
                    total_pool = st.number_input("Total Amount (₹)", min_value=10000, value=100000, step=10000)
                    total_members = st.number_input("Total Members", min_value=2, value=10)
                with col2:
                    min_bid = st.number_input("Minimum Bid (₹)", min_value=0, value=1000, step=500)
                    app_fee = st.number_input("Platform Fee Per Member (₹)", min_value=0, value=50)
                    
                timer_minutes = st.number_input("Timer Duration (Minutes)", min_value=1, value=15)
                submit_setup = st.form_submit_button("Start Committee & Open Bidding")
                
                if submit_setup:
                    end_timestamp = time.time() + (timer_minutes * 60)
                    db.reference('current_committee').set({
                        'total_pool': total_pool,
                        'total_members': total_members,
                        'min_bid': min_bid,
                        'app_fee': app_fee,
                        'highest_bid': 0,
                        'highest_bidder': "No one yet",
                        'status': "Active",
                        'end_time': end_timestamp
                    })
                    st.success(f"✅ Committee Started for {timer_minutes} minutes!")

        # TAB 2: MANAGE MEMBERS
        with tab2:
            st.subheader("Register New Member")
            with st.form("add_user_form", clear_on_submit=True):
                new_name = st.text_input("Member Name")
                new_mobile = st.text_input("Mobile Number (This is their Login ID)")
                new_pass = st.text_input("Assign a Password")
                add_user = st.form_submit_button("Save Member")
                
                if add_user:
                    if new_name and new_mobile and new_pass:
                        db.reference(f'users/{new_mobile}').set({
                            'name': new_name,
                            'password': new_pass
                        })
                        st.success(f"✅ {new_name} added successfully! Mobile: {new_mobile}")
                    else:
                        st.error("Kripya sabhi details bharein.")
            
            st.divider()
            st.subheader("📋 Registered Members")
            try:
                all_users = db.reference('users').get()
                if all_users:
                    for mob, details in all_users.items():
                        st.write(f"👤 **{details.get('name', 'Unknown')}** (Login ID: {mob})")
                else:
                    st.info("Abhi tak koi member add nahi hua hai.")
            except Exception:
                pass
    else:
        st.warning("🔒 Kripya Admin Panel access karne ke liye sahi Admin Passcode dalein. (Default: admin123)")

# ------------------- MEMBER PANEL -------------------
elif page == "👤 Member Panel (Live Bidding)":
    if not st.session_state.logged_in:
        st.header("🔐 Member Login")
        mobile_input = st.text_input("Mobile Number")
        pass_input = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if mobile_input and pass_input:
                user_data = db.reference(f'users/{mobile_input}').get()
                if user_data and user_data.get('password') == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user_data.get('name')
                    st.session_state.mobile = mobile_input
                    st.success(f"Welcome {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error("❌ Galat Mobile Number ya Password.")
            else:
                st.warning("Kripya Mobile aur Password dalein.")
    else:
        colA, colB = st.columns([4, 1])
        with colA:
            st.header(f"👤 Welcome, {st.session_state.user_name}!")
        with colB:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.mobile = ""
                st.rerun()
                
        st.divider()
        try:
            committee_data = db.reference('current_committee').get()
            
            if committee_data:
                current_time = time.time()
                end_time = committee_data.get('end_time', 0)
                status = committee_data.get('status', 'Closed')
                remaining_seconds = int(end_time - current_time)
                
                if status == "Active" and remaining_seconds <= 0:
                    db.reference('current_committee').update({'status': 'Completed'})
                    st.rerun()

                if status == "Active":
                    timer_html = f"""
                    <div id="clock" style="background-color: #ffefc2; color: #856404; padding: 12px; border-radius: 8px; border: 1px solid #ffeeba; font-size: 18px; font-weight: bold; font-family: sans-serif; text-align: center; margin-bottom: 10px;">
                        ⏳ Time Remaining: Calculating...
                    </div>
                    <script>
                        var countDownDate = {int(end_time * 1000)};
                        var x = setInterval(function() {{
                            var now = new Date().getTime();
                            var distance = countDownDate - now;
                            if (distance <= 0) {{
                                clearInterval(x);
                                document.getElementById("clock").innerHTML = "⏳ Time is Up! Please click 'Refresh Timer & Bids' button below.";
                                document.getElementById("clock").style.backgroundColor = "#f8d7da";
                                document.getElementById("clock").style.color = "#721c24";
                            }} else {{
                                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                                document.getElementById("clock").innerHTML = "⏳ Time Remaining: " + ("0" + minutes).slice(-2) + ":" + ("0" + seconds).slice(-2);
                            }}
                        }}, 1000);
                    </script>
                    """
                    components.html(timer_html, height=65)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💰 Total Pool", f"₹ {committee_data['total_pool']}")
                    col2.metric("📈 Current Highest Bid", f"₹ {committee_data['highest_bid']}")
                    col3.metric("👑 Highest Bidder", committee_data['highest_bidder'])
                    
                    st.divider()
                    st.subheader("Place Your Bid")
                    
                    next_min_bid = committee_data['highest_bid'] + 500
                    if committee_data['highest_bid'] == 0:
                        next_min_bid = committee_data['min_bid']
                        
                    new_bid = st.number_input("Enter Bid Amount (₹)", min_value=next_min_bid, step=500)
                    
                    if st.button("Submit Bid"):
                        actual_time = time.time()
                        if actual_time > end_time:
                            st.error("⏳ Time is up! You cannot place a bid anymore.")
                        else:
                            new_end_time = end_time
                            if (end_time - actual_time) < 20:
                                new_end_time = actual_time + 60
                                
                            db.reference('current_committee').update({
                                'highest_bid': new_bid,
                                'highest_bidder': st.session_state.user_name,
                                'end_time': new_end_time
                            })
                            st.success("✅ Bid placed successfully!")
                            st.rerun()
                            
                    if st.button("🔄 Refresh Timer & Bids"):
                        st.rerun()
                        
                elif status == "Completed":
                    st.success("🎉 **Bidding has Ended!** 🎉")
                    T = committee_data['total_pool']
                    B = committee_data['highest_bid']
                    M = committee_data['total_members']
                    F = committee_data['app_fee']
                    Winner = committee_data['highest_bidder']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"🏆 **Winner:** {Winner}")
                        st.info(f"💵 **Winner Receives:** ₹ {T - B:,.2f}")
                    with col2:
                        st.error(f"💸 **EMI (Per Member):** ₹ {((T - B) / M) + F:,.2f}")
                        st.warning(f"🛠️ **Admin/Platform Fee Collected:** ₹ {F * M:,.2f}")
            else:
                st.info("⏳ Abhi koi Committee chalu nahi hai. Kripya Admin ka intezar karein.")
        except Exception as e:
            st.warning(f"Database Error: {e}")

# ------------------- HISTORY PANEL -------------------
elif page == "📜 History & Records":
    st.header("📜 Committee History & Records")
    st.write("Yahan aapki sabhi purani committees ka hisaab-kitaab save rahega.")
    
    try:
        history_data = db.reference('history').get()
        if history_data:
            # Data ko ulta (reverse) kar rahe hain taaki latest wali upar dikhe
            for key, record in reversed(list(history_data.items())):
                date_str = record.get('date', 'Unknown Date')
                winner_name = record.get('highest_bidder', 'Unknown')
                
                with st.expander(f"📅 Date: {date_str} | 🏆 Winner: {winner_name}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"💰 **Total Pool:** ₹ {record.get('total_pool', 0):,.2f}")
                        st.write(f"📉 **Final Bid (Discount):** ₹ {record.get('highest_bid', 0):,.2f}")
                        st.write(f"💵 **Winner Received:** ₹ {record.get('winner_received', 0):,.2f}")
                    with c2:
                        st.write(f"💸 **EMI Per Member:** ₹ {record.get('emi', 0):,.2f}")
                        st.write(f"🛠️ **Platform Fee Collected:** ₹ {record.get('admin_fee', 0):,.2f}")
        else:
            st.info("📭 Abhi tak koi purani committee ka record nahi hai.")
    except Exception as e:
        st.warning(f"History load karne mein error: {e}")
