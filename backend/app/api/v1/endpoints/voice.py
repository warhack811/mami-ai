from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import tempfile
# from app.services.voice import transcribe_audio # Placeholder import

router = APIRouter()

@router.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Upload an audio file (wav/mp3) and get transcription.
    """
    temp_file_path = None
    try:
        # Save temporary file securely
        suffix = os.path.splitext(file.filename)[1] if file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as buffer:
            temp_file_path = buffer.name
            shutil.copyfileobj(file.file, buffer)

        # Call Whisper Service (Placeholder)
        # transcription = transcribe_audio(temp_file_path)
        transcription = "This is a simulated transcription of the uploaded audio file."

        return {"text": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
