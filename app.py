import streamlit as st
from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
import openai

# Streamlit UI
st.set_page_config(page_title="Interview Insights Generator", layout="centered")
st.title("🎤 Interview Tips to Social Posts")
st.write("Turn a YouTube video into a professional social media post in seconds.")

# API Key input
openai_api_key = st.text_input("🔑 Enter your OpenAI API key:", type="password")

# Button
if st.button("✨ Generate from Top YouTube Interview Video") and openai_api_key:
    openai.api_key = openai_api_key

    # Step 1: Search YouTube
    with st.spinner("Searching for top video..."):
        search = VideosSearch("interview tips", limit=1)
        video = search.result()["result"][0]
        video_id = video["id"]
        video_title = video["title"]
        video_link = video["link"]

    st.success("Found video!")
    st.markdown(f"**🎥 {video_title}**  \n📎 [Watch on YouTube]({video_link})")

    # Step 2: Get transcript
    with st.spinner("Extracting transcript..."):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([entry["text"] for entry in transcript])
        except Exception as e:
            st.error(f"Failed to get transcript: {e}")
            st.stop()

    # Step 3: Summarize
    with st.spinner("Summarizing and extracting insights..."):
        summary_prompt = f"""
        You are a career expert. Summarize the following interview advice transcript, and extract 3–5 key actionable insights.

        Transcript:
        {transcript_text}

        Format:
        - Summary:
        - Key Insights:
        """
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.7
        )
        summary_output = response.choices[0].message.content.strip()

    st.markdown("### 🧠 Summary & Key Insights")
    st.text(summary_output)

    # Step 4: Generate social posts
    with st.spinner("Writing social media posts..."):
        post_prompt = f"""
        Based on the following summary and insights about interview tips, create 3 engaging social media posts:

        1. A professional and thoughtful LinkedIn post
        2. A friendly and shareable Facebook post
        3. A short, punchy Threads post

        Content:
        {summary_output}
        """
        post_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": post_prompt}],
            temperature=0.8
        )
        posts = post_response.choices[0].message.content.strip()

    st.markdown("### ✍️ Social Media Posts")
    st.text(posts)

elif not openai_api_key:
    st.warning("Please enter your OpenAI API key.")
