#author: Agee Aondo
#Year: 2023
#import all the upduired modules
from sqlalchemy.orm import Session
from fastapi import FastAPI,Depends, HTTPException,Request,Response,File, UploadFile,Form,Header,BackgroundTasks
from fastapi.responses import RedirectResponse,HTMLResponse,StreamingResponse
#from fastapi.templating import Jinja2Templates
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from docs import (summary,description,title, version,contact,docs)
from database import create_database, get_db
#from api.models import ResponseModel,User,UpdateUser
from crud import *
from services import *
from blob_services import *
from convert_to_blob import *
from transcribe import transcribe_video
import os

chunk_size = 1000000 
create_database()


app = FastAPI(title=title,summary=summary,docs_url=docs,version=version,contact=contact,description=description)

#templates = Jinja2Templates(directory="templates")

@app.post("/api/start")
async def  start_recording(media_type:Annotated[str, Form()],file_extension:Annotated[str, Form()],db: Session = Depends(get_db)):
    '''This endpoint creates file instance when press start recording, and returns file_id for the recording session'''
    #generate id for the recording session/file
    file_id = generate_uuid(db=db)
    
    #create files bucket
    create_empty(file_id=file_id)

    #create a file instance in db
    resp = db_create_empty(db=db,file_id=file_id,media_type=media_type,file_extension=file_extension)
    return jsonable_encoder(resp)

@app.post("/api/chunks")
async def  chunk_upload(file_id:Annotated[str, Form()],blob_number:Annotated[int, Form()], blob_data: Annotated[UploadFile, File()],
    is_last:bool, db: Session = Depends(get_db)):
    '''This endpoint handles uploading of chunks at intervals, uses form submission'''
    
    #query the file_id and get the bucketname and file name
    item = db.query(VideoData).filter(VideoData.file_id==file_id).first()
    if item is not None:
        chunk_dir = get_chunk_dir(file_id)
        os.makedirs(chunk_dir, exist_ok=True)

        #get the file extension and extract blob bytes
        ext = blob_data.filename.split(".",1)[1][:3]
        blob_data = blob_data.file
        

        #break the blob data into 1mb blobs and save to chunks folder
        create_video_blob_files(blob_data,chunk_dir,ext,blob_number, chunk_size)

        resp = upload_chunk(db=db,file_id=file_id,blob_number=blob_number,is_last=is_last)
        print("Chunk processed successfully")
        return jsonable_encoder(resp)
    raise HTTPException(status_code=404, detail="file_id not found")

@app.post("/api/stop")
async def  stop_recording(file_id:Annotated[str, Form()],blob_number:Annotated[int, Form()], blob_data: Annotated[UploadFile, File()],
    is_last:bool,background_tasks:BackgroundTasks, db: Session = Depends(get_db)):
    '''This endpoint handles uploading of chunks, automatically sets chunk as last and calls for merging of chunks , uses form submission'''
    if is_last != True:
        is_last = True
    #query the file_id and get the bucketname and file name
    item = db.query(VideoData).filter(VideoData.file_id==file_id).first()
    if item is not None:
        chunk_dir = get_chunk_dir(file_id)
        os.makedirs(chunk_dir, exist_ok=True)

        #get file extension and extract blob bytes
        ext = blob_data.filename.split(".",1)[1][:3]
        blob_data = blob_data.file
        
        #break the blob data into 1mb blobs and save to chunks folder
        create_video_blob_files(blob_data,chunk_dir,ext,blob_number, chunk_size)

        resp = upload_chunk(db=db,file_id=file_id,blob_number=blob_number,is_last=is_last)
        print("Chunk processed successfully")

        #return jsonable_encoder(resp)

        #call prepare chunks for the merging process
        file_name,output_path = prepare_chunks_for_merging(file_id=file_id,db=db)

        #update the process in the database
        update_process = VideoData(file_name=file_name, file_path=output_path,status="processing")
        db.add(update_process)
        db.commit()
        db.refresh(update_process)

        #merge the video and tidy up processing in the background in order not to keep user hanging
        background_tasks.add_task(combine_chunks_to_video,get_chunk_dir(file_id), output_path)
        response = {
            "status":"success",
            "file_name":file_name,
            "file_path":output_path,
            "processed last chunk": jsonable_encoder(resp)
        }
        return response

    raise HTTPException(status_code=404, detail="file_id not found")



@app.post("/api/render/{file_id}")
async def render_video(file_id:str,range: str = Header(None),db: Session = Depends(get_db)):
    '''This is called to return video file and render it for streaming in browser'''
    #check if the file_id requested for is valid
    item = db.query(VideoData).filter(VideoData.file_id==file_id).first()
    if item is not None:
        loc = os.getcwd()
        bucket = item.bucket_name
        fn = item.file_name
        m_type = item.file_type
        vid_path = os.path.join(bucket,fn)
        file_path = os.path.join(loc,vid_path)

        #get the range from header as the user play the video
        start, end = range.replace("bytes=", "").split("-")
        start = int(start)

        with open(file_path, "rb") as video:
            video.seek(start)
            data = video.read()
            filesize = str(os.stat(file_path).st_size)
            end = int(filesize)-1
            contentLength = end - start + 1
            headers = {
                'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
                'Accept-Ranges': 'bytes',
                "Content-Length":str(contentLength),
            }
        return Response(data, status_code=206, headers=headers, media_type=m_type)
    raise HTTPException(status_code=404,detail="file not found")
     
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app",reload=True)  
    