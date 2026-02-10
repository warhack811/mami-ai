from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from app.services.voice import transcribe_audio

router = APIRouter()

@router.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Upload an audio file (wav/mp3) and get transcription.
    """
    try:
        # Save temporary file
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call Whisper Service
        transcription = await transcribe_audio(temp_file)

        # Cleanup
        os.remove(temp_file)

        return {"text": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
