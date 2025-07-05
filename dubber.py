from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import whisper
import ffmpeg
import os
import uuid
from datetime import timedelta
import requests
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def generate_audio_from_text(text: str, lang: str, session_id: str):
    output_path = os.path.join(UPLOAD_DIR, f"audio_{session_id}.mp3")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v1" if lang != "en" else "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"ElevenLabs API Error {response.status_code}: {response.text}")


def extract_audio(video_path):
    audio_path = f"/tmp/{uuid.uuid4()}.mp3"
    ffmpeg.input(video_path).output(audio_path).run(overwrite_output=True)
    return audio_path


def format_timestamp(seconds: float):
    td = str(timedelta(seconds=int(seconds)))
    return td if '.' in td else td + ".000"


def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, verbose=False)
    return result['segments']


def translate_segments(segments, target_lang):
    translated = []

    for seg in segments:
        prompt = (
            f"Translate the following sentence into {target_lang} using modern, simple, "
            f"and conversational language. Avoid overly formal or harsh words. "
            f"Only return the translated sentence:\n\n\"{seg['text']}\"\n"
        )

        try:
            print(f"[Translating] {seg['text'][:60]}...")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful translator that outputs clear and modern translations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )

            translated_text = response.choices[0].message.content.strip()
            print(f"[✅ Translated] {translated_text}")

            translated.append({
                "start": format_timestamp(seg["start"]),
                "end": format_timestamp(seg["end"]),
                "text": translated_text
            })

        except Exception as e:
            print(f"[❌ Error] {e}")
            translated.append({
                "start": format_timestamp(seg["start"]),
                "end": format_timestamp(seg["end"]),
                "text": "translation failed"
            })

    return translated


def format_segments(segments):
    return [{
        "start": format_timestamp(seg["start"]),
        "end": format_timestamp(seg["end"]),
        "text": seg["text"]
    } for seg in segments]


def save_transcript(file_path, segments):
    with open(file_path, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"[{seg['start']} --> {seg['end']}] {seg['text']}\n")


def create_final_dubbed_video(video_path: str, audio_path: str, session_id: str):
    temp_video_path = os.path.join(UPLOAD_DIR, f"temp_video_{session_id}.mp4")
    output_video_path = os.path.join(UPLOAD_DIR, f"final_vid_{session_id}.mp4")

    ffmpeg.input(video_path).output(temp_video_path, vcodec='copy', an=None).run(overwrite_output=True)
    input_video = ffmpeg.input(temp_video_path)
    input_audio = ffmpeg.input(audio_path)

    (
        ffmpeg
        .output(input_video, input_audio, output_video_path,
                vcodec='copy',
                acodec='aac',
                strict='experimental',
                shortest=None,
                **{'map': '0:v:0', 'map': '1:a:0'})
        .run(overwrite_output=True)
    )

    os.remove(temp_video_path)
    return output_video_path


@app.post("/transcribe-dub/")
async def transcribe_and_translate(
    video: UploadFile = File(...),
    lang: str = Form(...)
):
    try:
        file_ext = os.path.splitext(video.filename)[1]
        session_id = str(uuid.uuid4())
        raw_video_path = os.path.join(UPLOAD_DIR, f"original_{session_id}{file_ext}")
        with open(raw_video_path, "wb") as f:
            f.write(await video.read())

        extracted_audio_path = extract_audio(raw_video_path)
        segments = transcribe_audio(extracted_audio_path)
        os.remove(extracted_audio_path)

        original = format_segments(segments)
        translated = translate_segments(segments, lang)

        if all(seg["text"].lower() == "translation failed" for seg in translated):
            raise Exception("❌ All segments failed translation. Check OpenAI API or rate limits.")

        orig_path = os.path.join(UPLOAD_DIR, f"original_{session_id}.txt")
        trans_path = os.path.join(UPLOAD_DIR, f"translated_{session_id}.txt")
        save_transcript(orig_path, original)
        save_transcript(trans_path, translated)

        translated_text_full = " ".join([seg["text"] for seg in translated])
        dubbed_audio_path = generate_audio_from_text(translated_text_full, lang, session_id)

        final_dubbed_video_path = create_final_dubbed_video(raw_video_path, dubbed_audio_path, session_id)

        return {
            "original_video_file": raw_video_path,
            "dubbed_audio_file": dubbed_audio_path,
            "final_dubbed_video_file": final_dubbed_video_path,
            "original_transcript_file": orig_path,
            "translated_transcript_file": trans_path,
            "language": lang
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
