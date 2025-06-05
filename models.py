#model.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    clerk_id = db.Column(db.String(100), nullable=False)
    projects = db.relationship('Project', backref='owner', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    client_name = db.Column(db.String(100), nullable=True)
    contractor_name = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    project_cost = db.Column(db.Float, nullable=True)
    site_location = db.Column(db.String(200), nullable=True)
    client_email = db.Column(db.String(100), nullable=True)
    contractor_email = db.Column(db.String(100), nullable=True)
    completion_date = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Integer, default=0)
    user_id = db.Column(db.String(100), db.ForeignKey('user.clerk_id'), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "client_name": self.client_name,
            "contractor_name": self.contractor_name,
            "currency": self.currency,
            "project_cost": self.project_cost,
            "site_location": self.site_location,
            "client_email": self.client_email,
            "contractor_email": self.contractor_email,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "progress": self.progress,
            "user_id": self.user_id
        }