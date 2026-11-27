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

# --- Custom CSS for Beautiful UI & Text Visibility Fix ---
st.markdown("""
    <style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #f8f9fa;
        color: #111111 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Make all standard text dark for readability */
    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #222222 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e1e2f;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Buttons Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #ff8008 0%, #ffc837 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4e54c8 0%, #8f94fb 100%) !important;
        color: white !important;
    }
    .stTabs [aria-selected="true"] p {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- API Configuration ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.5-flash-lite") # Updated model name for better compatibility

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
user_email = st.sidebar.text_input("Enter your email to start:")

if user_email:
    credits = get_user_credits(user_email)
    st.sidebar.success(f"Logged in: {user_email}")
    st.sidebar.metric("💰 Your Credits", credits)

    # Recharge Button
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

    # --- Main App Tabs ---
    tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "🎨 Image Generator", "🎥 Video Generator"])

    # TAB 1: CHAT
    with tab1:    # TAB 1: CHAT
    with tab1:
        st.title("🤖 kpspoint AI Assistant")
        st.markdown("💬 **ചോദിക്കൂ, ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യൂ, അനലൈസ് ചെയ്യൂ!** | *Ask questions, upload images & chat with full memory!*")

        # Initialize chat history in session state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Initialize Gemini chat session with proper history
        if "chat_session" not in st.session_state:
            # Convert previous messages to Gemini format if restarting
            st.session_state.chat_session = model.start_chat(history=[])

        # Display previous chat messages from Streamlit session state
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "image" in message and message["image"]:
                    st.image(message["image"], width=200)

        # File uploader for images
        uploaded_file = st.file_uploader("Upload an image (Optional) | ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യുക", type=["jpg", "jpeg", "png"], key="chat_img_uploader")

        # Chat Input
        prompt = st.chat_input("Type your question here... | നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

        if prompt:
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
                img = None
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    st.image(img, width=200, caption="Uploaded Image")

            # Save user message to history
            st.session_state.messages.append({"role": "user", "content": prompt, "image": img})

            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("⏳ AI ചിന്തിക്കുന്നു... | AI is thinking..."):
                    try:
                        # Send message to Gemini chat session
                        if uploaded_file:
                            response = st.session_state.chat_session.send_message([img, prompt])
                        else:
                            response = st.session_state.chat_session.send_message(prompt)

                        st.markdown(response.text)

                        # Save assistant response to history
                        st.session_state.messages.append({"role": "assistant", "content": response.text})

                    except Exception as e:
                        st.error(f"Error: {e}")
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

        uploaded_file = st.file_uploader("Upload an image (Optional) | ഒരു ചിത്രം അപ്‌ലോഡ് ചെയ്യുക", type=["jpg", "jpeg", "png"])
        prompt = st.chat_input("Type your question here... | നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    st.image(img, width=200, caption="Uploaded Image")

            with st.chat_message("assistant"):
                with st.spinner("⏳ AI ചിന്തിക്കുന്നു... | AI is thinking..."):
                    try:
                        if uploaded_file:
                            img = Image.open(uploaded_file)
                            response = st.session_state.chat_session.send_message([img, prompt])
                        else:
                            response = st.session_state.chat_session.send_message(prompt)

                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # TAB 2: IMAGE GENERATOR
    with tab2:
        st.title("🎨 AI Image Generator")
        st.markdown("✨ *Generate stunning images just by typing a prompt! (Costs 1 Credit)*")

        img_prompt = st.text_input("Enter image description (in English):", placeholder="e.g., A futuristic city with flying cars, cyberpunk style, 8k resolution")

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

    # TAB 3: VIDEO GENERATOR
    with tab3:
        st.title("🎥 AI Video Generator")
        st.markdown("🎬 *Generate short cinematic clips and reels! (Costs 5 Credits)*")

        video_prompt = st.text_input("Enter video description (in English):", placeholder="e.g., A futuristic car driving through a neon city at night, cinematic lighting, 4k")

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
