from sqlalchemy import Column, Integer, Text, TIMESTAMP, func

from moment_classic.database import Base


class MusicEntry(Base):
    __tablename__ = "music_entries"
    __table_args__ = {"schema": "main_db"}

    id = Column(Integer, primary_key=True, index=True)
    emotion = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    youtube_url = Column(Text, nullable=False)
    description = Column(Text)
    commentary = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
