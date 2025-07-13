from . import db
from sqlalchemy.orm import relationship

class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)  # Ex: "Hemograma", "Raio-X", etc.
    description = db.Column(db.String)

    scheduled_exams = relationship('ScheduledExam', back_populates='exam')
    availabilities = relationship('ExamAvailability', back_populates='exam')

    def __repr__(self):
        return f'<Exam {self.id}: {self.type}>'
