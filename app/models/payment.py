# app/models/payment.py

from sqlalchemy import Column, ForeignKey, DateTime, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    amount = Column(Float)
    payment_status = Column(Enum('pending', 'completed', 'failed', name='payment_status'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")

    def mark_as_completed(self):
        """Mark the payment as completed."""
        self.payment_status = 'completed'

    def mark_as_failed(self):
        """Mark the payment as failed."""
        self.payment_status = 'failed'
