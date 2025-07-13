from . import db
from sqlalchemy.orm import relationship


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Isto define o outro lado da relação para agendamentos e logs de chat
    appointments = relationship('Appointment', back_populates='patient')
    scheduled_exams = relationship('ScheduledExam', back_populates='patient')

    def __repr__(self):
        return f'<Patient {self.id}: {self.name}>'