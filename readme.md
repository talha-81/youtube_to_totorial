# 🎥 YouTube to Tutorial Converter

Transform any YouTube video into a structured, AI-powered tutorial with step-by-step instructions and perfectly matched images. Automatically generates professional PDF documents with embedded images.

## ✨ Features

- **🤖 AI-Powered Structure**: Uses GPT-4o-mini to automatically structure content into introduction and logical steps
- **🎯 Smart Frame Selection**: AI vision selects the most relevant frame for each tutorial step
- **📄 PDF Export**: Generate beautiful, shareable PDF tutorials with all images embedded
- **📝 Professional Format**: Numbered steps with explanations, images, and video timestamps
- **⚡ Real-time Progress**: Live updates on processing status with detailed milestones
- **🎨 Modern UI**: Clean Streamlit interface for easy video conversion
- **🖼️ Live Preview**: View tutorial in frontend before downloading
- **🔗 Video Links**: Jump to specific timestamps in original YouTube video

## 🛠️ Technology Stack

- **Backend**: FastAPI (REST API)
- **Frontend**: Streamlit (Web UI)
- **AI Models**: 
  - OpenAI GPT-4o-mini (tutorial structuring & frame selection)
  - OpenAI Whisper (audio transcription)
- **PDF Generation**: pdfkit + wkhtmltopdf
- **Video Processing**: yt-dlp, OpenCV, NumPy
- **Image Processing**: Pillow, base64 encoding

## 📋 Prerequisites

1. **Python 3.8+**
2. **System Dependencies**:
   - ffmpeg (video processing)
   - wkhtmltopdf (PDF generation)
3. **OpenAI API Key** (free trial or paid account)

### Installing ffmpeg

**Windows:**
```bash
choco install ffmpeg
```

Or download from: https://ffmpeg.org/download.html

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Installing wkhtmltopdf

**Windows:**
- Download from: https://wkhtmltopdf.org/downloads.html
- Run installer (default paths supported: `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`)

**macOS:**
```bash
brew install --cask wkhtmltopdf
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install wkhtmltopdf
```

**Verify Installation:**
```bash
wkhtmltopdf --version
```

## 🚀 Installation & Setup

### 1. Clone or Create Project Directory

```bash
mkdir youtube-tutorial-converter
cd youtube-tutorial-converter
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

Create a `.env` file in the backend directory:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

## 🎯 Running the Application

### Terminal 1: Start FastAPI Backend

```bash
cd backend
python app.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2: Start Streamlit Frontend

```bash
cd frontend
streamlit run app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 3. Access the Application

Open your browser to: **http://localhost:8501**

## 📖 Usage Guide

### Step 1: Paste YouTube URL
- Copy any YouTube video URL
- Paste it in the "Enter YouTube URL" field
- Example: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

### Step 2: Convert to Tutorial
- Click the "🚀 Convert to Tutorial" button
- Watch real-time progress:
  - 📥 Downloading video
  - 🤖 Loading AI models
  - 🎤 Transcribing audio
  - 🎬 Extracting frames
  - 📝 Structuring with GPT
  - 🖼️ Matching frames to steps

### Step 3: View Tutorial
- Once complete, the tutorial appears in the browser
- Each step shows:
  - Step number (badge)
  - Step title
  - Detailed explanation
  - Relevant screenshot
  - Video timestamp with link

### Step 4: Download PDF
- Click "📥 Download PDF" button
- Professional PDF generates with:
  - Title page with gradient header
  - Introduction section
  - All steps with embedded images
  - Timestamps for each step
  - Professional formatting

### Step 5: Share or Archive
- Save the PDF locally
- Share with colleagues or students
- Archive for offline access
- Print for physical distribution

## 🔧 How It Works

```
YouTube Video
    ↓
[Download] via yt-dlp
    ↓
[Transcribe] via Whisper
    ↓
