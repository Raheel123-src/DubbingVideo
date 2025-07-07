# NewDubber 🎬

A powerful AI-powered video dubbing application that automatically transcribes, translates, and dubs videos into multiple languages using cutting-edge AI technologies.

## 🌟 Features

-   **Automatic Speech Recognition**: Uses OpenAI Whisper for accurate audio transcription
-   **AI Translation**: Leverages GPT-3.5-turbo for natural, modern translations
-   **Text-to-Speech**: Integrates ElevenLabs for high-quality voice synthesis
-   **Video Processing**: FFmpeg-powered video manipulation and audio replacement
-   **Cloud Deployment**: Ready for Modal cloud deployment with S3 storage
-   **Multi-language Support**: Supports various languages with modern, conversational translations
-   **Hinglish Support**: Special handling for Hindi translations using Hinglish (Hindi + English mix)

## 🏗️ Architecture

The project consists of two main components:

### 1. Local Development (`dubber.py`)

-   FastAPI application for local testing and development
-   Returns local file paths for all generated files
-   Perfect for development and testing without cloud dependencies

### 2. Cloud Deployment (`modal_app.py`)

-   Modal-optimized version for production deployment
-   Automatically uploads final dubbed videos to AWS S3
-   Returns S3 URLs instead of local file paths
-   Includes comprehensive error handling and logging

## 🔧 Technology Stack

-   **Backend Framework**: FastAPI
-   **Speech Recognition**: OpenAI Whisper
-   **Translation**: OpenAI GPT-3.5-turbo
-   **Text-to-Speech**: ElevenLabs API
-   **Video Processing**: FFmpeg
-   **Cloud Platform**: Modal
-   **Storage**: AWS S3 (production)
-   **Language**: Python 3.11+

## 📋 Prerequisites

-   Python 3.11 or higher
-   FFmpeg installed on your system
-   API keys for:
    -   OpenAI API
    -   ElevenLabs API
    -   AWS S3 (for production deployment)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Raheel123-src/DubbingVideo.git
cd DubbingVideo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
VOICE_ID=your_voice_id_here

# AWS S3 Configuration (for production deployment)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```

## 🎯 Usage

### Local Development

1. **Start the local server:**

```bash
uvicorn dubber:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the API:**
    - Health check: `GET http://localhost:8000/`
    - API documentation: `http://localhost:8000/docs`

### Production Deployment

1. **Install Modal CLI:**

```bash
pip install modal
```

2. **Authenticate with Modal:**

```bash
modal token new
```

3. **Set up Modal secrets:**

```bash
modal secret create newdubber-env --from-dotenv .env
```

4. **Deploy to Modal:**

```bash
modal deploy modal_app.py
```

## 📡 API Endpoints

### Health Check

```http
GET /
```

**Response:**

```json
{
    "message": "NewDubber API is running! Use POST /transcribe-dub/ to process videos."
}
```

### Video Dubbing

```http
POST /transcribe-dub/
```

**Request:**

-   **Content-Type**: `multipart/form-data`
-   **Parameters**:
    -   `video`: Video file (MP4, AVI, MOV, etc.)
    -   `lang`: Target language (e.g., "hindi", "spanish", "french", "german")

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/transcribe-dub/" \
  -H "Content-Type: multipart/form-data" \
  -F "video=@your_video.mp4" \
  -F "lang=hindi"
```

**Local Development Response:**

```json
{
    "original_video_file": "uploads/original_uuid.mp4",
    "dubbed_audio_file": "uploads/audio_uuid.mp3",
    "final_dubbed_video_file": "uploads/final_vid_uuid.mp4",
    "original_transcript_file": "uploads/original_uuid.txt",
    "translated_transcript_file": "uploads/translated_uuid.txt",
    "language": "hindi"
}
```

**Production Response (Modal deployment):**

```json
{
    "success": true,
    "s3_url": "https://your-bucket.s3.us-east-1.amazonaws.com/dubbed_videos/uuid_final_dubbed.mp4",
    "session_id": "uuid-session-id",
    "language": "hindi",
    "message": "Video successfully dubbed and uploaded to S3"
}
```

## 🔄 Processing Pipeline

1. **Video Upload**: Accepts video file via multipart form data
2. **Audio Extraction**: Extracts audio from video using FFmpeg
3. **Speech Recognition**: Transcribes audio using OpenAI Whisper
4. **Translation**: Translates transcript using GPT-3.5-turbo
5. **Text-to-Speech**: Generates dubbed audio using ElevenLabs
6. **Video Synthesis**: Combines original video with dubbed audio
7. **Storage**: Saves files locally (dev) or uploads to S3 (production)

## 🌍 Supported Languages

The application supports translation to various languages with modern, conversational style:

-   **Hindi**: Uses Hinglish (Hindi + English mix) for natural, contemporary speech
-   **Spanish**: Modern Spanish with casual expressions
-   **French**: Contemporary French with current slang
-   **German**: Modern German with trendy expressions
-   **And more**: Any language supported by GPT-3.5-turbo

## 🛠️ Development

### Project Structure

```
NewDubber/
├── dubber.py              # Local development version
├── modal_app.py           # Production deployment version
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment variables (not in repo)
├── .gitignore           # Git ignore rules
└── uploads/             # Local file storage (dev only)
```

### Key Functions

-   `transcribe_audio()`: Speech recognition using Whisper
-   `translate_segments()`: AI-powered translation with modern language
-   `generate_audio_from_text()`: Text-to-speech using ElevenLabs
-   `create_final_dubbed_video()`: Video synthesis with FFmpeg
-   `upload_to_s3()`: Cloud storage integration (production)

## 🔒 Security & Best Practices

-   Environment variables for sensitive API keys
-   Local file cleanup after processing
-   Error handling and validation
-   Secure file upload handling
-   AWS IAM roles for S3 access

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**: Ensure FFmpeg is installed and in your PATH
2. **API key errors**: Verify all API keys are correctly set in `.env`
3. **Memory issues**: Large videos may require more memory in Modal
4. **S3 upload failures**: Check AWS credentials and bucket permissions

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export DEBUG=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:

-   Create an issue on GitHub
-   Check the troubleshooting section
-   Review the API documentation at `/docs`

---

**Made with ❤️ using FastAPI, OpenAI, ElevenLabs, and Modal**
