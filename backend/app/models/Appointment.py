from . import db
from sqlalchemy.orm import relationship
from sqlalchemy import Enum


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        Enum('Scheduled', 'Completed', 'Cancelled_by_Patient', 'Cancelled_by_Doctor', 'No_Show', name='appointment_status_enum'),
        nullable=False,
        default='Scheduled'
    )
    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('Doctor', back_populates='appointments')


    def __repr__(self):
        return f'<Appointment {self.id}> with {self.doctor} at {self.date}. Status: {self.status}>'