[Extract Frames] via OpenCV (every 10 seconds)
    ↓
[Structure] via GPT-4o-mini
    ├─ Title
    ├─ Introduction
    └─ Steps (numbered with explanations)
    ↓
[Match Frames] via GPT-4o-mini Vision
    └─ Select best image for each step
    ↓
[Generate Output]
    ├─ HTML (for preview)
    ├─ JSON (data format)
    └─ PDF (for download)
```

## 📊 Output Examples

### Generated Tutorial Contains:

**Title**: Automatically generated from video content
```
"Three-Star Strategy for Town Hall 17 Challenge"
```

**Introduction**: Overview from transcript
```
"This tutorial provides a comprehensive strategy to achieve a three-star victory..."
```

**Steps**: Numbered with titles and explanations
```
Step 1: Preparation and Setup
Step 2: Deploying Initial Troops
Step 3: Further Troop Deployment
...
```

**Images**: Automatically selected best frames
- One relevant image per step
- Embedded in PDF (no broken links)
- Displayed in web preview

**Timestamps**: Links back to video
```
⏱️ Timestamp: 10.00s [Jump to video]
```

## ⚙️ Configuration

### Adjust Processing Parameters

Edit in backend `app.py`:

```python
# Frame extraction interval (seconds)
frame_interval = 10  # Extract frame every 10 seconds

# Whisper model size (tiny, base, small, medium, large)
whisper_model = "base"  # Larger = more accurate but slower

# GPT model for structuring
model = "gpt-4o-mini"  # Latest and most efficient
```

### Adjust Output Quality

For PDF in `generate_pdf_html()`:

```python
options = {
    'dpi': 300,  # Higher = better quality but larger file
    'page-size': 'A4',
    'margin-top': '1.5cm',
    # ... other options
}
```

## 🎨 Output Files Structure

```
jobs/
└── {job_id}/
    ├── downloaded_video.mp4          # Original YouTube video
    ├── transcription_result.json     # Whisper transcription
    ├── frames/
    │   ├── frame_0.00.jpg
    │   ├── frame_10.00.jpg
    │   ├── frame_20.00.jpg
    │   └── ...
    └── output/
        ├── tutorial.html             # HTML preview
        └── tutorial.pdf              # Download this!
```

## 🔒 Caching & Performance

- **Transcriptions**: Cached (reuse if same video)
- **Frames**: Extracted once and stored
- **API Calls**: Only for GPT processing (per video)
- **Processing Time**: 5-15 minutes depending on video length

## 💾 Storage Management

### Clear Old Jobs

```bash
# Remove old job folders to free disk space
rm -rf jobs/old_job_id_1
rm -rf jobs/old_job_id_2
```

### Job Size Reference

- 10-minute video:
  - Downloaded video: ~50-150MB
  - Frames (10s interval): ~20-40MB
  - Total: ~100-200MB

## 🐛 Troubleshooting

### Error: "Connection refused"
```bash
✗ FastAPI backend not running
✓ Solution: Start backend first: python app.py
```

### Error: "OPENAI_API_KEY not found"
```bash
✗ .env file missing or key not set
✓ Solution: Create .env with valid API key
```

### Error: "wkhtmltopdf not found"
```bash
✗ PDF tool not installed
✓ Solution: Install from https://wkhtmltopdf.org/downloads.html
```

### Error: "Failed to download video"
```bash
✗ YouTube blocked the download
✓ Solution: 
  - Update yt-dlp: pip install --upgrade yt-dlp
  - Try different video or use VPN
