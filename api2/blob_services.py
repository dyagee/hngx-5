#author: Agee Aondo
#Year: 2023

from sqlalchemy.orm import Session
import os
from moviepy.editor import *
from models import VideoData, Chunks
from services import get_video_dir, get_chunk_dir

def prepare_chunks_for_merging(file_id:str,db:Session):
    #check if there are chunks saved under that recording session
    chunks = db.query(Chunks).filter(Chunks.file_id==file_id).order_by(Chunks.blob_number.asc()).all()
    if chunks is None:
        return None
    # Define the output video path
    vid_item = db.query(VideoData).filter(VideoData.file_id==file_id).first()
    if vid_item is None:
        return None
    file_name = f'combined_video{file_id}.{vid_item.file_extension}'
    output_path = os.path.join(get_video_dir(file_id),file_name )

    # Call the combine_chunks_to_video function
    #combine_chunks_to_video(get_chunk_dir(file_id), output_path)

    return file_name,output_path


def combine_chunks_to_video(chunk_dir, output_video_path):
    # Get a list of chunk files in the directory
    chunk_files = sorted([os.path.join(chunk_dir, file) for file in os.listdir(chunk_dir)])

    # create VideoFileClip object for each video file
    clips = [VideoFileClip(c) for c in chunk_files]
    
    # concatenating both the clips
    final = concatenate_videoclips(clips)
    

    # write the output video file
    final.write_videofile(output_video_path, fps=30, threads=1, codec="libx264")