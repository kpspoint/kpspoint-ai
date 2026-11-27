                with st.spinner("⏳ AI ചിന്തിക്കുന്നു... | AI is thinking..."):
                    try:
                        if image_for_prompt is not None:
                            response = st.session_state.chat_session.send_message(
                                [image_for_prompt, prompt]
                            )
                        else:
                            response = st.session_state.chat_session.send_message(
                                prompt
                            )

                        st.markdown(response.text)

                    except Exception as e:
                        st.error(f"Chat Error: {e}")

    # --- 2. IMAGE GENERATOR SECTION ---
    elif app_mode == "🎨 Image Generator":
        st.title("🎨 AI Image Generator")
        st.markdown(
            "✨ *Generate stunning images just by typing a prompt! "
            "(Costs 1 Credit)*"
        )

        img_prompt = st.text_input(
            "Enter image description (in English):",
            placeholder=(
                "e.g., A futuristic city with flying cars, "
                "cyberpunk style, 8k resolution"
            ),
            key="img_input"
        )

        if st.button("Generate Image 🖼️"):
            if not img_prompt.strip():
                st.warning("Please enter a description!")
            elif get_user_credits(user_email) < 1:
                st.error("You do not have enough credits.")
            else:
                with st.spinner("⏳ Generating image... Please wait..."):
                    try:
                        output = replicate.run(
                            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                            input={"prompt": img_prompt.strip()}
                        )

                        if output:
                            image_url = str(output[0])
                            st.image(
                                image_url,
                                caption="Generated Image",
                                use_container_width=True
                            )
                            st.success("✅ Image generated successfully!")
                            remaining_credits = deduct_credits(user_email, 1)
                            credits_display.metric("💰 Your Credits", remaining_credits)
                        else:
                            st.error(
                                "Image generation failed. Please try again."
                            )

                    except Exception as e:
                        st.error(f"Image Generation Error: {e}")

    # --- 3. VIDEO GENERATOR SECTION ---
    elif app_mode == "🎥 Video Generator":
        st.title("🎥 AI Video Generator")
        st.markdown(
            "🎬 *Generate short cinematic clips and reels! (Costs 5 Credits)*"
        )

        video_prompt = st.text_input(
            "Enter video description (in English):",
            placeholder=(
                "e.g., A futuristic car driving through a neon city "
                "at night, cinematic lighting, 4k"
            ),
            key="vid_input"
        )

        if st.button("Generate Video 🎬"):
            if not video_prompt.strip():
                st.warning("Please enter a description!")
            elif get_user_credits(user_email) < 5:
                st.error("You do not have enough credits. Video generation costs 5 credits.")
            else:
                with st.spinner(
                    "⏳ Generating video... This may take 1-2 minutes..."
                ):
                    try:
                        output = replicate.run(
                            "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                            input={"prompt": video_prompt.strip()}
                        )

                        if output:
                            st.video(str(output[0]))
                            st.success("✅ Video generated successfully!")
                            remaining_credits = deduct_credits(user_email, 5)
                            credits_display.metric("💰 Your Credits", remaining_credits)
                        else:
                            st.error(
                                "Video generation failed. Please try again."
                            )

                    except Exception as e:
                        st.error(f"Video Generation Error: {e}")

else:
    st.markdown(
        """
        <div style="text-align:center; padding: 3rem 1rem;">
            <h1 style="color:#A78BFA;">🚀 Welcome to kpspoint AI Studio</h1>
            <h4 style="color:#F1F5F9;">
                Your All-in-One AI Platform for Chatting, Images, and Videos.
            </h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.info(
        "👈 **Please enter your email in the left sidebar to start using the app!**"
    )
