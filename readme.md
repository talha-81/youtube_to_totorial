# 🎥 YouTube to Tutorial Converter

Transform any YouTube video into a structured, AI-powered tutorial with step-by-step instructions and perfectly matched images.

## ✨ Features

- **🤖 AI-Powered Structure**: Uses GPT-4o-mini to automatically structure content into introduction and logical steps
- **🎯 Smart Frame Selection**: AI vision selects the most relevant frame for each tutorial step
- **📝 Professional Format**: Beautiful HTML output with step numbers, explanations, and timestamps
- **⚡ Real-time Progress**: Live updates on processing status
- **🎨 Modern UI**: Clean Streamlit interface for easy video conversion

## 🛠️ Technology Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **AI Models**: 
  - OpenAI GPT-4o-mini (tutorial structuring & frame selection)
  - OpenAI Whisper (audio transcription)
- **Video Processing**: yt-dlp, OpenCV

## 📋 Prerequisites

1. Python 3.8+
2. ffmpeg (for video processing)
3. OpenAI API key

### Installing ffmpeg

**Windows:**
```bash
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Installation

1. **Clone or create project directory**
```bash
mkdir youtube-tutorial-converter
cd youtube-tutorial-converter
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

## 🎯 Usage

### 1. Start the FastAPI Backend

```bash
python app.py
```

The API will run on `http://localhost:8000`

### 2. Start the Streamlit Frontend

In a new terminal:

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### 3. Convert a Video

1. Paste a YouTube URL in the input field
2. Click "Convert to Tutorial"
3. Wait for processing (progress bar shows status)
4. View the generated tutorial in the browser
5. Download the HTML file for offline use

## 🔧 How It Works

1. **Download**: Video is downloaded from YouTube using yt-dlp
2. **Transcribe**: Audio is transcribed using OpenAI Whisper
3. **Extract Frames**: Video frames are extracted at regular intervals
4. **Structure with AI**: GPT-4o-mini analyzes the transcript and creates a structured tutorial with:
   - Introduction
   - Multiple numbered steps with titles and explanations
5. **Match Frames**: GPT-4o-mini vision analyzes frames and selects the best image for each step
6. **Generate HTML**: Beautiful tutorial HTML is created with all content

## 🎨 Output Format

The generated tutorial includes:

- **Title**: Auto-generated from video content
- **Introduction**: Overview of what the tutorial covers
- **Steps**: Each with:
  - Step number (visual badge)
  - Step title
  - Detailed explanation
  - Relevant image from video
  - Timestamp with link back to original video

## ⚙️ Configuration

You can adjust these parameters in `main.py`:

```python
# Frame extraction interval (seconds)
frame_interval = 10  # Extract frame every 10 seconds

# Whisper model size
whisper_model = "base"  # Options: tiny, base, small, medium, large
```

## 🐛 Troubleshooting

### "Connection refused" error
- Make sure FastAPI backend is running on port 8000
- Check if another service is using port 8000

### "OpenAI API error"
- Verify your API key in .env file
- Check your OpenAI account has credits

### "ffmpeg not found"
- Install ffmpeg using instructions above
- Restart terminal after installation

### Frames not loading in tutorial
- Images use absolute file paths
- Open HTML file from the jobs/{job_id}/output/ directory
- Or use the "View Tutorial" button in Streamlit

## 💡 Tips for Best Results

- ✅ Use educational or tutorial videos (5-30 minutes ideal)
- ✅ Videos with clear audio work best
- ✅ Content with distinct visual steps produces better tutorials
- ❌ Avoid videos with poor audio quality
- ❌ Very long videos (60+ min) may take significant time

## 📊 API Endpoints

### POST `/process`
Start video processing
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=..."
}
```

### GET `/status/{job_id}`
Check processing status

### GET `/tutorial/{job_id}`
Get tutorial HTML

### GET `/tutorial-data/{job_id}`
Get tutorial data as JSON

## 🔐 Privacy & Data

- Videos are temporarily downloaded and processed locally
- Transcripts are sent to OpenAI for structuring
- Video frames are sent to OpenAI vision API for selection
- All data remains on your machine except API calls
- Jobs folder can be cleared periodically to free space

## 📄 License

This project uses several open-source libraries. Make sure to comply with YouTube's Terms of Service when downloading videos.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini and Whisper
- Streamlit for the amazing UI framework
- FastAPI for the modern API framework
- yt-dlp for reliable YouTube downloads

---
