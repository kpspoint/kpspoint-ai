import os
from google import genai
from google.genai import types
from PIL import Image
import replicate
import streamlit as st

# Keys സെറ്റ് ചെയ്യുക (Secrets അല്ലെങ്കിൽ Environment Variables വഴി)
# os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
# GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

gemini_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def extract_first_media(output):
    if isinstance(output, (list, tuple)) and len(output) > 0:
        first = output[0]
        return getattr(first, "url", first)
    return getattr(output, "url", output)


def generate_image_with_gemini(prompt_text: str):
    result = gemini_client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt_text,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
        ),
    )
    return result.generated_images[0].image.image_bytes


def generate_image_with_replicate(prompt_text: str):
    raw_output = replicate.run(
        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        input={"prompt": prompt_text},
    )
    return extract_first_media(raw_output)


def render_recharge_ui():
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


if st.sidebar.button("💳 Recharge Credits"):
    render_recharge_ui()
def safe_int(value, default: int = 0) -> int:
    if value is None or isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# നിങ്ങളുടെ നിലവിലുള്ള user_email / get_credits ലോജിക് അനുസരിച്ച് സുരക്ഷിതമായി എടുക്കുക
user_email = st.session_state.get("user_email")
if isinstance(user_email, str) and user_email.strip():
    user_email = user_email.strip().lower()
    try:
        raw_credits = get_credits(user_email)
    except Exception:
        raw_credits = 0
    credits = safe_int(raw_credits, default=0)
else:
    user_email = None
    credits = 0

if credits <= 0:
    st.sidebar.error("❌ No credits left!")
    render_recharge_ui()
    st.stop()
if credits <= 0:
    st.sidebar.error("❌ No credits left!")
    render_recharge_ui()
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_processed_file" not in st.session_state:
    st.session_state.last_processed_file = None

tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "🎨 Image Generator", "🎥 Video Generator"])

# TAB 1: CHAT
with tab1:
    st.title("🤖 kpspoint AI Assistant")
    st.write("ചോദിക്കൂ, ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യൂ, അനലൈസ് ചെയ്യൂ! (സൗജന്യം) | Ask questions, upload images & analyze for FREE!")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("image") is not None:
                st.image(message["image"], caption="Uploaded Image")

    uploaded_file = st.file_uploader(
        "Upload an image or file (Optional) | ഒരു ചിത്രമോ ഫയലോ അപ്‌ലോഡ് ചെയ്യുക",
        type=["jpg", "jpeg", "png", "pdf", "txt"],
    )
    prompt = st.chat_input("Type your question here... | നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

    file_sig = (uploaded_file.name, uploaded_file.size) if uploaded_file else None
    is_new_file = file_sig is not None and file_sig != st.session_state.last_processed_file

    if prompt or is_new_file:
        content_parts = []
        pil_image = None

        if uploaded_file and (is_new_file or prompt):
            if uploaded_file.type.startswith("image/"):
                uploaded_file.seek(0)
                pil_image = Image.open(uploaded_file)
                content_parts.append(pil_image)
            elif uploaded_file.type == "text/plain":
                uploaded_file.seek(0)
                text_data = uploaded_file.getvalue().decode("utf-8", errors="replace")
                content_parts.append(f"Uploaded file ({uploaded_file.name}):\n{text_data}")
            else:
                uploaded_file.seek(0)
                content_parts.append(uploaded_file.read())

            if file_sig is not None:
                st.session_state.last_processed_file = file_sig

        user_text = prompt if prompt else "Analyze this file/image | ഈ ഫയൽ/ചിത്രം അനലൈസ് ചെയ്യുക"
        content_parts.append(user_text)

        st.session_state.messages.append({"role": "user", "content": user_text, "image": pil_image})
        with st.chat_message("user"):
            st.markdown(user_text)
            if pil_image is not None:
                st.image(pil_image, caption="Uploaded Image")

        with st.chat_message("assistant"):
            with st.spinner("⏳ AI ചിന്തിക്കുന്നു... | AI is thinking..."):
                try:
                    response = model.generate_content(content_parts)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

# TAB 2: IMAGE GENERATOR (Google AI Studio + Replicate)
with tab2:
    IMAGE_COST = 1
    st.title("🎨 AI Image Generator")
    st.write(f"Generate stunning images just by typing a prompt! (Costs {IMAGE_COST} Credit) | ഒരു പ്രോംപ്റ്റ് നൽകി മനോഹരമായ ചിത്രങ്ങൾ ഉണ്ടാക്കുക! ({IMAGE_COST} ക്രെഡിറ്റ്)")

    img_provider = st.radio(
        "Select Image Engine:",
        ["Google AI Studio (Imagen)", "Replicate"],
        horizontal=True,
    )
    img_prompt = st.text_input(
        "Enter image description (in English):",
        placeholder="e.g., A futuristic city with flying cars, cyberpunk style, 8k resolution",
    )

    if st.button("Generate Image 🖼️"):
        if not img_prompt.strip():
            st.warning("Please enter a description!")
        elif credits < IMAGE_COST:
            st.error(f"You need at least {IMAGE_COST} credit to generate an image.")
        else:
            with st.spinner("⏳ Generating image..."):
                try:
                    if img_provider.startswith("Google"):
                        image_result = generate_image_with_gemini(img_prompt.strip())
                    else:
                        image_result = generate_image_with_replicate(img_prompt.strip())

                    deduct_credits(user_email, IMAGE_COST)
                    st.session_state["last_generated_image"] = image_result
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.get("last_generated_image"):
        st.success("✅ Image generated successfully!")
        st.image(st.session_state["last_generated_image"], caption="Generated Image")

# TAB 3: VIDEO GENERATOR (Replicate)
with tab3:
    VIDEO_COST = 5
    st.title("🎥 AI Video Generator")
    st.write(f"Generate short cinematic clips and reels! (Costs {VIDEO_COST} Credits) | സിനിമാറ്റിക് വീഡിയോകൾ ഉണ്ടാക്കുക! ({VIDEO_COST} ക്രെഡിറ്റ്)")

    video_prompt = st.text_input(
        "Enter video description (in English):",
        placeholder="e.g., A futuristic car driving through a neon city at night, cinematic lighting, 4k",
    )

    if st.button("Generate Video 🎬"):
        if not video_prompt.strip():
            st.warning("Please enter a description!")
        elif credits < VIDEO_COST:
            st.error(f"You need at least {VIDEO_COST} credits to generate a video.")
        else:
            with st.spinner("⏳ Generating video... This may take 1-2 minutes..."):
                try:
                    raw_output = replicate.run(
                        "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                        input={"prompt": video_prompt.strip()},
                    )
                    video_result = extract_first_media(raw_output)
                    deduct_credits(user_email, VIDEO_COST)
                    st.session_state["last_generated_video"] = video_result
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.get("last_generated_video"):
        st.success("✅ Video generated successfully!")
        st.video(st.session_state["last_generated_video"])
