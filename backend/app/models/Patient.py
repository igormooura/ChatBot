from . import db
from sqlalchemy.orm import relationship


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)

    appointments = relationship('Appointment', back_populates='patient')

    def __repr__(self):
        return f'<Patient {self.id}: {self.name}>'