from . import db
from sqlalchemy.orm import relationship
from sqlalchemy import Enum


class ScheduledExam(db.Model):
    __tablename__ = 'scheduled_exams'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        Enum('Scheduled', 'Completed', 'Cancelled', 'No_Show', name='exam_status_enum'),
        nullable=False,
        default='Scheduled'
    )

    patient = relationship('Patient', back_populates='scheduled_exams')
    exam = relationship('Exam', back_populates='scheduled_exams')

    def __repr__(self):
        return f'<ScheduledExam {self.id}: {self.exam.type} for Patient {self.patient_id} on {self.date}. Status: {self.status}>'
