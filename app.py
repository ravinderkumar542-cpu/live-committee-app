import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

st.set_page_config(page_title="Live Committee App", page_icon="💸", layout="wide")

# ----------------- FIREBASE CONNECTION -----------------
# Ensure Firebase is only initialized once
if not firebase_admin._apps:
    try:
        # JSON file ka naam jo aapne laptop mein save ki hai
        cred = credentials.Certificate("firebase_key.json")
        
        # YAHAN APNA DATABASE URL DALEIN (Firebase dashboard se copy karke)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://committee-app-88cab-default-rtdb.firebaseio.com/' 
        })
    except Exception as e:
        st.error(f"❌ Firebase Error: {e}")
# -------------------------------------------------------

st.title("💸 Live Committee & Bidding Platform")

# Sidebar navigation
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
            
        submit_setup = st.form_submit_button("Start Committee & Open Bidding")
        
        if submit_setup:
            # Data Firebase mein save karne ka code
            ref = db.reference('current_committee')
            ref.set({
                'total_pool': total_pool,
                'total_members': total_members,
                'min_bid': min_bid,
                'app_fee': app_fee,
                'highest_bid': 0,
                'highest_bidder': "No one yet",
                'status': "Active"
            })
            st.success("✅ New Committee Started! Members can now place bids.")

# ------------------- MEMBER PANEL -------------------
elif page == "👤 Member Panel (Live Bidding)":
    st.header("👤 Live Bidding Room")
    
    # Firebase se live data padhna
    try:
        committee_data = db.reference('current_committee').get()
        
        if committee_data and committee_data.get('status') == "Active":
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Pool", f"₹ {committee_data['total_pool']}")
            col2.metric("📈 Current Highest Bid", f"₹ {committee_data['highest_bid']}")
            col3.metric("👑 Highest Bidder", committee_data['highest_bidder'])
            
            st.divider()
            
            # Bidding Form
            st.subheader("Place Your Bid")
            bidder_name = st.text_input("Your Name")
            new_bid = st.number_input("Enter Bid Amount (₹)", min_value=committee_data['highest_bid'] + 500, step=500)
            
            if st.button("Submit Bid"):
                if bidder_name:
                    # Nayi bid ko Firebase mein update karna
                    ref = db.reference('current_committee')
                    ref.update({
                        'highest_bid': new_bid,
                        'highest_bidder': bidder_name
                    })
                    st.success(f"✅ Bid of ₹{new_bid} placed successfully! Page will update.")
                    st.rerun()
                else:
                    st.error("Kripya apna naam dalein!")
                    
        else:
            st.info("⏳ Abhi koi Committee chalu nahi hai. Kripya Admin ka intezar karein.")
            
    except Exception as e:
        st.warning("Database se connect karne mein samasya. Kripya Admin se sampark karein.")