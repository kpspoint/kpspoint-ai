import streamlit as st
import google.generativeai as genai

genai.configure(api_key="st.secrets["YOUR_KEY_NAME"] 


# AI മോഡൽ സെറ്റ് ചെയ്യുക
model = genai.GenerativeModel("gemini-3.8-flash") 

st.title("🤖 kpspoint AI Assistant")
st.write("സ്വാഗതം! എന്ത് ചോദിക്കണം?")

# ചാറ്റ് ഹിസ്റ്ററി
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ഉപയോക്താവിന്റെ ഇൻപുട്ട്
if prompt := st.chat_input("നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("⏳ AI ചിന്തിക്കുന്നു..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})