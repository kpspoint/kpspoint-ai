import streamlit as st

# --- ആപ്പിന്റെ ഐക്കൺ സെറ്റ് ചെയ്യുന്നു ---
st.set_page_config(
    page_title="kpspoint AI Assistant", 
    page_icon="kpspoint.png",  # ഇവിടെ നിങ്ങൾ അപ്‌ലോഡ് ചെയ്ത ഫയലിന്റെ പേര്
    layout="wide"
)

# ബാക്കി ഇംപോർട്ടുകൾ താഴെ തുടരാം...
import google.generativeai as genai
from PIL import Image
import replicate
import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import replicate
import os

# --- API Configuration ---
# 1. Google Gemini Setup
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.8-flash") 

# 2. Replicate Setup (For Image & Video)
os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- Create 3 Tabs ---
tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "🎨 Image Generator", "🎥 Video Generator"])

# ==========================================
# TAB 1: CHAT & IMAGE ANALYZER (Gemini)
# ==========================================
with tab1:
    st.title("🤖 kpspoint AI Assistant")
    st.write("ചോദിക്കൂ, ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യൂ, അനലൈസ് ചെയ്യൂ!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded_file = st.file_uploader("ഒരു ചിത്രമോ ഫയലോ അപ്‌ലോഡ് ചെയ്യുക (ഓപ്ഷണൽ)", type=["jpg", "jpeg", "png", "pdf", "txt"])
    prompt = st.chat_input("നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

    if prompt or uploaded_file:
        file_to_send = None
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                file_to_send = Image.open(uploaded_file)
            else:
                file_to_send = uploaded_file.read()

        user_text = prompt if prompt else "ഈ ഫയൽ/ചിത്രം അനലൈസ് ചെയ്യുക"
        
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
            if file_to_send and uploaded_file.type.startswith("image/"):
                st.image(file_to_send, caption="Uploaded Image")

        with st.chat_message("assistant"):
            with st.spinner("⏳ AI ചിന്തിക്കുന്നു..."):
                try:
                    if file_to_send:
                        response = model.generate_content([file_to_send, user_text])
                    else:
                        response = model.generate_content(user_text)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"എറർ: {e}")

# ==========================================
# TAB 2: IMAGE GENERATOR (Replicate)
# ==========================================
with tab2:
    st.title("🎨 AI Image Generator")
    st.write("Generate stunning images just by typing a prompt!")

    img_prompt = st.text_input("Enter image description (in English):", placeholder="e.g., A futuristic city with flying cars, cyberpunk style, 8k resolution")

    if st.button("Generate Image 🖼️"):
        if img_prompt:
            with st.spinner("⏳ Generating image... This may take 10-20 seconds..."):
                try:
                    # Using Stable Diffusion XL (SDXL) model
                    output = replicate.run(
                        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                        input={"prompt": img_prompt}
                    )
                    st.success("✅ Image generated successfully!")
                    st.image(output[0], caption="Generated Image")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a description to generate an image!")

# ==========================================
# TAB 3: VIDEO GENERATOR (Replicate)
# ==========================================
with tab3:
    st.title("🎥 AI Video Generator")
    st.write("Generate short cinematic clips and reels just by typing a prompt!")

    video_prompt = st.text_input("Enter video description (in English):", placeholder="e.g., A futuristic car driving through a neon city at night, cinematic lighting, 4k")

    if st.button("Generate Video 🎬"):
        if video_prompt:
            with st.spinner("⏳ Generating video... This may take 1-2 minutes..."):
                try:
                    # Using Zeroscope model for video
                    output = replicate.run(
                        "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                        input={"prompt": video_prompt}
                    )
                    st.success("✅ Video generated successfully!")
                    st.video(output[0])
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a description to generate a video!")
