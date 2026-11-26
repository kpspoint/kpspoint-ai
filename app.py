import streamlit as st
import google.generativeai as genai
from PIL import Image

# API Key സുരക്ഷിതമായി വായിക്കുന്നു
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# AI മോഡൽ സെറ്റ് ചെയ്യുന്നു
model = genai.GenerativeModel("gemini-3-pro-image")

st.title("🤖 kpspoint AI Assistant")
st.write("ചിത്രങ്ങളോ ഫയലുകളോ അപ്‌ലോഡ് ചെയ്ത് ചോദിക്കാം!")

# ചാറ്റ് ഹിസ്റ്ററി
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ഫയൽ അപ്‌ലോഡ് ചെയ്യാൻ
uploaded_file = st.file_uploader("ഒരു ചിത്രമോ ഫയലോ അപ്‌ലോഡ് ചെയ്യുക (ഓപ്ഷണൽ)", type=["jpg", "jpeg", "png", "pdf", "txt"])

# ഉപയോക്താവിന്റെ ചോദ്യം
prompt = st.chat_input("നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

if prompt or uploaded_file:
    file_to_send = None
    
    # അപ്‌ലോഡ് ചെയ്ത ഫയൽ പ്രോസസ്സ് ചെയ്യുന്നു
    if uploaded_file:
        if uploaded_file.type.startswith("image/"):
            file_to_send = Image.open(uploaded_file)
        else:
            file_to_send = uploaded_file.read()

    user_text = prompt if prompt else "ഈ ഫയൽ/ചിത്രം അനലൈസ് ചെയ്യുക"
    
    # ചാറ്റിൽ കാണിക്കാൻ
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
        if file_to_send and uploaded_file.type.startswith("image/"):
            st.image(file_to_send, caption="Uploaded Image")

    # AI മറുപടി
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
                # --- വീഡിയോ ജനറേറ്റർ ഭാഗം ---
st.markdown("---")
st.header("🎥 AI വീഡിയോ ജനറേറ്റർ")
st.write("ഒരു വാക്യം നൽകിയാൽ AI അതിനനുസരിച്ചുള്ള വീഡിയോ ഉണ്ടാക്കി തരും!")

import replicate

# Replicate ടോക്കൺ സെറ്റ് ചെയ്യുന്നു
replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])

video_prompt = st.text_input("വീഡിയോയ്ക്കുള്ള വിവരണം (ഇംഗ്ലീഷിൽ നൽകുക):", placeholder="ഉദാ: A futuristic car driving through a neon city at night")

if st.button("വീഡിയോ ഉണ്ടാക്കുക"):
    if video_prompt:
        with st.spinner("⏳ വീഡിയോ ഉണ്ടാക്കുന്നു... ഇതിന് 1-2 മിനിറ്റ് എടുത്തേക്കാം..."):
            try:
                # ഒരു ലളിതമായ Text-to-Video മോഡൽ ഉപയോഗിക്കുന്നു
                output = replicate.run(
                    "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                    input={"prompt": video_prompt}
                )
                st.success("✅ വീഡിയോ തയ്യാർ!")
                st.video(output[0]) # വീഡിയോ കാണിക്കുന്നു
            except Exception as e:
                st.error(f"എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വിവരണം നൽകുക!")
