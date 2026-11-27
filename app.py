
        img_prompt = st.text_input(
            "Enter image description (in English):",
            placeholder=(
                "e.g., A futuristic city with flying cars, "
                "cyberpunk style, 8k resolution"
            ),
            key="img_prompt",
        )

        if st.button("Generate Image 🖼️", key="generate_image"):
            if not img_prompt.strip():
                st.warning("Please enter a description!")
            elif get_user_credits(user_email) < 1:
                st.error("You do not have enough credits.")
            else:
                with st.spinner("⏳ Generating image..."):
                    try:
                        output = replicate.run(
                            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                            input={"prompt": img_prompt.strip()},
                        )

                        image_content = replicate_file_content(output)

                        if image_content:
                            if isinstance(image_content, str):
                                st.image(
                                    image_content,
                                    caption="Generated Image",
                                    use_container_width=True,
                                )
                            else:
                                st.image(
                                    image_content,
                                    caption="Generated Image",
                                    use_container_width=True,
                                )

                            st.success("✅ Image generated successfully!")
                            remaining_credits = deduct_credits(
                                user_email, 1
                            )
                            credits_display.metric(
                                "💰 Your Credits",
                                remaining_credits,
                            )
                        else:
                            st.error(
                                "Image generation failed. Please try again."
                            )

                    except Exception as e:
                        st.error(f"Image Generation Error: {e}")

    # --- TAB 3: VIDEO GENERATOR ---
    with tab3:
        st.title("🎥 AI Video Generator")
        st.write(
            "Generate short cinematic clips and reels! "
            "(Costs 5 Credits) | സിനിമാറ്റിക് വീഡിയോകൾ ഉണ്ടാക്കുക! "
            "(5 ക്രെഡിറ്റ്)"
        )

        video_prompt = st.text_input(
            "Enter video description (in English):",
            placeholder=(
                "e.g., A futuristic car driving through a neon city "
                "at night, cinematic lighting, 4k"
            ),
            key="video_prompt",
        )

        if st.button("Generate Video 🎬", key="generate_video"):
            if not video_prompt.strip():
                st.warning("Please enter a description!")
            elif get_user_credits(user_email) < 5:
                st.error(
                    "You do not have enough credits. "
                    "Video generation costs 5 credits."
                )
            else:
                with st.spinner(
                    "⏳ Generating video... This may take 1-2 minutes..."
                ):
                    try:
                        output = replicate.run(
                            "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                            input={"prompt": video_prompt.strip()},
                        )

                        video_content = replicate_file_content(output)

                        if video_content:
                            st.video(video_content)
                            st.success("✅ Video generated successfully!")
                            remaining_credits = deduct_credits(
                                user_email, 5
                            )
                            credits_display.metric(
                                "💰 Your Credits",
                                remaining_credits,
                            )
                        else:
                            st.error(
                                "Video generation failed. Please try again."
                            )

                    except Exception as e:
                        st.error(f"Video Generation Error: {e}")

else:
    st.warning(
        "⚠️ Please enter your email in the left sidebar "
        "to start using the app!"
    )
