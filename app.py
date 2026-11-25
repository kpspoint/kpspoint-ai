import streamlit as st
import google.generativeai as genai

# API Key സുരക്ഷിതമായി വായിക്കുന്നു
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# AI മോഡൽ സെറ്റ് ചെയ്യുന്നു
model = genai.GenerativeModel("gemini-3.5-flash-lite")

# ആപ്പിന്റെ ടൈറ്റിൽ
st.title("🤖 kpspoint AI Assistant")
st.write("സ്വാഗതം! എന്ത് ചോദിക്കണം?")

# ചാറ്റ് ഹിസ്റ്ററി സൂക്ഷിക്കാൻ
if "messages" not in st.session_state:
    st.session_state.messages = []

# പഴയ ചാറ്റുകൾ സ്ക്രീനിൽ കാണിക്കാൻ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ഉപയോക്താവിന്റെ ചോദ്യം വാങ്ങാൻ
if prompt := st.chat_input("നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI മറുപടി നൽകുന്നു
    with st.chat_message("assistant"):
        with st.spinner("⏳ AI ചിന്തിക്കുന്നു..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
