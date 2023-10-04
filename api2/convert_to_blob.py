import base64
import os


def break_video_into_blob_files(video_file,dir,blob_number, chunk_size):
    with open(video_file, 'rb') as video:
        video_data = video.read()

    total_size = len(video_data)
    chunk_count = 0
    start = 0

    while start < total_size:
        end = min(start + chunk_size, total_size)
        chunk_data = video_data[start:end]

        # Encode the chunk in base64
        chunk_base64 = base64.b64encode(chunk_data).decode('utf-8')

        # Save the chunk as a Blob file
        save_chunk_as_blob(chunk_base64,dir,blob_number,chunk_count)

        start = end
        chunk_count += 1


def save_chunk_as_blob(chunk_data,dir,blob_number, chunk_count):
    #blob_dir = 'media/blob'  # Directory to store blob files
    #os.makedirs(chunk_dir, exist_ok=True)

    # Save the chunk as a blob file
    with open(os.path.join(dir, f'chunk_{blob_number}_{chunk_count}.blob'), 'w') as file:
        file.write(chunk_data)

'''
if __name__ == "__main__":
    video_file = 'media/eat_well.mp4'  # Replace with your video file
    chunk_size = 1000000  # Adjust as needed (1 MB in bytes)
    break_video_into_blob_files(video_file, chunk_size)
'''