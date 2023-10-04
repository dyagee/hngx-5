#author: Agee Aondo
#Year: 2023

from sqlalchemy.orm import Session
import os
import subprocess
import uuid
import numpy as np
import cv2
from models import VideoData, Chunks
from services import get_video_dir, get_chunk_dir

def combine_chunks(file_id:str,db:Session):
    chunks = db.query(Chunks).filter(Chunks.file_id==file_id).order_by(Chunks.blob_number.asc()).all()
    if chunks is None:
        return None
    #mime_type = latest_chunk.session.mime_type
    # Define the output video path
    vid_item = db.query(VideoData).filter(VideoData.file_id==file_id).first()
    if vid_item is None:
        return None
    file_name = f'combined_video{file_id}.{vid_item.file_ext}'
    output_path = os.path.join(get_video_dir(file_id),file_name )

    # Call the combine_chunks_to_video function
    combine_chunks_to_video(get_chunk_dir(file_id), output_path)

    return file_name,output_path


def combine_chunks_to_video(chunk_dir, output_video_path):
    # Get a list of chunk files in the directory
    chunk_files = sorted([os.path.join(chunk_dir, file) for file in os.listdir(chunk_dir)])

    # Initialize an empty list to store chunk data
    chunk_data = []

    for chunk_file in chunk_files:
        with open(chunk_file, 'rb') as file:
            chunk_data.append(file.read())

    # Combine the binary chunks into a single byte stream
    video_data = b''.join(chunk_data)

    # Define video properties (e.g., frame width, height, frame rate)
    frame_width = 640  # Replace with your frame width
    frame_height = 480  # Replace with your frame height
    frame_rate = 30  # Replace with your desired frame rate

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (frame_width, frame_height))

    # Initialize variables for tracking frame position
    frame_pos = 0

    # Read frames from the video data and write them to the output video
    while frame_pos < len(video_data):
        frame_size = frame_width * frame_height * 3  # Assuming 3 channels (e.g., RGB)
        frame_data = video_data[frame_pos:frame_pos + frame_size]
        if len(frame_data) != frame_size:
            break  # Reached the end of video data

        # Reshape frame data and write it to the video
        frame = np.frombuffer(frame_data, dtype=np.uint8).reshape(frame_height, frame_width, 3)
        out.write(frame)
        frame_pos += frame_size

    # Release the VideoWriter and close the video file
    out.release()