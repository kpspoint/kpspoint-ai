st.sidebar.markdown("---")
if st.sidebar.button("💳 Recharge Credits"):
    st.sidebar.subheader("📱 Scan & Pay")
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

# No credits check
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
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "🎨 Image Generator", "🎥 Video Generator"])

# TAB 1: CHAT
with tab1:
    st.title("🤖 kpspoint AI Assistant")
    st.write("ചോദിക്കൂ, ചിത്രങ്ങൾ അപ്‌ലോഡ് ചെയ്യൂ, അനലൈസ് ചെയ്യൂ! (സൗജന്യം) | Ask questions, upload images & analyze for FREE!")

    # Chat History Memory
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded_file = st.file_uploader("Upload an image or file (Optional) | ഒരു ചിത്രമോ ഫയലോ അപ്‌ലോഡ് ചെയ്യുക", type=["jpg", "jpeg", "png", "pdf", "txt"])

    # Chat Input
    prompt = st.chat_input("Type your question here... | നിങ്ങളുടെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യുക...")

    if prompt or uploaded_file:
        file_to_send = None
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                file_to_send = Image.open(uploaded_file)
            else:
                file_to_send = uploaded_file.read()

        user_text = prompt if prompt else "Analyze this file/image | ഈ ഫയൽ/ചിത്രം അനലൈസ് ചെയ്യുക"

        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
            if file_to_send and uploaded_file.type.startswith("image/"):
                st.image(file_to_send, caption="Uploaded Image")

        with st.chat_message("assistant"):
            with st.spinner("⏳ AI ചിന്തിക്കുന്നു... | AI is thinking..."):
                try:
                    if file_to_send:
                        response = model.generate_content([file_to_send, user_text])
                    else:
                        response = model.generate_content(user_text)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

# TAB 2: IMAGE GENERATOR
with tab2:
    st.title("🎨 AI Image Generator")
    st.write("Generate stunning images just by typing a prompt! (Costs 1 Credit) | ഒരു പ്രോംപ്റ്റ് നൽകി മനോഹരമായ ചിത്രങ്ങൾ ഉണ്ടാക്കുക! (1 ക്രെഡിറ്റ്)")

    img_prompt = st.text_input("Enter image description (in English):", placeholder="e.g., A futuristic city with flying cars, cyberpunk style, 8k resolution")

    if st.button("Generate Image 🖼️"):
        if img_prompt:
            with st.spinner("⏳ Generating image..."):
                try:
                    output = replicate.run(
                        "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                        input={"prompt": img_prompt}
                    )
                    st.success("✅ Image generated successfully!")
                    st.image(output[0], caption="Generated Image")
                    deduct_credits(user_email, 1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a description!")

# TAB 3: VIDEO GENERATOR
with tab3:
    st.title("🎥 AI Video Generator")
    st.write("Generate short cinematic clips and reels! (Costs 5 Credits) | സിനിമാറ്റിക് വീഡിയോകൾ ഉണ്ടാക്കുക! (5 ക്രെഡിറ്റ്)")

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
