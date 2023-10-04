from sqlalchemy import Boolean, Column, DateTime, Integer, Text,String, LargeBinary
from sqlalchemy.sql import func
from database import Base


class VideoData(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_id = Column(String, default=False)
    media_type = Column(String, default="video/mp4")
    file_extension =Column(String,default="mp4")
    transcript = Column(Text,default="")
    status = Column(Boolean,default=False)
    transcribed = Column(Boolean,default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    


class Chunks(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    blob_number = Column(Integer, nullable=False)
    file_id = Column(String, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_processed = Column(Boolean, default=False)
    is_last = Column(Boolean, default=False)
    


