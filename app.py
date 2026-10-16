import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
from datetime import datetime
import urllib.parse

# Page Configuration for Mobile-like feel
st.set_page_config(page_title="Live Committee App", page_icon="💸", layout="centered")

# Custom CSS for Mobile App Look
st.markdown("""
<style>
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px;}
    .member-card {background-color: #ffffff; padding: 10px 15px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;}
    .winner-card {background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; text-align: center; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

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

APP_URL = "https://live-committee-app-tsnnxncqfoz34he6srtvvc.streamlit.app"

# ==========================================
#      INVITATION & REGISTRATION PAGE
# ==========================================
query_params = st.query_params
if "invite" in query_params:
    invite_mobile = query_params["invite"]
    
    st.title("🤝 Join Live Committee")
    
    # Fetch upcoming details to show to the invitee
    try:
        upcoming = db.reference('upcoming_settings').get()
        contrib = upcoming.get('contribution', 0) if upcoming else 0
        target_m = upcoming.get('target_members', 0) if upcoming else 0
        if contrib > 0:
            st.success(f"💎 **Contribution:** ₹{contrib} per member | 👥 **Target Members:** {target_m}")
    except:
        pass

    st.info("""
    📜 **Committee Rules:**
    1. Payment must be done within 2 days of bidding.
    2. Bidding is live. Last 1-minute bids will extend the timer by 60 seconds.
    3. Admin's decision is final.
    """)
    
    agree = st.checkbox("☑️ I Accept the Rules")
    if agree:
        with st.form("invite_join_form"):
            st.text_input("Mobile Number (ID)", value=invite_mobile, disabled=True)
            new_name = st.text_input("Enter Full Name")
            new_pass = st.text_input("Create Password", type="password")
            submit_join = st.form_submit_button("✅ Accept & Join")
            
            if submit_join:
                if new_name and new_pass:
                    db.reference(f'users/{invite_mobile}').set({'name': new_name, 'password': new_pass})
                    st.success("🎉 Registration Successful!")
                    st.markdown(f"**[👉 Click Here to Login]({APP_URL})**")
                else:
                    st.error("Please fill all details.")
    st.stop()

# ==========================================
#              NORMAL APP LOGIC
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'mobile' not in st.session_state:
    st.session_state.mobile = ""

st.title("💸 Live Committee")

page = st.sidebar.radio("Menu", ["👤 Member Dashboard", "🛠️ Admin Panel", "📜 History"])

# ------------------- ADMIN PANEL -------------------
if page == "🛠️ Admin Panel":
    admin_pass = st.sidebar.text_input("Admin Passcode", type="password")
    
    if admin_pass == "admin123":
        tab1, tab2 = st.tabs(["👥 1. Pre-Setup & Invites", "🚀 2. Start Bidding"])
        
        # TAB 1: SETUP & INVITES
        with tab1:
            st.subheader("Step 1: Set Target for Upcoming Committee")
            with st.form("upcoming_form"):
                col1, col2 = st.columns(2)
                with col1:
                    target_m = st.number_input("Target Members", min_value=2, value=10)
                with col2:
                    contrib = st.number_input("EMI/Contribution (₹)", min_value=1000, value=5000, step=500)
                if st.form_submit_button("Save Target"):
                    db.reference('upcoming_settings').set({'target_members': target_m, 'contribution': contrib})
                    st.success("Target Saved! Now send invites.")
            
            st.divider()
            st.subheader("Step 2: Invite Members")
            invite_mob = st.text_input("Mobile Number (without +91)")
            if st.button("Generate WhatsApp Invite"):
                if invite_mob and len(invite_mob) == 10:
                    invite_link = f"{APP_URL}/?invite={invite_mob}"
                    msg_text = f"Hello! 🤝 Maine tumhe apni Live Committee mein add kiya hai.\n\n🔗 Is link par click karke details check karo aur Join karo:\n{invite_link}"
                    wa_link = f"https://wa.me/91{invite_mob}?text={urllib.parse.quote(msg_text)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" style="background-color:#25D366;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;font-weight:bold;">💬 Send Invite</a>', unsafe_allow_html=True)
                else:
                    st.warning("Enter valid 10-digit number.")
                    
        # TAB 2: START COMMITTEE
        with tab2:
            try:
                current_data = db.reference('current_committee').get()
                if current_data and current_data.get('status') == 'Completed':
                    if st.button("📁 Archive Old Committee"):
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        T = current_data['total_pool']
                        B = current_data['highest_bid']
                        M = current_data['total_members']
                        F = current_data['app_fee']
                        db.reference('history').push({
                            'date': timestamp, 'total_pool': T, 'highest_bid': B,
                            'highest_bidder': current_data['highest_bidder'],
                            'emi': ((T - B) / M) + F, 'admin_fee': F * M, 'winner_received': T - B
                        })
                        db.reference('current_committee').delete()
                        st.success("Archived! Ready for new bidding.")
                        st.rerun()
            except: pass

            try:
                all_users = db.reference('users').get() or {}
                actual_member_count = len(all_users)
                upcoming = db.reference('upcoming_settings').get() or {}
                contrib = upcoming.get('contribution', 5000)
            except:
                actual_member_count = 0
                contrib = 5000
                
            st.info(f"👥 **Ready Members: {actual_member_count}** | 💸 **Contribution: ₹{contrib}**")

            with st.form("setup_committee"):
                c1, c2 = st.columns(2)
                with c1:
                    min_bid = st.number_input("Minimum Bid (₹)", value=1000, step=500)
                with c2:
                    app_fee = st.number_input("Platform Fee/Member (₹)", value=50)
                timer_minutes = st.number_input("Timer (Minutes)", min_value=1, value=15)
                
                if st.form_submit_button("🚀 Start Live Bidding"):
                    if actual_member_count < 2:
                        st.error("Need at least 2 members!")
                    else:
                        db.reference('current_committee').set({
                            'total_pool': contrib * actual_member_count,
                            'total_members': actual_member_count,
                            'min_bid': min_bid, 'app_fee': app_fee,
                            'highest_bid': 0, 'highest_bidder': "No one yet",
                            'status': "Active", 'end_time': time.time() + (timer_minutes * 60)
                        })
                        st.success("Bidding Started!")
    else:
        st.warning("Enter Admin Passcode")

# ------------------- MEMBER PANEL -------------------
elif page == "👤 Member Dashboard":
    if not st.session_state.logged_in:
        st.header("🔐 Login")
        mobile_input = st.text_input("Mobile Number")
        pass_input = st.text_input("Password", type="password")
        if st.button("Login"):
            user_data = db.reference(f'users/{mobile_input}').get()
            if user_data and user_data.get('password') == pass_input:
                st.session_state.logged_in = True
                st.session_state.user_name = user_data.get('name')
                st.session_state.mobile = mobile_input
                st.rerun()
            else:
                st.error("Wrong details.")
    else:
        c1, c2 = st.columns([3, 1])
        c1.subheader(f"👋 Hi, {st.session_state.user_name}")
        if c2.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
        st.divider()
        committee_data = db.reference('current_committee').get()
        
        # --- ACTIVE/COMPLETED BIDDING VIEW ---
        if committee_data and committee_data.get('status') in ["Active", "Completed"]:
            status = committee_data.get('status')
            end_time = committee_data.get('end_time', 0)
            
            if status == "Active" and int(end_time - time.time()) <= 0:
                db.reference('current_committee').update({'status': 'Completed'})
                st.rerun()

            if status == "Active":
                timer_html = f"""
                <div id="clock" style="background-color: #ffefc2; color: #856404; padding: 12px; border-radius: 8px; border: 1px solid #ffeeba; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 10px; transition: 0.5s;">
                    ⏳ Calculating...
                </div>
                <script>
                    var cDate = {int(end_time * 1000)};
                    var x = setInterval(function() {{
                        var dist = cDate - new Date().getTime();
                        if (dist <= 0) {{
                            clearInterval(x);
                            document.getElementById("clock").innerHTML = "⏳ Time is Up! Refresh bids.";
                            document.getElementById("clock").style.backgroundColor = "#f8d7da";
                            document.getElementById("clock").style.color = "#721c24";
                        }} else {{
                            var m = Math.floor((dist % (1000 * 60 * 60)) / (1000 * 60));
                            var s = Math.floor((dist % (1000 * 60)) / 1000);
                            document.getElementById("clock").innerHTML = "⏳ Remaining: " + ("0"+m).slice(-2) + ":" + ("0"+s).slice(-2);
                            if(dist <= 60000) {{ document.getElementById("clock").style.backgroundColor = "#ffcccc"; document.getElementById("clock").style.color = "#cc0000"; }}
                            else {{ document.getElementById("clock").style.backgroundColor = "#ffefc2"; document.getElementById("clock").style.color = "#856404"; }}
                        }}
                    }}, 1000);
                </script>
                """
                components.html(timer_html, height=65)
                
                c1, c2 = st.columns(2)
                c1.metric("💰 Total Pool", f"₹{committee_data['total_pool']}")
                c2.metric("📈 Highest Bid", f"₹{committee_data['highest_bid']} ({committee_data['highest_bidder']})")
                
                next_bid = committee_data['highest_bid'] + 500 if committee_data['highest_bid'] > 0 else committee_data['min_bid']
                new_bid = st.number_input("Your Bid (₹)", min_value=next_bid, step=500)
                
                if st.button("Submit Bid", use_container_width=True):
                    actual_time = time.time()
                    if actual_time < end_time:
                        remaining_time = end_time - actual_time
                        
                        # Fix: Sirf tabhi 60 seconds jodein jab time 1 minute se kam bacha ho
                        if remaining_time <= 60:
                            new_end_time = end_time + 60
                            success_msg = "Bid Placed! Time Extended by 1 minute."
                        else:
                            new_end_time = end_time
                            success_msg = "Bid Placed Successfully!"
                            
                        db.reference('current_committee').update({
                            'highest_bid': new_bid, 
                            'highest_bidder': st.session_state.user_name, 
                            'end_time': new_end_time
                        })
                        st.success(success_msg)
                        st.rerun()
                if st.button("🔄 Refresh", use_container_width=True): st.rerun()
                    
            elif status == "Completed":
                st.success("🎉 Bidding Ended!")
                T, B, M, F = committee_data['total_pool'], committee_data['highest_bid'], committee_data['total_members'], committee_data['app_fee']
                st.markdown(f"<div class='winner-card'>🏆 <b>Winner:</b> {committee_data['highest_bidder']}<br>💵 <b>Receives:</b> ₹{T-B:,.2f}<br>💸 <b>EMI (Per Member):</b> ₹{((T-B)/M)+F:,.2f}</div>", unsafe_allow_html=True)
        
        # --- WAITING LOUNGE (PRE-BIDDING) ---
        else:
            upcoming = db.reference('upcoming_settings').get() or {}
            all_users = db.reference('users').get() or {}
            target_m = upcoming.get('target_members', 10)
            contrib = upcoming.get('contribution', 0)
            joined_count = len(all_users)
            
            # Hall of Fame (Last Winner)
            try:
                hist = db.reference('history').get()
                if hist:
                    last_record = list(hist.values())[-1]
                    st.markdown(f"<div class='winner-card'>👑 <b>Hall of Fame (Last Winner)</b><br>{last_record['highest_bidder']} won ₹{last_record['winner_received']:,.0f}</div>", unsafe_allow_html=True)
            except: pass

            st.markdown("### 🛋️ Waiting Lounge")
            st.info("⏳ Bidding abhi shuru nahi hui hai. Kripya Admin ka intezar karein.")
            
            # Committee Overview
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='metric-card'>💸 <b>EMI/Month</b><br>₹{contrib}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'>💰 <b>Est. Pool</b><br>₹{contrib * target_m}</div>", unsafe_allow_html=True)
            
            # Progress Bar for Slots
            st.write(f"**Members Joined:** {joined_count} / {target_m}")
            st.progress(min(joined_count / target_m, 1.0))
            if joined_count < target_m:
                st.warning(f"Need {target_m - joined_count} more members to fill the slots.")
            else:
                st.success("All slots filled! Ready to start.")
            
            # Masked Member List
            st.divider()
            st.markdown("#### 👥 Committee Members")
            for mob, details in all_users.items():
                masked_mob = f"{mob[:2]}XXXXXX{mob[-2:]}" if len(mob) >= 4 else "Hidden"
                is_me = "(You)" if mob == st.session_state.mobile else ""
                st.markdown(f"<div class='member-card'><div>👤 <b>{details.get('name')}</b> {is_me}</div><div style='color:gray;'>📱 {masked_mob}</div></div>", unsafe_allow_html=True)

# ------------------- HISTORY PANEL -------------------
elif page == "📜 History":
    st.header("📜 Records")
    try:
        hist = db.reference('history').get()
        if hist:
            for key, rec in reversed(list(hist.items())):
                with st.expander(f"📅 {rec.get('date')} | 🏆 {rec.get('highest_bidder')}"):
                    st.write(f"💰 Total Pool: ₹{rec.get('total_pool')}")
                    st.write(f"📉 Final Bid: ₹{rec.get('highest_bid')}")
                    st.write(f"💵 Winner Got: ₹{rec.get('winner_received')}")
                    st.write(f"💸 EMI: ₹{rec.get('emi')}")
        else:
            st.info("No records found.")
    except: pass
