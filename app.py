import streamlit as st
from langchain.memory import ConversationBufferMemory

# --- 1. പേജ് സെറ്റപ്പ് ---
st.title("എൻ്റെ AI ചാറ്റ്‌ബോട്ട്")

# --- 2. ചാറ്റ് ഹിസ്റ്ററി സേവ് ചെയ്യാൻ മെമ്മറി സെറ്റ് ചെയ്യുന്നു ---
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

# --- 3. ബാക്കി ചാറ്റ് കോഡുകൾ ഇവിടെ എഴുതാം ---
# ഉദാഹരണത്തിന്:
user_input = st.text_input("നിങ്ങൾക്ക് എന്താണ് ചോദിക്കേണ്ടത്?")

if user_input:
    st.write(f"നിങ്ങൾ ചോദിച്ചത്: {user_input}")
    # മെമ്മറിയിൽ ഡാറ്റ സേവ് ചെയ്യുന്ന കോഡുകൾ ഇവിടെ തുടർന്ന് എഴുതാം
import io
import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import replicate
from supabase import create_client, Client
import qrcode

# --- Page Configuration ---
st.set_page_config(
    page_title="KPS Point AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

def render_recharge_section():
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

def get_user_credits(email: str) -> int:
    try:
        response = supabase.table("users").select("credits").eq("email", email).execute()
        if response.data:
            return response.data[0]["credits"]
        else:
            supabase.table("users").insert({"email": email, "credits": 10}).execute()
            return 10
    except Exception as e:
        st.error(f"Database Error: {e}")
        return 0

def deduct_credits(email: str, amount: int) -> int:
    current_credits = get_user_credits(email)
    new_credits = max(0, current_credits - amount)
    supabase.table("users").update({"credits": new_credits}).eq("email", email).execute()
    return new_credits

# --- Main App UI ---
st.sidebar.title("🔐 Login / Sign Up")
raw_email = st.sidebar.text_input("Enter your email to start:")
user_email = raw_email.strip().lower() if raw_email else ""

if user_email:
    credits = get_user_credits(user_email)
    st.sidebar.success(f"Logged in as: {user_email}")
    st.sidebar.metric("💰 Your Credits", credits)

    # Manual recharge toggle in sidebar
    st.sidebar.markdown("---")
    with st.sidebar.expander("💳 Recharge / Add Credits"):
        render_recharge_section()

    # Zero credits check
    if credits <= 0:
        st.sidebar.error("❌ No credits left!")
        render_recharge_section()
        st.warning("⚠️ You are out of credits. Please recharge via the sidebar to continue.")
        st.stop()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "🎨 Image Generator", "🎥 Video Generator"])

    # ---------------- TAB 1: CHAT ----------------
    with tab1:
        st.title("🤖 KPS Point AI Assistant")
        st.write("ചോദിക്കൂ, ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യൂ, അനലൈസ് ചെയ്യൂ! (സൗജന്യം) | Free AI Chat & Analysis")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        uploaded_file = st.file_uploader(
            "Upload an image or text file (Optional)",
            type=["jpg", "jpeg", "png", "txt"]
        )
        prompt = st.chat_input("Type your question here... | നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

        if prompt or uploaded_file:
            content_payload = []
            preview_image = None

            if uploaded_file:
                if uploaded_file.type.startswith("image/"):
                    preview_image = Image.open(uploaded_file)
                    content_payload.append(preview_image)
                elif uploaded_file.type == "text/plain":
                    text_content = uploaded_file.read().decode("utf-8")
                    content_payload.append(f"Attached file content:\n{text_content}")

            user_text = prompt if prompt else "Analyze this attachment."
            content_payload.append(user_text)

            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)
                if preview_image:
                    st.image(preview_image, caption="Uploaded Image", use_container_width=True)

            with st.chat_message("assistant"):
                with st.spinner("⏳ ചിന്തിക്കുന്നു... | AI is thinking..."):
                    try:
                        response = model.generate_content(content_payload)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ---------------- TAB 2: IMAGE GENERATOR ----------------
    with tab2:
        st.title("🎨 AI Image Generator")
        st.caption("Cost: **1 Credit** per generation")

        img_prompt = st.text_input(
            "Enter image description (English):",
            placeholder="e.g., A futuristic city with flying cars, cyberpunk style, 8k resolution"
        )

        if st.button("Generate Image 🖼️"):
            if not img_prompt:
                st.warning("Please enter a prompt first.")
            elif credits < 1:
                st.error("Insufficient credits! Please recharge.")
            else:
                with st.spinner("⏳ Generating image..."):
                    try:
                        output = replicate.run(
                            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                            input={"prompt": img_prompt}
                        )
                        image_url = output[0] if isinstance(output, list) else output
                        deduct_credits(user_email, 1)
                        st.session_state["last_generated_image"] = image_url
                        st.success("✅ Image generated! (1 credit deducted)")
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Persist generated image across reruns
        if "last_generated_image" in st.session_state:
            st.image(st.session_state["last_generated_image"], caption="Generated Image", use_container_width=True)

    # ---------------- TAB 3: VIDEO GENERATOR ----------------
    with tab3:
        st.title("🎥 AI Video Generator")
        st.caption("Cost: **5 Credits** per generation")

        video_prompt = st.text_input(
            "Enter video description (English):",
            placeholder="e.g., A futuristic car driving through a neon city at night, cinematic lighting, 4k"
        )

        if st.button("Generate Video 🎬"):
            if not video_prompt:
                st.warning("Please enter a prompt first.")
            elif credits < 5:
                st.error("You need at least 5 credits to generate a video! Please recharge.")
            else:
                with st.spinner("⏳ Generating video... This may take 1-2 minutes..."):
                    try:
                        output = replicate.run(
                            "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                            input={"prompt": video_prompt}
                        )
                        video_url = output[0] if isinstance(output, list) else output
                        deduct_credits(user_email, 5)
                        st.session_state["last_generated_video"] = video_url
                        st.success("✅ Video generated! (5 credits deducted)")
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Persist generated video across reruns
        if "last_generated_video" in st.session_state:
            st.video(st.session_state["last_generated_video"])

else:
    st.info("👈 Please enter your email in the sidebar to get started!")
