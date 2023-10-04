import time
import openai
from models import VideoData, Chunks
from sqlalchemy.orm import Session
from blob_services import combine_chunks


def transcribe_video(file_id:str,db:Session):
    video_item = db.query(VideoData).filter(VideoData.file_id==file_id).first()
    if video_item is None:
        return None

    # Simulate transcription process
    video_file = combine_chunks(file_id)
    transcript = openai.Audio.transcribe('whisper-1', open(video_file, 'rb'))
    time.sleep(10)  # Simulate a 10-second transcription

    video_item.transcript = transcript.get('text', '')
    video_item.status = True
    video_item.transcribed = True
    db.commit()
    db.refresh(video_item)