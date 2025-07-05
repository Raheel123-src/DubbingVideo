# NewDubber Modal Deployment Guide

This guide will help you deploy the NewDubber application on Modal.

## Prerequisites

1. **Modal CLI installed**: `pip install modal`
2. **Modal account**: Sign up at [modal.com](https://modal.com)
3. **API Keys**:
    - ElevenLabs API key
    - OpenAI API key
    - Voice ID from ElevenLabs

## Setup Steps

### 1. Install Modal CLI

```bash
pip install modal
```

### 2. Authenticate with Modal

```bash
modal token new
```

### 3. Set Environment Variables

Create a `.env` file in your project root with your API keys:

```bash
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
VOICE_ID=your_voice_id_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Deploy to Modal

```bash
modal deploy modal_app.py
```

### 5. Set Environment Variables in Modal

After deployment, set your environment variables in Modal:

```bash
modal secret create newdubber-env ELEVENLABS_API_KEY=your_key VOICE_ID=your_voice_id OPENAI_API_KEY=your_key
```

### 6. Update the deployment to use secrets

Edit `modal_app.py` to include the secret:

```python
@stub.function(image=image, timeout=300, secrets=[modal.Secret.from_name("newdubber-env")])
@modal.asgi_app()
def fastapi_app():
    return web_app
```

### 7. Redeploy with secrets

```bash
modal deploy modal_app.py
```

## Usage

Once deployed, your API will be available at the URL provided by Modal. You can:

1. **Test the API**: Visit the root endpoint `/` to see if it's running
2. **Process videos**: Send POST requests to `/transcribe-dub/` with:
    - `video`: Video file (multipart/form-data)
    - `lang`: Target language (e.g., "Spanish", "French", "German")

## API Endpoints

-   `GET /`: Health check
-   `POST /transcribe-dub/`: Process video for dubbing

## Troubleshooting

1. **Timeout issues**: The app is configured with a 5-minute timeout. For longer videos, increase the timeout in the decorator.
2. **Memory issues**: For large video files, consider increasing the memory allocation in Modal.
3. **API key errors**: Ensure all environment variables are properly set in Modal secrets.

## Cost Optimization

-   The app uses Modal's pay-per-use model
-   Consider setting up auto-scaling rules for production use
-   Monitor usage in the Modal dashboard
