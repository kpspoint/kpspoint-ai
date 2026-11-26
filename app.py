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
import qrcode
import io

def generate_upi_qr():
    """നിങ്ങളുടെ UPI ID ഉപയോഗിച്ച് QR കോഡ് ജനറേറ്റ് ചെയ്യുന്നു"""
    upi_id = "shoukathali.kalathingalpalliyali@federal"
    payee_name = "KPSPOINT"
    amount = "100"
    note = "10 Credits"
    
    # UPI deep link ഫോർമാറ്റ്
    upi_link = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount}&cu=INR&tn={note}"
    
    # QR കോഡ് ഉണ്ടാക്കുന്നു
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Streamlit-ൽ കാണിക്കാൻ ബൈറ്റാക്കി മാറ്റുന്നു
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
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
    
    # ✅ ഇത് ഇവിടെ പേസ്റ്റ് ചെയ്യുക
            if credits <= 0:
            st.sidebar.error("❌ No credits left!")
            st.sidebar.markdown("---")
            st.sidebar.subheader("💳 Recharge Credits")
            st.sidebar.write("**Price:** ₹100 = 10 Credits")
            
            st.sidebar.markdown("#### 📱 Scan & Pay")
            qr_buffer = generate_upi_qr()
            st.sidebar.image(qr_buffer, width=200)
            
            st.sidebar.code("shoukathali.kalathingalpalliyali@federal", language=None)
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("**🌍 International Users:**")
            st.sidebar.link_button("Pay via PayPal 💵", "https://paypal.me/kpyard")
            
            st.sidebar.markdown("---")
            st.sidebar.write("📸 **After payment**, send screenshot to:")
            st.sidebar.write("**WhatsApp:** +91 88487 03120")
            st.sidebar.write("We'll add your credits within 5 minutes! ⚡")
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
