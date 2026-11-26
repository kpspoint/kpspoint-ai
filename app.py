import streamlit as st
import google.generativeai as genai
from PIL import Image
import replicate
import os
from supabase import create_client, Client

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.8-flash") 

os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- Supabase Configuration ---
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- Helper Functions for Credits ---
def get_user_credits(email):
    try:
        response = supabase.table("users").select("credits").eq("email", email).execute()
        if response.data:
            return response.data[0]['credits']
        else:
            supabase.table("users").insert({"email": email, "credits": 10}).execute()
            return 10
    except Exception as e:
        st.error(f"Database Error: {e}")
        return 0

def deduct_credits(email, amount):
    current_credits = get_user_credits(email)
    new_credits = current_credits - amount
    supabase.table("users").update({"credits": new_credits}).eq("email", email).execute()
    return new_credits

# --- Main App UI ---
st.set_page_config(page_title="kpspoint AI Studio", page_icon="🚀", layout="wide")

st.sidebar.title("🔐 Login / Sign Up")
user_email = st.sidebar.text_input("Enter your email to start:")

if user_email:
    credits = get_user_credits(user_email)
    st.sidebar.success(f"Logged in as: {user_email}")
    st.sidebar.metric("💰 Your Credits", credits)
    
    if credits <= 0:
        st.sidebar.error("❌ No credits left!")
        st.sidebar.markdown("---")
        st.sidebar.subheader("💳 Recharge Credits")
        st.sidebar.write("**Price:** ₹100 for 10 Credits")
        st.sidebar.write("**UPI ID:** shoukathali.kalathingalpalliyali@federal") #
        st.sidebar.write("**PayPal:**  https://paypal.me/kpyard") # 
        st.sidebar.write("Send screenshot to WhatsApp:  +918848703120") #
        st.stop() # Stop the app if no credits

    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "🎨 Image Generator", "🎥 Video Generator"])
    
    # ==========================================
    # TAB 1: CHAT & IMAGE ANALYZER (Free)
    # ==========================================
    with tab1:
        st.title("🤖 kpspoint AI Assistant")
        st.write("ചോദിക്കൂ, ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യൂ, അനലൈസ് ചെയ്യൂ! (സൗജന്യം)")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        uploaded_file = st.file_uploader("ഒരു ചിത്രമോ ഫയലോ അപ്‌ലോഡ് ചെയ്യുക (ഓപ്ഷണൽ)", type=["jpg", "jpeg", "png", "pdf", "txt"])
