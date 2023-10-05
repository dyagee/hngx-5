import base64
import os


def create_video_blob_files(video_file,dir,ext,blob_number, chunk_size):
    #with open(video_file, 'rb') as video:
    video_data = video_file.read()
    print(ext)
    #total_size = len(video_data)
    
    
   
    # Save the chunk as a Blob file
    save_chunk_as_blob(video_data,ext,dir,blob_number)

    


def save_chunk_as_blob(chunk_data,ext,dir,blob_number):
    #blob_dir = 'media/blob'  # Directory to store blob files
    #os.makedirs(chunk_dir, exist_ok=True)

    # Save the chunk as a blob file
    with open(os.path.join(dir, f'chunk_{blob_number}.{ext}'), 'wb') as file:
        file.write(chunk_data)

'''
if __name__ == "__main__":
    video_file = 'media/eat_well.mp4'  # Replace with your video file
    chunk_size = 1000000  # Adjust as needed (1 MB in bytes)
    break_video_into_blob_files(video_file, chunk_size)
'''