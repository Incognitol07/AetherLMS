# app/background_tasks/jobs/media_jobs.py
from app.models import Lesson, BackgroundTask
from app.database import SessionLocal
from external_services import video_processor, file_converter

def transcode_video(video_url):
    db = SessionLocal()
    try:
        lesson = db.query(Lesson).filter_by(video_url=video_url).first()
        processed_url = video_processor.transcode(video_url)
        lesson.processed_video_url = processed_url
        db.commit()
    finally:
        db.close()

def generate_document_previews(file_url):
    db = SessionLocal()
    try:
        lesson = db.query(Lesson).filter_by(pdf_url=file_url).first()
        preview_url = file_converter.generate_preview(file_url)
        lesson.preview_url = preview_url
        db.commit()
    finally:
        db.close()