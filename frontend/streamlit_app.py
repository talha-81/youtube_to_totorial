import streamlit as st
import requests
import time
import json
import os


# Page config
st.set_page_config(
    page_title="YouTube to Tutorial Converter",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint
import os
API_URL = os.getenv("API_URL", "http://localhost:8000")


# Initialize session state for theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Custom CSS with theme support
def get_custom_css(dark_mode):
    if dark_mode:
        return """
        <style>
            .main {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            .stButton>button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            .step-card {
                background: #2d2d2d;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .step-number {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5em;
                font-weight: bold;
                margin-right: 15px;
            }
            .content-box {
                background: #2d2d2d;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                color: #e0e0e0;
            }
            .stMarkdown h3 {
                color: #e0e0e0;
            }
        </style>
        """
    else:
        return """
        <style>
            .main {
                background-color: #f5f5f5;
                color: #333;
            }
            .stButton>button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            .step-card {
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .step-number {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5em;
                font-weight: bold;
                margin-right: 15px;
            }
            .content-box {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                color: #333;
            }
        </style>
        """

st.markdown(get_custom_css(st.session_state.dark_mode), unsafe_allow_html=True)

# Title and theme toggle
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🎥 YouTube to Tutorial Converter")
    st.markdown("Transform any YouTube video into a structured step-by-step tutorial with AI")
with col2:
    st.write("")
    st.write("")
    if st.button("🌓 Toggle Theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Initialize session state
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'tutorial_data' not in st.session_state:
    st.session_state.tutorial_data = None
if 'youtube_url' not in st.session_state:
    st.session_state.youtube_url = None
if 'pdf_generated' not in st.session_state:
    st.session_state.pdf_generated = False

# Input section
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        youtube_url = st.text_input(
            "Enter YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste the full YouTube video URL here"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        process_button = st.button("🚀 Convert to Tutorial")

# Process video
if process_button and youtube_url:
    st.session_state.youtube_url = youtube_url
    st.session_state.pdf_generated = False  # Reset PDF generation flag
    with st.spinner("Starting video processing..."):
        try:
            response = requests.post(
                f"{API_URL}/process",
                json={"youtube_url": youtube_url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.job_id = data['job_id']
                st.success(f"✅ Processing started! Job ID: {data['job_id']}")
            else:
                st.error(f"❌ Error: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error: Make sure the FastAPI server is running on http://localhost:8000")
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout: Server is taking too long to respond")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

# Show progress if job is active
if st.session_state.job_id and st.session_state.tutorial_data is None:
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Poll for status
    max_polls = 300  # 10 minutes max (300 * 2 seconds)
    poll_count = 0
    
    while poll_count < max_polls:
        try:
            response = requests.get(
                f"{API_URL}/status/{st.session_state.job_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data['status']
                progress = status_data.get('progress', 0)
                
                # Update progress bar
                progress_placeholder.progress(progress / 100)
                
                # Update status message
                status_messages = {
                    'downloading': '📥 Downloading video...',
                    'loading_model': '🤖 Loading AI models...',
                    'transcribing': '🎤 Transcribing audio...',
                    'extracting_frames': '🎬 Extracting video frames...',
                    'structuring_tutorial': '📝 Structuring tutorial with GPT...',
                    'matching_frames': '🖼️ Matching frames to steps with AI...',
                    'completed': '✅ Tutorial ready!',
                    'error': '❌ Error occurred'
                }
                
                status_placeholder.info(status_messages.get(status, status))
                
                if status == 'completed':
                    # Fetch tutorial data
                    tutorial_response = requests.get(
                        f"{API_URL}/tutorial-data/{st.session_state.job_id}",
                        timeout=10
                    )
                    
                    if tutorial_response.status_code == 200:
                        st.session_state.tutorial_data = tutorial_response.json()
                        progress_placeholder.empty()
                        status_placeholder.empty()
                        st.success("✅ Tutorial generated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to fetch tutorial data")
                    break
                
                elif status == 'error':
                    st.error(f"Error: {status_data.get('message', 'Unknown error')}")
                    st.session_state.job_id = None
                    break
                
                time.sleep(2)  # Poll every 2 seconds
                poll_count += 1
            else:
                st.error("Failed to get status")
                break
                
        except requests.exceptions.Timeout:
            st.warning("Status check timeout, retrying...")
            poll_count += 1
            time.sleep(2)
        except Exception as e:
            st.error(f"Error checking status: {str(e)}")
            break
    
    if poll_count >= max_polls:
        st.error("Processing timeout - please try again with a shorter video")
        st.session_state.job_id = None

# Display tutorial
if st.session_state.tutorial_data:
    tutorial = st.session_state.tutorial_data
    
    # Header
    st.markdown("---")
    st.markdown(f"## 📚 {tutorial['title']}")
    
    # Download PDF section
    st.markdown("### 📥 Download Tutorial")
    
    # Check if we need to load PDF data
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Generate PDF", key="gen_pdf_btn"):
            with st.spinner("Generating PDF... This may take a moment (30-60 seconds)"):
                try:
                    # Make request with longer timeout
                    pdf_response = requests.get(
                        f"{API_URL}/download-pdf/{st.session_state.job_id}",
                        timeout=120,  # 2 minutes timeout for PDF generation
                    )
                    
                    if pdf_response.status_code == 200:
                        st.session_state.pdf_data = pdf_response.content
                        st.success("✅ PDF generated successfully!")
                        st.rerun()
                    elif pdf_response.status_code == 500:
                        try:
                            error_detail = pdf_response.json().get('detail', 'Unknown error')
                        except:
                            error_detail = pdf_response.text
                        if 'wkhtmltopdf' in error_detail:
                            st.error("❌ PDF generation failed: wkhtmltopdf is not installed")
                            st.info("Please install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")
                        else:
                            st.error(f"❌ PDF generation failed: {error_detail}")
                    else:
                        st.error(f"❌ Failed to generate PDF (Status: {pdf_response.status_code})")
                        
                except requests.exceptions.Timeout:
                    st.error("❌ PDF generation timeout - the video may be too long or server is busy")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Connection error - make sure the server is running")
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col2:
        if st.session_state.pdf_data is not None:
            st.download_button(
                label="⬇️ Download PDF File",
                data=st.session_state.pdf_data,
                file_name=f"tutorial_{st.session_state.job_id}.pdf",
                mime="application/pdf",
                key="download_pdf_final"
            )
    
    # Introduction
    st.markdown("### 📖 Introduction")
    with st.container():
        st.markdown(f"""
        <div class="content-box">
            {tutorial['introduction']}
        </div>
        """, unsafe_allow_html=True)
    
    # Steps
    st.markdown("### 📋 Tutorial Steps")
    
    for step in tutorial['steps']:
        with st.container():
            # Step header
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                st.markdown(f"""
                <div class="step-number">{step['step_number']}</div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"### {step['title']}")
            
            # Step explanation
            st.markdown(f"""
            <div class="content-box">
                {step['explanation']}
            </div>
            """, unsafe_allow_html=True)
            
            # Step image - Get from API endpoint
            try:
                filename = os.path.basename(step['frame'])
                image_url = f"{API_URL}/image/{st.session_state.job_id}/{filename}"
                
                # Try to fetch and display the image
                img_response = requests.get(image_url, timeout=10)
                if img_response.status_code == 200:
                    st.image(
                        img_response.content,
                        caption=f"⏱️ Timestamp: {step['timestamp']:.2f}s",
                        use_column_width=True
                    )
                else:
                    st.warning(f"⚠️ Image not available (Status: {img_response.status_code})")
            except Exception as e:
                st.error(f"❌ Error loading image: {str(e)}")
            
            # Video timestamp link
            if st.session_state.youtube_url:
                timestamp_url = f"{st.session_state.youtube_url}&t={int(step['timestamp'])}s"
                st.markdown(f"[▶️ Jump to this step in video]({timestamp_url})")
            
            st.markdown("---")
    
    # Reset button
    if st.button("🔄 Convert Another Video"):
        st.session_state.job_id = None
        st.session_state.tutorial_data = None
        st.session_state.youtube_url = None
        st.session_state.pdf_generated = False
        st.rerun()

# Sidebar info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    This tool uses AI to:
    1. 📥 Download YouTube videos
    2. 🎤 Transcribe audio using Whisper
    3. 📝 Structure content using GPT-4o-mini
    4. 🖼️ Select relevant frames with AI vision
    5. 📚 Generate beautiful PDF tutorials
    """)
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Use educational/tutorial videos
    - Videos under 30 mins work best
    - Clear audio improves results
    - PDF downloads include all images
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Made by using FastAPI, Streamlit, and OpenAI GPT-4o-mini
</div>
""", unsafe_allow_html=True)