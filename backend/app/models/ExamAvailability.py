from . import db
from sqlalchemy.orm import relationship

class ExamAvailability(db.Model):
    __tablename__ = 'exam_availabilities'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    exam = relationship('Exam', back_populates='availabilities')

    def __repr__(self):
        return f'<ExamAvailability for Exam {self.exam_id} on {self.date}>'
