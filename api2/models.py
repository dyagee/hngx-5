from sqlalchemy import Boolean, Column, DateTime, Integer, Text,String, LargeBinary
from sqlalchemy.sql import func
from database import Base


class VideoData(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_id = Column(String, default=False)
    file_type = Column(String, default="video/mp4")
    bucket_name = Column(String)
    Transcript = Column(Text,default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    


class Chunks(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    #blob_number = Column(Integer, nullable=False)
    file_id = Column(String, default=False)
    #blob_data = Column(LargeBinary)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_processed = Column(Boolean, default=False)
    is_last = Column(Boolean, default=False)

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, default=False)
    transcribed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_processed = Column(Boolean, default=False)
