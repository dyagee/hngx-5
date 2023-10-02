#author: Agee Aondo
#Year: 2023
#import all the required modules
#from markupsafe import escape

from sqlalchemy.orm import Session
from models import VideoData, Chunks, Progress
import os


def create_empty(db:Session,file_name:str, file_id:str, file_type:str, bucket_name:str ):
    
    #create a  folder to save empty video
    loc = os.getcwd()
    if bucket_name is None:
        file_path = os.path.join(loc,file_id)
    else:
        file_path = os.path.join(loc,bucket_name)

    if os.path.isdir(file_path):
        pass
    else:
        os.mkdir(file_path)

    #absolute file path
    file_save = os.path.join(file_path,file_name)

    #create an empty binary file
    f = open(file_save,"wb+")
    f.close()
    video_item = VideoData(file_id=file_id,file_name=file_name,file_type=file_type,bucket_name=bucket_name)
    db.add(video_item)
    db.commit()
    db.refresh(video_item)
    return video_item

def upload_chunk(db:Session, file_id:str,is_last:bool):
    is_processed=True
    chunk_item = Chunks(file_id=file_id,is_last=is_last,is_processed=is_processed)
    db.add(chunk_item)
    db.commit()
    db.refresh(chunk_item)
    response = {
        "id":chunk_item.id,
        "file_id":chunk_item.file_id,
        "is_last":chunk_item.is_last,
        "is_processed":chunk_item.is_processed
    }
    return response

def chunk_progress(db:Session,file_id:str,blob_number:int):
    progress =  db.query(Chunks).filter(Chunks.file_id==file_id).first()
    process = progress.is_processed
    return process

def video_progress(db:Session,file_id:str):
    progress =  db.query(Progress).filter(Progress.file_id==file_id).first()
    process = progress.is_processed
    return process


def retrieve_video(db:Session,file_id:str,file_name:str):
    item = db.query(VideoData).filter(VideoData.file_id==file_id,VideoData.file_name==file_name).first()
    return item

def retrieve_videos(db:Session,file_id:str):
    items = db.query(VideoData).filter(VideoData.file_id==file_id).all()
    return items

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

def set_video_progress(db:Session,file_id:str,file_name:str):
    progress =  db.query(VideoData).filter(VideoData.file_id==file_id,VideoData.file_name==file_name).first()
    process = progress.is_processed
    if process == False:
        process = True
        db.commit()
        db.refresh(progress)
        return process
    else:
        pass

def save(db:Session,file_id:str,file_name:str,bucket_name:str | None=None):
    #create a  folder to save video
    loc = os.getcwd()
    if bucket_name is None:
        file_path = os.path.join(loc,file_id)
    else:
        file_path = os.path.join(loc,bucket_name)

    if os.path.isdir(file_path):
        pass
    else:
        os.mkdir(file_path)

    #absolute file path
    file_save = os.path.join(file_path,file_name)

    #retrieve all chunk bytes from Chunks matching the file_id sequencially
    chunk = db.query(Chunks).filter(Chunks.file_id==file_id).order_by(Chunks.blob_number.asc()).all()

    #sort and extract chunk 
    for chun in chunk:
        ckd = chun.blob_data
        with open(file_save,"ab+") as output:
            output.write(ckd)

    
    
    
    
    
    #set the progress of chunks
    for x in chunk:
        bn = x.blob_number
        set_chunk_progress(db,file_id,bn)
    print("chunks progress updated")

    #update video progress data
    progress_item = Progress(file_id=file_id,is_processed=True)
    db.add(progress_item)
    db.commit()
    db.refresh(progress_item)
    print("file progress updated")

    return True
        

    




