from . import db
from sqlalchemy.orm import relationship


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    specialty = db.Column(db.String, nullable=False)
    appointments = relationship('Appointment', back_populates='doctor')
    availabilities = relationship('DoctorAvailability', back_populates='doctor')

    def __repr__(self):
        return f'<Doctor {self.id}: {self.name} ({self.specialty})>'