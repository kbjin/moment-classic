from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MusicCreate(BaseModel):
    emotion: str
    title: str
    youtube_url: str
    description: Optional[str] = None
    commentary: Optional[str] = None


class Music(MusicCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