```

### Images Not Loading in Frontend
```bash
✗ Old Streamlit version or parameter issue
✓ Solution: Update Streamlit: pip install --upgrade streamlit
```

### PDF Download Returns "File wasn't available"
```bash
✗ PDF generation failed or file path issue
✓ Solution: Check backend logs for errors, restart server
```

## 💡 Tips for Best Results

### ✅ DO:
- Use educational/tutorial videos (5-30 minutes)
- Choose videos with clear audio
- Pick content with distinct visual steps
- Convert one video at a time
- Check PDF before sharing

### ❌ DON'T:
- Use videos with poor audio quality
- Try 60+ minute videos (very slow)
- Process multiple videos simultaneously
- Close browser before download completes
- Delete jobs folder while processing

## 📊 API Reference

### POST `/process`
Start video processing
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=..."
}
```
Returns: `{"job_id": "uuid", "message": "Processing started"}`

### GET `/status/{job_id}`
Check processing status
Returns:
```json
{
  "status": "completed",
  "progress": 100,
  "tutorial_data": {...},
  "job_dir": "..."
}
```

### GET `/tutorial/{job_id}`
Get HTML preview
Returns: HTML content with styling

### GET `/tutorial-data/{job_id}`
Get structured data
Returns: JSON with title, introduction, steps

### GET `/image/{job_id}/{filename}`
Get image file
Returns: JPEG image

### GET `/download-pdf/{job_id}`
Generate and download PDF
Returns: PDF file for download

## 🔐 Privacy & Data

- ✅ Videos processed locally on your machine
- ✅ Transcripts sent to OpenAI (encrypted)
- ✅ Frames sent to OpenAI Vision (encrypted)
- ✅ No data stored on OpenAI servers long-term
- ✅ Generated files stay in your `jobs/` folder
- 📌 Review OpenAI's privacy policy: https://openai.com/privacy

## 📄 Requirements

See `requirements.txt`:

```
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.1
yt-dlp==2023.12.30
openai==1.3.9+
python-dotenv==1.0.0
opencv-python==4.8.1.78
numpy==1.24.3
pdfkit==1.0.0
requests==2.31.0
pydantic==2.5.0
whisper-openai==20231117
```

## 📝 Example Workflow

```
1. Find tutorial video on YouTube
   → https://www.youtube.com/watch?v=u4rsmfJov0E

2. Paste URL in app
   → "Enter YouTube URL"

3. Click Convert
   → Wait for processing (progress shows status)

4. View tutorial
   → See all steps with images in browser

5. Download PDF
   → Click "📥 Download PDF"

6. Share PDF
   → Send to colleagues, students, or archive
```

## 🚀 Performance Benchmarks

| Video Length | Processing Time | File Size |
|-------------|-----------------|-----------|
| 5 minutes   | 3-5 min         | ~50MB     |
| 10 minutes  | 5-10 min        | ~100MB    |
| 20 minutes  | 10-15 min       | ~200MB    |
| 30 minutes  | 15-20 min       | ~300MB    |

*Times vary based on internet speed and system specs*

## 🤝 Contributing

Found a bug or have a feature request?
- Report issues in the GitHub repository
- Submit pull requests with improvements
- Share feedback and suggestions

## 📧 Support

For issues with:
- **YouTube Downloads**: Check yt-dlp documentation
- **OpenAI API**: Check OpenAI docs at https://platform.openai.com/docs
- **PDF Generation**: Check wkhtmltopdf documentation
- **Streamlit**: Check Streamlit docs at https://docs.streamlit.io

## 📄 License

This project uses several open-source libraries:
- FastAPI (MIT License)
- Streamlit (Apache 2.0)
- OpenCV (Apache 2.0)
- yt-dlp (Unlicense)

**Important**: Respect YouTube's Terms of Service when downloading videos.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini and Whisper
- **Streamlit** for the amazing UI framework
- **FastAPI** for the modern async framework
- **yt-dlp** for reliable YouTube downloads
- **wkhtmltopdf** for PDF generation
- **OpenCV** for video frame extraction

---

### 📌 Quick Start Command

```bash
# Backend
python app.py

# Frontend (new terminal)
streamlit run app.py

# Open browser
http://localhost:8501
```

**Enjoy creating professional tutorials! 🎉**