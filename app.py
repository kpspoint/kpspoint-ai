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
st.markdown(
    """
<style>
    /* മൊത്തത്തിലുള്ള ആപ്പ് ബാക്ക്ഗ്രൗണ്ട് */
    .stApp {
        background-color: #0b0f19 !important;
    }

    /* എല്ലാ പ്രധാന ടെക്സ്റ്റുകളും വെളുപ്പാക്കുന്നു */
    h1, h2, h3, h4, h5, h6, span, label, a {
        color: #ffffff !important;
    }

    /* ഫയൽ അപ്‌ലോഡർ ബോക്സ് (വെള്ള നിറം വരുന്നത് തടയാൻ) */
    [data-testid="stFileUploader"] {
        background-color: #1f2937 !important;
        border: 2px dashed #4b5563 !important;
        border-radius: 10px;
        padding: 10px;
    }

    /* അപ്‌ലോഡർ ബോക്സിനുള്ളിലെ ടെക്സ്റ്റുകൾ കാണാൻ */
    [data-testid="stFileUploader"] section {
        background-color: #1f2937 !important;
    }
    [data-testid="stFileUploader"] section div, 
    [data-testid="stFileUploader"] section span, 
    [data-testid="stFileUploader"] section small {
        color: #ffffff !important;
    }

    /* അപ്‌ലോഡ് ബട്ടൺ ഡാർക്ക് ആക്കുന്നു */
    [data-testid="stFileUploader"] button {
        background-color: #374151 !important;
        color: #ffffff !important;
        border: 1px solid #6b7280 !important;
    }
    [data-testid="stFileUploader"] button svg {
        fill: #ffffff !important;
    }

    /* താഴെയുള്ള ചാറ്റ് ഇൻപുട്ട് ബോക്സ് */
    .stChatInputContainer {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
    }
    .stChatInputContainer textarea {
        background-color: #1f2937 !important;
        color: #ffffff !important;
    }
</style>
""",
    unsafe_allow_html=True,
)
# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

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
        st.title("🤖 kpspoint AI Assistant")
        st.markdown("💬 **ചോദിക്കൂ, ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യൂ, അനലൈസ് ചെയ്യൂ!** | *Ask questions, upload images & chat with full memory!*")

        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])

        for message in st.session_state.chat_session.history:
            role = "user" if message.role == "user" else "assistant"
            with st.chat_message(role):
                for part in message.parts:
                    if part.text:
                        st.markdown(part.text)

        uploaded_file = st.file_uploader("Upload an image (Optional) | ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യുക", type=["jpg", "jpeg", "png"], key="chat_img_uploader")
        prompt = st.chat_input("Type your question here... | നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
                img = None
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    st.image(img, width=200, caption="Uploaded Image")

            with st.chat_message("assistant"):
                with st.spinner("⏳ AI ചിന്തിക്കുന്നു... | AI is thinking..."):
                    try:
                        if uploaded_file:
                            response = st.session_state.chat_session.send_message([img, prompt])
                        else:
                            response = st.session_state.chat_session.send_message(prompt)

                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- 2. IMAGE GENERATOR SECTION ---
    elif app_mode == "🎨 Image Generator":
        st.title("🎨 AI Image Generator")
        st.markdown("✨ *Generate stunning images just by typing a prompt! (Costs 1 Credit)*")

        img_prompt = st.text_input("Enter image description (in English):", placeholder="e.g., A futuristic city with flying cars, cyberpunk style, 8k resolution", key="img_input")

        if st.button("Generate Image 🖼️"):
            if img_prompt:
                with st.spinner("⏳ Generating image... Please wait..."):
                    try:
                        output = replicate.run(
                            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                            input={"prompt": img_prompt}
                        )
                        st.success("✅ Image generated successfully!")
                        st.image(output[0], caption="Generated Image", use_column_width=True)
                        deduct_credits(user_email, 1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter a description!")

    # --- 3. VIDEO GENERATOR SECTION ---
    elif app_mode == "🎥 Video Generator":
        st.title("🎥 AI Video Generator")
        st.markdown("🎬 *Generate short cinematic clips and reels! (Costs 5 Credits)*")

        video_prompt = st.text_input("Enter video description (in English):", placeholder="e.g., A futuristic car driving through a neon city at night, cinematic lighting, 4k", key="vid_input")

        if st.button("Generate Video 🎬"):
            if video_prompt:
                with st.spinner("⏳ Generating video... This may take 1-2 minutes..."):
                    try:
                        output = replicate.run(
                            "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                            input={"prompt": video_prompt}
                        )
                        st.success("✅ Video generated successfully!")
                        st.video(output[0])
                        deduct_credits(user_email, 5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter a description!")

else:
    st.markdown("<h1 style='text-align: center; color: #4e54c8;'>🚀 Welcome to kpspoint AI Studio</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555;'>Your All-in-One AI Platform for Chatting, Images, and Videos.</h4>", unsafe_allow_html=True)
    st.info("👈 **Please enter your email in the left sidebar to start using the app!**")
