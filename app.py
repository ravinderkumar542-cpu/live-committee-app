import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time

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

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["👤 Member Panel (Live Bidding)", "🛠️ Admin Panel"])

# ------------------- ADMIN PANEL -------------------
if page == "🛠️ Admin Panel":
    # Optional: Basic Admin Password to prevent members from opening this page
    admin_pass = st.sidebar.text_input("Admin Passcode", type="password")
    
    if admin_pass == "admin123": # Aap is password ko badal sakte hain
        st.header("🛠️ Admin Dashboard")
        
        # Tabs for Admin
        tab1, tab2 = st.tabs(["🚀 Start Committee", "👥 Add/Manage Members"])
        
        # TAB 1: START COMMITTEE
        with tab1:
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
            
            # (clear_on_submit=True) lagane se save karte hi box khali ho jayenge
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
            
            # Niche sabhi add kiye hue members ki list dikhegi
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
    
    # IF NOT LOGGED IN -> SHOW LOGIN SCREEN
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
                
    # IF LOGGED IN -> SHOW BIDDING ROOM
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
                   # --- NAYA LIVE TIMER CODE ---
                    timer_html = f"""
                    <div id="clock" style="background-color: #ffefc2; color: #856404; padding: 12px; border-radius: 8px; border: 1px solid #ffeeba; font-size: 18px; font-weight: bold; font-family: sans-serif; text-align: center; margin-bottom: 10px;">
                        ⏳ Time Remaining: Calculating...
                    </div>
                    <script>
                        var countDownDate = {{int(end_time * 1000)}};
                        var x = setInterval(function() {{{{
                            var now = new Date().getTime();
                            var distance = countDownDate - now;
                            if (distance <= 0) {{{{
                                clearInterval(x);
                                document.getElementById("clock").innerHTML = "⏳ Time is Up! Please click 'Refresh Timer & Bids' button below.";
                                document.getElementById("clock").style.backgroundColor = "#f8d7da";
                                document.getElementById("clock").style.color = "#721c24";
                            }}}} else {{{{
                                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                                document.getElementById("clock").innerHTML = "⏳ Time Remaining: " + ("0" + minutes).slice(-2) + ":" + ("0" + seconds).slice(-2);
                            }}}}
                        }}}}, 1000);
                    </script>
                    """
                    components.html(timer_html, height=65)
                    # ----------------------------
                    
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
                                'highest_bidder': st.session_state.user_name, # Ab naam automatic jayega
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
                    
                    winner_amount = T - B
                    emi_per_member = ((T - B) / M) + F
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"🏆 **Winner:** {Winner}")
                        st.info(f"💵 **Winner Receives:** ₹ {winner_amount:,.2f}")
                        
                    with col2:
                        st.error(f"💸 **EMI (Per Member):** ₹ {emi_per_member:,.2f}")
                        st.warning(f"🛠️ **Admin/Platform Fee Collected:** ₹ {F * M:,.2f}")
            else:
                st.info("⏳ Abhi koi Committee chalu nahi hai. Kripya Admin ka intezar karein.")
                
        except Exception as e:
            st.warning(f"Database Error: {e}")
