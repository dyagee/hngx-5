#author: Agee Aondo
#Year: 2023
#import all the upduired modules
from sqlalchemy.orm import Session
from fastapi import FastAPI,Depends, HTTPException,Request,Response,File, UploadFile,Form,Header
from fastapi.responses import RedirectResponse,HTMLResponse,StreamingResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from docs import (summary,description,title, version,contact,docs)
from database import create_database, get_db
#from api.models import ResponseModel,User,UpdateUser
from crud import *
import os

create_database()


app = FastAPI(title=title,summary=summary,docs_url=docs,version=version,contact=contact,description=description)

templates = Jinja2Templates(directory="templates")

@app.post("/api/file")
async def  empty_file(file_name:Annotated[str, Form()],file_id:Annotated[str, Form()],
    file_type:Annotated[str, Form()],bucket_name:Annotated[str, Form()],db: Session = Depends(get_db)):

    resp = create_empty(db=db,file_name=file_name,file_id=file_id,file_type=file_type,bucket_name=bucket_name)
    return jsonable_encoder(resp)

@app.post("/api/chunks")
async def  chunk_upload(file_id:Annotated[str, Form()], blob_data: Annotated[UploadFile, File()],
    is_last:bool, db: Session = Depends(get_db)):
    #query the file_id and get the bucketname and file name
    item = db.query(VideoData).filter(VideoData.file_id==file_id).first()
    if item is not None:
        abs_path =os.getcwd()
        exist_file = item.file_name
        bucket = item.bucket_name
        loc = os.path.join(bucket,exist_file)
        # Read the existing video file
        existing_video_file_path = os.path.join(abs_path,loc)
        print(existing_video_file_path)
        with open(existing_video_file_path, 'rb') as existing_video_file:
            existing_video_buffer = existing_video_file.read()
        
        chunk_contents = blob_data.file.read()
        merged_video_buffer =  existing_video_buffer + chunk_contents
        # Write the merged video buffer back to the existing video file
        with open(existing_video_file_path, 'wb') as merged_video_file:
            merged_video_file.write(merged_video_buffer)
        resp = upload_chunk(db=db,file_id=file_id,is_last=is_last)
        print("Chunk processed successfully")
    return jsonable_encoder(resp)

#this is called if the chunk is_last is true, return the rendered video
@app.post("/api/render/{file_id}")
async def render_video(file_id:str,range: str = Header(None),db: Session = Depends(get_db)):
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
    