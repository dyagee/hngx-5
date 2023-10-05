#author: Agee Aondo
#Year: 2023
#import all the required modules
#from markupsafe import escape

from sqlalchemy.orm import Session
from models import VideoData, Chunks
import os


def db_create_empty(db:Session, file_id:str, media_type:str,file_extension:str):
    video_item =  VideoData(media_type=media_type,file_extension=file_extension,file_id=file_id)
    db.add(video_item)
    db.commit()
    db.refresh(video_item)
    return video_item

def upload_chunk(db:Session, file_id:str,is_last:bool,blob_number:int):
    is_processed=True
    chunk_item = Chunks(file_id=file_id,is_last=is_last,is_processed=is_processed,blob_number=blob_number)
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








def retrieve_videos(db:Session,file_id:str):
    items = db.query(VideoData).filter(VideoData.file_id==file_id).all()
    return items




def save(db:Session,file_id:str,file_name:str,bucket_name:str):
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
        

    




