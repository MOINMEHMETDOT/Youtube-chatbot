import streamlit as st
import requests


# 🔗 Backend URL
API_BASE_URL = "https://youtube-chatbot-l532.onrender.com"  # Change for deployment


st.set_page_config(
    page_title="YouTube Q&A Assistant v1.1",
    page_icon="🎥",
    layout="wide"
)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "video_processed" not in st.session_state:
    st.session_state.video_processed = False
if "current_video" not in st.session_state:
    st.session_state.current_video = None
if "research_results" not in st.session_state:
    st.session_state.research_results = []


# Header
st.title("🎥 YouTube Video Q&A Assistant")
st.caption("Version 1.1 - Research Integration Ready")
st.markdown("""
Ask questions about any YouTube video using AI-powered transcript analysis.
**New:** Research papers & resources automatically linked to video content.""")

st.markdown(
    """
    <p style="font-size:24px; font-weight:bold;">
        Dear recruiter please read below line
    </p>
    """,
    unsafe_allow_html=True
)    

st.markdown("""
**⚠️Cloud Deployment Technical Limitation**
            
**⚠️ Production Notice:** If The Live demo shows "Processing failed"this is due to YouTube's strict cloud IP blocking on deployed servers (Render/Railway). See details below.
            
**✅ Works perfectly on localhost/development.**
This application faces YouTube bot detection on cloud platforms.

🎥 **Watch Full Technical Explanation Why it Failed:**
🎬 [Cloud vs Local Analysis](https://www.youtube.com/watch?v=Vwb89PJQHBc)

 **See It Working: in Local Machine**
▶️ [Local Demo (Working)](https://www.linkedin.com/posts/md-moinuddin-5777503ab_generativeai-machinelearning-python-activity-7426181276790980608-ELeA)

📂 [**GitHub:**](https://github.com/MOINMEHMETDOT/Youtube-chatbot/tree/main)
            
    ***Trying my best to resolve this issue for cloud deployment, As YouTube's anti-bot measures are very aggressive***
""")    

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **Owner:** Moin
    
    **Version:** 1.1
    
    **Features:**
    - 🔍 YouTube transcript extraction
    - 🧠 AI-powered Q&A
    - 📝 Context-aware answers
    - 🔬 Research paper integration (v2.0)
    
    **RIGHT NOW IT IS ON HOLD UNLIT PROBLEM RESOLVED THANKYOU:-:-:-**
    **🆕 v2.0 Coming Soon:**
    - 🤖 Auto research agent
    - 📄 arXiv/Google Scholar papers
    - 🌐 Related websites & tutorials
    - 🔗 Direct paper citations in answers
    """)
    
    st.divider()
    
    st.header("🚀 My Latest Projects")
    st.markdown("""
    **🔥 Agentic DOC RAG Assistant**  
    *[Check out my latest Agentic AI project]*  
    [https://agenticdocragassistant-9cvu5adthrbgvnez4sltvq.streamlit.app/](https://agenticdocragassistant-9cvu5adthrbgvnez4sltvq.streamlit.app/)
    """)
    
    st.markdown("""
    **📂 GitHub**  
    [https://github.com/MOINMEHMETDOT](https://github.com/MOINMEHMETDOT)
    """)
    
    st.divider()
    
    # Status indicator
    st.header("📊 Status")
    if st.session_state.video_processed:
        st.success("✅ Video loaded")
        if st.session_state.current_video:
            st.info(f"📹 Current video")
        if st.session_state.research_results:
            st.success(f"🔬 {len(st.session_state.research_results)} research resources found")
    else:
        st.warning("⚠️ No video loaded")
    
    st.divider()
    
    # Clear button
    if st.button("🗑️ Clear Chat & Video"):
        st.session_state.messages = []
        st.session_state.video_processed = False
        st.session_state.current_video = None
        st.session_state.research_results = []
        
        try:
            requests.delete(f"{API_BASE_URL}/youtube/clear", timeout=5)
        except:
            pass
        
        st.rerun()
    
    st.divider()
    
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.85em;'>
        <p>Built with FastAPI, LangChain & Gemini</p>
        <p>🔬 Research powered by AI Agent (v2.0)</p>
    </div>
    """, unsafe_allow_html=True)


st.divider()


# Video input section
st.header("📥 Step 1: Load YouTube Video")


col1, col2 = st.columns([4, 1])


with col1:
    youtube_url = st.text_input(
        "Enter YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        label_visibility="collapsed"
    )


with col2:
    process_button = st.button("🚀 Process", use_container_width=True)


if process_button:
    if not youtube_url.strip():
        st.warning("⚠️ Please enter a valid YouTube URL")
    else:
        with st.spinner("🔄 Processing video... Please Wait moment... Because (Render) backend part sleep if it is inactive and take time upto 5 Mins"):
            try:
                res = requests.post(
                    f"{API_BASE_URL}/youtube/ingest",
                    json={"youtube_url": youtube_url},
                    timeout=120
                )

                if res.status_code == 200:
                    st.success("✅ Video processed successfully!")
                    st.session_state.video_processed = True
                    st.session_state.current_video = youtube_url
                    st.session_state.messages = []
                    st.session_state.research_results = []
                else:
                    error_detail = res.json().get("detail", res.text)
                    st.error(f"❌ Expected: {error_detail}")
                    st.info("🔒 **This is YouTube cloud IP blocking.**")
                    st.session_state.video_processed = False
                    st.error("""
    - YouTube blocks **datacenter/cloud IPs** after ~1-3 requests
    - Detected as "bot" → `"Sign in to confirm you're not a bot"` or `IpBlocked` errors
    - **Tried & failed fixes:**
      - `yt-dlp` with cookies/browser export
      - Webshare free proxies (worked 12x, then blocked as "cloud web-based IP")
      - Residential rotating proxies (no free reliable option for continuous demo)
    **⚡ Localhost = 100% working** (no IP blocks, no captcha)
""")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. Video might be too long. Try a shorter video.")
            
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to backend. Make sure the API is running.")
            
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


st.divider()


# NEW: Research Integration Section
if st.session_state.video_processed:
    st.header("🔬 Step 1.5: Auto Research (v2.0 Feature)")
    
    research_col1, research_col2 = st.columns([1, 3])
    
    with research_col1:
        if st.button("🧠 Find Research Papers", use_container_width=True, disabled=len(st.session_state.research_results) > 0):
            with st.spinner("🔍 Searching research papers & resources..."):
                # Future API endpoint for research agent
                try:
                    res = requests.post(
                        f"{API_BASE_URL}/research/find",
                        json={"youtube_url": st.session_state.current_video},
                        timeout=90
                    )
                    if res.status_code == 200:
                        st.session_state.research_results = res.json().get("resources", [])
                        st.success(f"✅ Found {len(st.session_state.research_results)} relevant resources!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Research feature coming soon in v2.0")
                except:
                    st.info("🔄 Research Agent integration ready - v2.0 feature")
    
    with research_col2:
        if st.session_state.research_results:
            st.success(f"📚 Found {len(st.session_state.research_results)} research resources")
            with st.expander("📖 View Research Papers & Resources", expanded=True):
                for i, resource in enumerate(st.session_state.research_results[:5]):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**[{i+1}] {resource.get('title', 'N/A')}**")
                            st.caption(resource.get('source', ''))
                        with col2:
                            if resource.get('url'):
                                st.markdown(f"[🔗 View]({resource['url']})")
                        st.markdown(resource.get('snippet', ''))
        else:
            st.info("""
            **🚀 Research Agent Ready!**
            
            In v2.0 this will automatically find:
            - 📄 Relevant research papers (arXiv, Google Scholar)
            - 🌐 Authoritative websites
            - 📚 Related tutorials & documentation
            - 🔬 Technical references
            
            **Click "Find Research Papers" when ready!**
            """)


st.divider()


# Q&A Section
st.header("💬 Step 2: Ask Questions")


if not st.session_state.video_processed:
    st.info("👆 Please process a YouTube video first before asking questions.")
    st.stop()


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chat input
if question := st.chat_input("Ask anything about the video (or mention 'research' for paper references)..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    
    with st.chat_message("user"):
        st.write(question)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                res = requests.post(
                    f"{API_BASE_URL}/youtube/ask",
                    json={"question": question},
                    timeout=60
                )

                if res.status_code == 200:
                    answer = res.json().get("answer", "No answer generated")
                    st.write(answer)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                else:
                    error_detail = res.json().get("detail", res.text)
                    error_msg = f"❌ Error: {error_detail}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

            except requests.exceptions.Timeout:
                error_msg = "⏱️ Request timeout. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            
            except requests.exceptions.ConnectionError:
                error_msg = "🔌 Cannot connect to backend."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>💡 <b>Tips:</b> Ask specific questions like "What is the main topic?" or "Summarize the key points" or "Show me research papers on this topic"</p>
    <p>⚠️ <b>Cloud demo:</b> Fails due to YouTube IP blocks. Localhost = 100% working. See sidebar.</p>
    <p style='font-size: 0.8em; margin-top: 10px;'>YouTube Q&A Assistant v1.1 | Research Ready | Created by Moin</p>
</div>
""", unsafe_allow_html=True)

