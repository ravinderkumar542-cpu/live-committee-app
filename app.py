import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(page_title="Live Committee", page_icon="💸", layout="centered")

# 2. Custom CSS to hide Web UI and make it look like a Native App
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

# 3. App Title
st.title("💸 Live Committee")

# 4. Dummy Data for UI (इसे बाद में आप अपने असली डेटा से जोड़ सकते हैं)
members = ["Ravinder Kumar", "Gopal Dhiman", "Ankit Kumar", "Sachin"]

# 5. Sidebar - For simulating User Login
st.sidebar.title("🔐 Login / मेम्बर चुनें")
current_user = st.sidebar.selectbox("आप कौन हैं?", members)

# ----------------- DASHBOARD -----------------

# 6. Welcome Message
st.markdown(f"### 👋 नमस्ते, {current_user}!")
st.write("आपकी **Live Committee** का ताज़ा अपडेट यहाँ है:")

st.markdown("---")

# 7. Attractive Metrics (3 Box Layout)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🟢 कुल जमा (Paid)", value="₹ 44,000")
with col2:
    st.metric(label="🔴 बकाया (Due)", value="₹ 3,192")
with col3:
    st.metric(label="🏆 पिछले विजेता", value="Gopal")

st.markdown("<br>", unsafe_allow_html=True)

# 8. Action Area (Alerts based on payment status)
# Demo Logic: If user is Ravinder, show Due alert, else show Paid alert
if current_user == "Ravinder Kumar":
    st.warning("⏳ **ध्यान दें:** आपकी इस महीने की किश्त (₹ 3,192) पेंडिंग है। कृपया समय पर जमा करें।")
else:
    st.success("🎉 शानदार! आपकी इस महीने की किश्त सफलता से जमा हो चुकी है।")

st.markdown("<br>", unsafe_allow_html=True)

# 9. Next Bidding Countdown (Engagement Feature)
st.info("⏳ **अगली कमेटी:** अगली बोली (Bidding) खुलने में **8 दिन** बाकी हैं! तैयार रहें।")

st.markdown("---")

# ----------------- TRANSACTION HISTORY -----------------
st.subheader("📜 आपकी ट्रांज़ैक्शन हिस्ट्री")

# Using Expanders for clean UI
with st.expander("✅ October 2026 - सफलतापूर्वक जमा"):
    st.markdown("**तारीख:** 15 Oct 2026")
    st.markdown("**रकम:** ₹ 3,192")
    st.markdown("**स्टेटस:** 🟢 Paid")
    st.markdown("**रिसीट:** कमेटी संचालक द्वारा वेरिफाइड")

with st.expander("⏳ November 2026 - पेंडिंग (बकाया)"):
    st.markdown("**तारीख:** 15 Nov 2026")
    st.markdown("**रकम:** ₹ 3,192")
    st.markdown("**स्टेटस:** 🔴 Pending")
    st.button("Pay Now (एडमिन से संपर्क करें)")

st.markdown("---")

# ----------------- STAR MEMBERS -----------------
st.subheader("🌟 Star Members (इस महीने)")
st.caption("इन सदस्यों ने इस महीने सबसे पहले किश्त जमा की है। बहुत बढ़िया!")

# List of star members
st.markdown("🥇 ✅ **Gopal Dhiman**")
st.markdown("🥈 ✅ **Ankit Kumar**")
st.markdown("🥉 ✅ **Sachin**")

# Footer motivation
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Live Committee App v1.0 | सुरक्षित और पारदर्शी")
