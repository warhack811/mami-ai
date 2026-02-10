import os
from groq import Groq
from app.core.config import settings

client = None

if settings.GROQ_API_KEY:
    client = Groq(api_key=settings.GROQ_API_KEY)

async def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio file using Groq Whisper.
    """
    if not client:
        return "Voice service not configured (Missing GROQ_API_KEY)."

    try:
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                language="en",
                temperature=0.0
            )
        return transcription.text
    except Exception as e:
        print(f"Transcription error: {e}")
        return f"Error processing audio: {str(e)}"
