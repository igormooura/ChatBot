# backend/app/models/User.py
from . import db
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users' 

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) 
    created_at = db.Column(db.DateTime, default=db.func.now())

    patient = relationship('Patient', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        """Cria um hash para a senha fornecida."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash salvo."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'