import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
from datetime import datetime, timedelta

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

st.title("💸 Live Committee & Bidding Platform")

page = st.sidebar.radio("Navigation", ["👤 Member Panel (Live Bidding)", "🛠️ Admin Panel"])

# ------------------- ADMIN PANEL -------------------
if page == "🛠️ Admin Panel":
    st.header("🛠️ Admin Panel - Setup New Committee")
    
    with st.form("setup_committee"):
        col1, col2 = st.columns(2)
        with col1:
            total_pool = st.number_input("Total Committee Amount (₹)", min_value=10000, value=100000, step=10000)
            total_members = st.number_input("Total Members", min_value=2, value=10)
        with col2:
            min_bid = st.number_input("Minimum Bid Allowed (₹)", min_value=0, value=1000, step=500)
            app_fee = st.number_input("Platform Fee Per Member (₹)", min_value=0, value=50)
            
        # Timer setup (15 Minutes)
        timer_minutes = st.number_input("Timer Duration (Minutes)", min_value=1, value=15)
        
        submit_setup = st.form_submit_button("Start Committee & Open Bidding")
        
        if submit_setup:
            end_timestamp = time.time() + (timer_minutes * 60)
            
            ref = db.reference('current_committee')
            ref.set({
                'total_pool': total_pool,
                'total_members': total_members,
                'min_bid': min_bid,
                'app_fee': app_fee,
                'highest_bid': 0,
                'highest_bidder': "No one yet",
                'status': "Active",
                'end_time': end_timestamp
            })
            st.success(f"✅ New Committee Started for {timer_minutes} minutes! Bidding is now open.")

# ------------------- MEMBER PANEL -------------------
elif page == "👤 Member Panel (Live Bidding)":
    st.header("👤 Live Bidding Room")
    
    try:
        committee_data = db.reference('current_committee').get()
        
        if committee_data:
            current_time = time.time()
            end_time = committee_data.get('end_time', 0)
            status = committee_data.get('status', 'Closed')
            remaining_seconds = int(end_time - current_time)
            
            # Check if time is up
            if status == "Active" and remaining_seconds <= 0:
                db.reference('current_committee').update({'status': 'Completed'})
                st.rerun()

            if status == "Active":
                # Show Timer
                mins, secs = divmod(remaining_seconds, 60)
                st.warning(f"⏳ **Time Remaining:** {mins:02d}:{secs:02d}")
                
                # Bidding Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("💰 Total Pool", f"₹ {committee_data['total_pool']}")
                col2.metric("📈 Current Highest Bid", f"₹ {committee_data['highest_bid']}")
                col3.metric("👑 Highest Bidder", committee_data['highest_bidder'])
                
                st.divider()
                
                # Bidding Form
                st.subheader("Place Your Bid")
                bidder_name = st.text_input("Your Name (Eg: Ravinder)")
                
                # Next minimum bid calculation
                next_min_bid = committee_data['highest_bid'] + 500
                if committee_data['highest_bid'] == 0:
                    next_min_bid = committee_data['min_bid']
                    
                new_bid = st.number_input("Enter Bid Amount (₹)", min_value=next_min_bid, step=500)
                
                if st.button("Submit Bid"):
                    if bidder_name:
                        # Refresh time to prevent offline cheating
                        actual_time = time.time()
                        if actual_time > end_time:
                            st.error("⏳ Time is up! You cannot place a bid anymore.")
                        else:
                            # Anti-Sniping Logic: If less than 20 seconds left, add 60 seconds
                            new_end_time = end_time
                            if (end_time - actual_time) < 20:
                                new_end_time = actual_time + 60
                                
                            db.reference('current_committee').update({
                                'highest_bid': new_bid,
                                'highest_bidder': bidder_name,
                                'end_time': new_end_time
                            })
                            st.success(f"✅ Bid placed! (Time extended if it was the last 20 seconds)")
                            st.rerun()
                    else:
                        st.error("Kripya apna naam dalein!")
                        
                if st.button("🔄 Refresh Timer & Bids"):
                    st.rerun()
                    
            elif status == "Completed":
                st.success("🎉 **Bidding has Ended!** 🎉")
                
                T = committee_data['total_pool']
                B = committee_data['highest_bid']
                M = committee_data['total_members']
                F = committee_data['app_fee']
                Winner = committee_data['highest_bidder']
                
                # Calculation Logic
                winner_amount = T - B
                emi_per_member = ((T - B) / M) + F
                total_admin_fee = F * M
                
                st.subheader("📊 Final Calculations")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"🏆 **Winner:** {Winner}")
                    st.info(f"💵 **Winner Receives:** ₹ {winner_amount:,.2f}")
                    st.info(f"📉 **Final Bid (Discount):** ₹ {B:,.2f}")
                    
                with col2:
                    st.error(f"💸 **EMI (Per Member):** ₹ {emi_per_member:,.2f}")
                    st.error(f"👥 **Total Members:** {M}")
                    st.warning(f"🛠️ **Admin/Platform Fee Collected:** ₹ {total_admin_fee:,.2f}")
                    
                st.divider()
                st.write("सभी मेंबर्स को यह अमाउंट (EMI) जमा करनी होगी, जिसमें ऐप/एडमिन फीस (₹{}) शामिल है।".format(F))

        else:
            st.info("⏳ Abhi koi Committee chalu nahi hai. Kripya Admin ka intezar karein.")
            
    except Exception as e:
        st.warning(f"Database Error: {e}")
