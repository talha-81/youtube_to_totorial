import os
import yt_dlp
import whisper
import cv2
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from openai import OpenAI
from dotenv import load_dotenv
import base64
from pathlib import Path
import uuid

load_dotenv()

app = FastAPI()

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store processing status
processing_status = {}

class VideoRequest(BaseModel):
    youtube_url: str

class YouTubeVideoProcessor:
    def __init__(self, youtube_url, job_id):
        self.job_id = job_id
        self.youtube_url = youtube_url
        self.job_dir = f"jobs/{job_id}"
        os.makedirs(f'{self.job_dir}/frames', exist_ok=True)
        os.makedirs(f'{self.job_dir}/output', exist_ok=True)
        
        processing_status[job_id] = {"status": "downloading", "progress": 0}
        self.video_path = self._download_video(youtube_url)
        
        processing_status[job_id] = {"status": "loading_model", "progress": 20}
        self.whisper_model = whisper.load_model("base")

    def _download_video(self, video_url):
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{self.job_dir}/downloaded_video.%(ext)s',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(video_url, download=False)
                video_title = info_dict.get('title', 'Unknown Title')
                video_extension = info_dict.get('ext', 'mp4')
                output_file_path = f"{self.job_dir}/downloaded_video.{video_extension}"

                self.yt_title = video_title
                video_path = os.path.abspath(output_file_path)
                
                if not os.path.exists(video_path):
                    ydl.download([video_url])
                
                return video_path
            except Exception as e:
                processing_status[self.job_id] = {"status": "error", "message": str(e)}
                raise Exception(f"Error downloading video: {str(e)}")

    def extract_text_and_frames(self, frame_interval=10):
        transcription_file_path = f'{self.job_dir}/transcription_result.json'

        if os.path.exists(transcription_file_path):
            with open(transcription_file_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
        else:
            processing_status[self.job_id] = {"status": "transcribing", "progress": 40}
            result = self.whisper_model.transcribe(self.video_path)
            with open(transcription_file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

        # Extract ALL frames at intervals
        processing_status[self.job_id] = {"status": "extracting_frames", "progress": 60}
        all_frames = self._extract_all_frames(frame_interval)
        
        # Get full transcript
        full_transcript = " ".join([seg['text'] for seg in result['segments']])
        
        # Use GPT to structure the tutorial
        processing_status[self.job_id] = {"status": "structuring_tutorial", "progress": 70}
        tutorial_structure = self._structure_tutorial_with_gpt(full_transcript)
        
        # Match frames to steps using GPT-4o-mini
        processing_status[self.job_id] = {"status": "matching_frames", "progress": 85}
        tutorial_with_frames = self._match_frames_to_steps(tutorial_structure, all_frames, result['segments'])
        
        processing_status[self.job_id] = {"status": "completed", "progress": 100}
        return tutorial_with_frames

    def _extract_all_frames(self, interval):
        """Extract frames at regular intervals"""
        video = cv2.VideoCapture(self.video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        
        frames_data = []
        for t in np.arange(0, duration, interval):
            video.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ret, frame = video.read()
            if ret:
                frame_path = f'{self.job_dir}/frames/frame_{t:.2f}.jpg'
                cv2.imwrite(frame_path, frame)
                
                # Encode frame to base64 for GPT-4o-mini
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                frames_data.append({
                    'timestamp': t,
                    'path': frame_path,
                    'base64': frame_base64
                })
        
        video.release()
        return frames_data

    def _structure_tutorial_with_gpt(self, transcript):
        """Use GPT to structure the transcript into tutorial format"""
        prompt = f"""You are a tutorial creator. Convert the following video transcript into a well-structured tutorial format.

Structure it as:
1. Introduction (brief overview)
2. Multiple steps (as many as needed based on content)
   - Each step should have a title and detailed explanation
   - Steps should be logical and sequential

Transcript:
{transcript}

Return ONLY a JSON object with this structure:
{{
    "title": "Tutorial title",
    "introduction": "Introduction text",
    "steps": [
        {{"step_number": 1, "title": "Step title", "explanation": "Detailed explanation"}},
        ...
    ]
}}"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a tutorial structuring expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error structuring tutorial: {e}")
            return {
                "title": "Video Tutorial",
                "introduction": transcript[:500],
                "steps": [{"step_number": 1, "title": "Content", "explanation": transcript}]
            }

    def _match_frames_to_steps(self, tutorial_structure, frames_data, segments):
        """Use GPT-4o-mini vision to select best frame for each step"""
        steps_with_frames = []
        
        for step in tutorial_structure['steps']:
            # Select 5-8 candidate frames (evenly distributed)
            num_candidates = min(8, len(frames_data))
            step_index = step['step_number'] - 1
            total_steps = len(tutorial_structure['steps'])
            
            # Calculate time range for this step
            start_idx = int((step_index / total_steps) * len(frames_data))
            end_idx = int(((step_index + 1) / total_steps) * len(frames_data))
            candidate_frames = frames_data[start_idx:end_idx:max(1, (end_idx-start_idx)//num_candidates)]
            
            if not candidate_frames:
                candidate_frames = frames_data[:1]
            
            # Use GPT-4o-mini vision to select best frame
            best_frame = self._select_best_frame_with_gpt(step, candidate_frames)
            
            steps_with_frames.append({
                **step,
                'frame': best_frame['path'],
                'timestamp': best_frame['timestamp']
            })
        
        return {
            **tutorial_structure,
            'steps': steps_with_frames
        }

    def _select_best_frame_with_gpt(self, step, candidate_frames):
        """Use GPT-4o-mini vision to select the most relevant frame"""
        if len(candidate_frames) == 1:
            return candidate_frames[0]
        
        # Prepare message with images
        content = [
            {
                "type": "text",
                "text": f"""Select the frame number (1-{len(candidate_frames)}) that best illustrates this tutorial step:

Step {step['step_number']}: {step['title']}
{step['explanation']}

Respond with ONLY the frame number (1-{len(candidate_frames)}) that best matches this step."""
            }
        ]
        
        # Add images
        for idx, frame in enumerate(candidate_frames, 1):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame['base64']}"
                }
            })
            content.append({
                "type": "text",
                "text": f"Frame {idx}"
            })
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": content}
                ],
                max_tokens=10,
                temperature=0.3
            )
            
            # Extract frame number from response
            response_text = response.choices[0].message.content.strip()
            frame_num = int(''.join(filter(str.isdigit, response_text)))
            frame_num = max(1, min(frame_num, len(candidate_frames)))
            
            return candidate_frames[frame_num - 1]
        except Exception as e:
            print(f"Error selecting frame with GPT: {e}")
            # Return middle frame as fallback
            return candidate_frames[len(candidate_frames) // 2]

    def generate_html(self, tutorial_data):
        """Generate HTML tutorial"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{tutorial_data['title']}</title>
            <style>
                :root {{
                    --bg-color: #f5f5f5;
                    --card-bg: white;
                    --text-color: #333;
                    --text-secondary: #555;
                    --shadow: rgba(0,0,0,0.1);
                    --timestamp-bg: #f0f0f0;
                    --timestamp-color: #666;
                }}
                
                [data-theme="dark"] {{
                    --bg-color: #1a1a1a;
                    --card-bg: #2d2d2d;
                    --text-color: #e0e0e0;
                    --text-secondary: #b0b0b0;
                    --shadow: rgba(0,0,0,0.3);
                    --timestamp-bg: #3d3d3d;
                    --timestamp-color: #a0a0a0;
                }}
                
                * {{
                    transition: background-color 0.3s ease, color 0.3s ease;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 40px 20px;
                    background-color: var(--bg-color);
                    line-height: 1.6;
                    color: var(--text-color);
                }}
                
                .theme-toggle {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 1em;
                    font-weight: bold;
                    box-shadow: 0 4px 6px var(--shadow);
                    z-index: 1000;
                }}
                
                .theme-toggle:hover {{
                    transform: scale(1.05);
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px var(--shadow);
                }}
                
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 2.5em;
                }}
                
                .intro {{
                    background: var(--card-bg);
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px var(--shadow);
                }}
                
                .intro h2 {{
                    color: #667eea;
                    margin-top: 0;
                }}
                
                .step {{
                    background: var(--card-bg);
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px var(--shadow);
                }}
                
                .step-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                
                .step-number {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5em;
                    font-weight: bold;
                    margin-right: 20px;
                    flex-shrink: 0;
                }}
                
                .step-title {{
                    font-size: 1.8em;
                    color: var(--text-color);
                    margin: 0;
                }}
                
                .step-explanation {{
                    color: var(--text-secondary);
                    margin-bottom: 20px;
                    font-size: 1.1em;
                }}
                
                .step-image {{
                    width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px var(--shadow);
                    margin-top: 20px;
                }}
                
                .timestamp {{
                    display: inline-block;
                    background: var(--timestamp-bg);
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    color: var(--timestamp-color);
                    margin-top: 10px;
                }}
                
                .timestamp a {{
                    color: #667eea;
                    text-decoration: none;
                    margin-left: 10px;
                }}
                
                .timestamp a:hover {{
                    text-decoration: underline;
                }}
                
                .video-link {{
                    color: white;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 10px;
                    padding: 10px 20px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 5px;
                    transition: background 0.3s;
                }}
                
                .video-link:hover {{
                    background: rgba(255,255,255,0.3);
                }}
            </style>
        </head>
        <body>
            <button class="theme-toggle" onclick="toggleTheme()">🌓 Toggle Theme</button>
            
            <div class="header">
                <h1>{tutorial_data['title']}</h1>
                <a href="{self.youtube_url}" class="video-link" target="_blank">🎥 Watch Original Video</a>
            </div>
            
            <div class="intro">
                <h2>📖 Introduction</h2>
                <p>{tutorial_data['introduction']}</p>
            </div>
        """
        
        for step in tutorial_data['steps']:
            html_content += f"""
            <div class="step">
                <div class="step-header">
                    <div class="step-number">{step['step_number']}</div>
                    <h2 class="step-title">{step['title']}</h2>
                </div>
                <div class="step-explanation">
                    {step['explanation']}
                </div>
                <img src="file:///{os.path.abspath(step['frame'])}" alt="Step {step['step_number']}" class="step-image">
                <div class="timestamp">
                    ⏱️ Timestamp: {step['timestamp']:.2f}s 
                    <a href="{self.youtube_url}&t={int(step['timestamp'])}s" target="_blank">Jump to video</a>
                </div>
            </div>
            """
        
        html_content += """
            <script>
                // Check for saved theme preference or default to light mode
                const currentTheme = localStorage.getItem('theme') || 'light';
                document.documentElement.setAttribute('data-theme', currentTheme);
                
                function toggleTheme() {
                    const theme = document.documentElement.getAttribute('data-theme');
                    const newTheme = theme === 'light' ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-theme', newTheme);
                    localStorage.setItem('theme', newTheme);
                }
            </script>
        </body>
        </html>
        """
        
        output_path = f'{self.job_dir}/output/tutorial.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

@app.get("/")
async def root():
    return {"message": "YouTube to Tutorial API - Use POST /process to convert videos"}

@app.post("/process")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """Start video processing"""
    job_id = str(uuid.uuid4())
    
    background_tasks.add_task(process_video_task, request.youtube_url, job_id)
    
    return {"job_id": job_id, "message": "Processing started"}

def process_video_task(youtube_url: str, job_id: str):
    """Background task to process video"""
    try:
        processor = YouTubeVideoProcessor(youtube_url, job_id)
        tutorial_data = processor.extract_text_and_frames()
        html_path = processor.generate_html(tutorial_data)
        
        processing_status[job_id] = {
            "status": "completed",
            "progress": 100,
            "html_path": html_path,
            "tutorial_data": tutorial_data
        }
    except Exception as e:
        processing_status[job_id] = {
            "status": "error",
            "message": str(e),
            "progress": 0
        }

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get processing status"""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return processing_status[job_id]

@app.get("/tutorial/{job_id}")
async def get_tutorial(job_id: str):
    """Get tutorial HTML"""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = processing_status[job_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Tutorial not ready yet")
    
    html_path = status["html_path"]
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)

@app.get("/tutorial-data/{job_id}")
async def get_tutorial_data(job_id: str):
    """Get tutorial data as JSON"""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = processing_status[job_id]
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Tutorial not ready yet")
    
    return JSONResponse(content=status["tutorial_data"])

@app.get("/image/{job_id}/{filename}")
async def get_image(job_id: str, filename: str):
    """Serve image files for display in Streamlit"""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Construct the image path
    image_path = f"jobs/{job_id}/frames/{filename}"
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path, media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)