from pydantic import BaseModel


class ResponseMakeVideo(BaseModel):
    srt:str
    text:str
    video_path:str
