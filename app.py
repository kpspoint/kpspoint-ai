import streamlit as st
import google.generativeai as genai
from PIL import Image
import replicate
import os
from supabase import create_client, Client
import qrcode
import io

# --- Page Configuration ---
st.set_page_config(page_title="kpspoint AI Studio", page_icon="🚀", layout="wide")

# --- Custom CSS for Beautiful Dark UI ---
st.markdown("""
<style>
    /* ആപ്പിന്റെ ബാക്ക്ഗ്രൗണ്ട് കറുപ്പ് ആക്കുന്നു */
    .stApp {
        background-color: #000000;
    }
    
    /* എല്ലാ ടെക്സ്റ്റുകളും വെളുപ്പ് ആക്കുന്നു */
    p, span, label, h1, h2, h3, h4, h5, h6, div, a {
        color: #ffffff !important;
    }
    
    /* സൈഡ്ബാറിന്റെ ബാക്ക്ഗ്രൗണ്ട് */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
    }
    
    /* ഇൻപുട്ട് ബോക്സുകൾ */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #222222;
        color: #ffffff;
    }
    
    /* ബട്ടണുകൾ */
    .stButton>button {
        background-color: #ffffff;
        color: #000000;
        font-weight: bold;
    }
    
    /* ചാറ്റ് ബോക്സുകൾ */
    .stChatMessage {
        background-color: #1a1a1a;
        border: 1px solid #333333;
    }
</style>
""", unsafe_allow_html=True)

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.5-flash-lite")

os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- Supabase Configuration ---
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- Helper Functions ---
def generate_upi_qr():
    upi_id = "shoukathali.kalathingalpalliyali@federal"
    payee_name = "KPSPOINT"
    amount = "100"
    note = "10 Credits"
    upi_link = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount}&cu=INR&tn={note}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
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

# --- Main App Sidebar UI ---
st.sidebar.title("🚀 kpspoint AI")
st.sidebar.markdown("### 🔐 Login / Sign Up")
user_email = st.sidebar.text_input("Enter your email to start:", key="email_login")

if user_email:
    credits = get_user_credits(user_email)
    st.sidebar.success(f"Logged in: {user_email}")
    st.sidebar.metric("💰 Your Credits", credits)

    # Recharge Button in Sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("💳 Recharge Credits"):
        st.sidebar.subheader("📱 Scan & Pay")
        qr_buffer = generate_upi_qr()
        st.sidebar.image(qr_buffer, width=180)
        st.sidebar.code("shoukathali.kalathingalpalliyali@federal", language=None)
        st.sidebar.markdown("---")
        st.sidebar.markdown("**🌍 International Users:**")
        st.sidebar.link_button("Pay via PayPal 💵", "https://paypal.me/kpyard")
        st.sidebar.markdown("---")
        st.sidebar.write("📸 **After payment**, send screenshot to:")
        st.sidebar.write("**WhatsApp:** +91 88487 03120")
        st.sidebar.write("We'll add your credits within 5 minutes! ⚡")

    # No credits check
    if credits <= 0:
        st.sidebar.error("❌ No credits left!")
        st.sidebar.markdown("---")
        st.sidebar.subheader("💳 Recharge Credits")
        st.sidebar.write("**Price:** ₹100 = 10 Credits")

        st.sidebar.markdown("#### 📱 Scan & Pay")
        qr_buffer = generate_upi_qr()
        st.sidebar.image(qr_buffer, width=180)

        st.sidebar.code("shoukathali.kalathingalpalliyali@federal", language=None)

        st.sidebar.markdown("---")
        st.sidebar.markdown("**🌍 International Users:**")
        st.sidebar.link_button("Pay via PayPal 💵", "https://paypal.me/kpyard")

        st.sidebar.markdown("---")
        st.sidebar.write("📸 **After payment**, send screenshot to:")
        st.sidebar.write("**WhatsApp:** +91 88487 03120")
        st.sidebar.write("We'll add your credits within 5 minutes! ⚡")
        st.stop()

    # --- Sidebar Menu (Replaces Tabs) ---
    st.sidebar.markdown("---")
    app_mode = st.sidebar.selectbox("Choose AI Tool", ["💬 AI Chat", "🎨 Image Generator", "🎥 Video Generator"])

    # --- 1. AI CHAT SECTION ---
    if app_mode == "💬 AI Chat":
        st.title("🤖 kpspoint AI Assistant
