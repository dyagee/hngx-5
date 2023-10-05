#author: Agee Aondo
#Year: 2023
from sqlalchemy.orm import Session
from models import VideoData, Chunks
import os
import uuid

abs_path = os.getcwd()
chunk_dir = os.path.join(abs_path,"recording/chunks")
os.makedirs(chunk_dir,exist_ok=True)
video_dir = os.path.join(abs_path,"recording/videos")
os.makedirs(video_dir,exist_ok=True)


def create_empty(file_id):
    loc = os.path.join(video_dir,f"recording_{file_id}")
    if os.path.isdir(loc):
        pass
    else:
        os.mkdir(loc)

   
def generate_uuid(db:Session):
    new_id = str(uuid.uuid4())
    # Check if the ID already exists
    check = db.query(VideoData).filter(VideoData.file_id==new_id).first()
    if check is not None:
        # If yes, try again
        return generate_uuid(db=db)
    else:
        # If no, return the ID
        return new_id

def get_chunk_progress(db:Session,file_id:str,blob_number:int):
    #check if the chunk have been processed
    progress =  db.query(Chunks).filter(Chunks.file_id==file_id).first()
    process = progress.is_processed
    return process

def set_chunk_progress(db:Session,file_id:str,blob_number:int):
    progress =  db.query(Chunks).filter(Chunks.file_id==file_id,Chunks.blob_number==blob_number).first()
    process = progress.is_processed
    print("chunk process:",process)
    if process == False:
        progress.is_processed = True
        db.commit()
        db.refresh(progress)
        return process
    else:
        pass
def get_chunk_dir(file_id:str):
    dir = os.path.join(chunk_dir, f'chunk_{file_id}')
    os.makedirs(dir,exist_ok=True)
    return dir


def get_video_dir(file_id:str):
    return os.path.join(video_dir, f'recording_{file_id}')



def retrieve_videos(db:Session,file_id:str):
    items = db.query(VideoData).filter(VideoData.file_id==file_id).all()
    return items

def retrieve_video(db:Session,file_id:str,file_name:str):
    items = db.query(VideoData).filter(VideoData.file_id==file_id,file_name==file_name).first()
    return items