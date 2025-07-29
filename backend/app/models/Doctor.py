from . import db
from sqlalchemy.orm import relationship

doctor_specialties = db.Table('doctor_specialties',
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctors.id'), primary_key=True),
    db.Column('specialty_id', db.Integer, db.ForeignKey('specialties.id'), primary_key=True)
)

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    specialty = db.Column(db.String, nullable=False)
    appointments = relationship('Appointment', back_populates='doctor')
    availabilities = relationship('DoctorAvailability', back_populates='doctor')

    def __repr__(self):
        return f'<Doctor {self.id}: {self.name} ({self.specialty})>'

class Specialty(db.Model):
    __tablename__ = 'specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    doctors = relationship('Doctor', secondary=doctor_specialties, back_populates='specialties')

    def __repr__(self):
        return f'<Specialty {self.id}: {self.name}>'