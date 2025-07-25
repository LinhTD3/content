import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import openai
import re

st.set_page_config(page_title="🎤 Interview Video to Story", layout="centered")
st.title("🎬 YouTube Video ➜ Social Media Story")
st.write("Paste a YouTube video link, and we’ll turn it into a summary and social media content.")

# --- API KEY Input ---
openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

# --- YouTube Video Input ---
youtube_url = st.text_input("📎 Paste a YouTube video URL")

# --- Extract YouTube Video ID ---
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

# --- Get Transcript ---
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except NoTranscriptFound:
        return None

# --- Generate Summary and Insights ---
def summarize_transcript(transcript, api_key):
    openai.api_key = api_key
    prompt = f"""
    You're a professional career advisor. Summarize this interview-related video transcript and extract 3–5 practical insights:

    Transcript:
    {transcript}

    Format:
    - Summary:
    - Key Insights:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

# --- Generate Social Media Posts ---
def create_social_posts(summary_text, api_key):
    openai.api_key = api_key
    prompt = f"""
    Create 3 social media posts based on the following interview advice summary and insights:

    1. LinkedIn post — professional tone.
    2. Facebook post — friendly and conversational.
    3. Threads post — short and snappy.

    Content:
    {summary_text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

# --- Main Logic ---
if youtube_url and openai_api_key:
    video_id = extract_video_id(youtube_url)
    if not video_id:
        st.error("❌ Invalid YouTube URL. Please check and try again.")
    else:
        with st.spinner("📜 Extracting transcript..."):
            transcript = get_transcript(video_id)
            if not transcript:
                st.error("😕 No transcript available for this video.")
            else:
                with st.spinner("🧠 Summarizing and extracting insights..."):
                    summary_text = summarize_transcript(transcript, openai_api_key)
                    st.markdown("### 🧠 Summary & Key Insights")
                    st.text(summary_text)

                with st.spinner("✍️ Generating social media posts..."):
                    posts = create_social_posts(summary_text, openai_api_key)
                    st.markdown("### 📱 Social Media Posts")
                    st.text(posts)
