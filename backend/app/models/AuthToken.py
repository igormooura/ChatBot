# backend/app/models/AuthToken.py
import secrets
from datetime import datetime, timedelta, timezone
from .. import db

class AuthToken(db.Model):
    __tablename__ = 'auth_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(6), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    
    patient = db.relationship('Patient')

    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.token = str(secrets.randbelow(1_000_000)).zfill(6)
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    def is_expired(self):
        # Agora a comparação funcionará, pois ambos os lados são "offset-aware"
        return datetime.now(timezone.utc) > self.expires_at

    def __repr__(self):
        return f'<AuthToken para Patient {self.patient_id}>'