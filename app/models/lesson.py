# app/models/lesson.py

from sqlalchemy import Column, String, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey('modules.id'))
    title = Column(String, nullable=False)
    content = Column(Text)
    video_url = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    order = Column(Float)
    
    module = relationship("Module", back_populates="lessons")

    def add_content(self, content: str):
        """Add or update content for the lesson."""
        self.content = content

    def add_video(self, video_url: str):
        """Add a video URL for the lesson."""
        self.video_url = video_url

    def add_pdf(self, pdf_url: str):
        """Add a PDF URL for the lesson."""
        self.pdf_url = pdf_url
