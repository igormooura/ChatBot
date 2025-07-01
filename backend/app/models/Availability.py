from . import db
from sqlalchemy.orm import relationship


class Availability(db.Model):
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    doctor = relationship('Doctor', back_populates='availabilities')

    def __repr__(self):
        return f'<Availability for Doctor {self.doctor_id} on day {self.date}>'