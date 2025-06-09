import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()
bcrypt = Bcrypt()

class Status(Enum):
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

class User(UserMixin, db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    clerk_id = db.Column(db.String(100), nullable=False)
    projects = db.relationship('Project', backref='owner', lazy=True)
    # team_members = db.relationship('TeamMember', backref='user', lazy=True)

class Project(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(SQLAlchemyEnum(Status),nullable=False , default=Status.PLANNING)
    client_name = db.Column(db.String(100), nullable=True)
    contractor_name = db.Column(db.String(100), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    project_cost = db.Column(db.Float, nullable=True)
    site_location = db.Column(db.String(200), nullable=True)
    client_email = db.Column(db.String(100), nullable=True)
    contractor_email = db.Column(db.String(100), nullable=True)
    
    # year  month date
    completion_date = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Integer, default=0)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # tasks = db.relationship('Task', backref='project', lazy=True)
    # team_members = db.relationship('TeamMember', backref='project', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description":self.description,
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
            "user_id": self.user_id,
            "status": self.status.name
        }
        
# class TeamMember(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     full_name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     role = db.Column(db.String(50), nullable=False)  # e.g., "Supervisor", "Labor"
#     designation = db.Column(db.String(100), nullable=True)
#     bio = db.Column(db.Text, nullable=True)
#     user_id = db.Column(db.String(100), db.ForeignKey('user.clerk_id'), nullable=False)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "full_name": self.full_name,
#             "email": self.email,
#             "role": self.role,
#             "designation": self.designation,
#             "bio": self.bio,
#             "project_id": self.project_id
#         }

# class Task(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     priority = db.Column(db.String(20), default='Medium')  # Low/Medium/High
#     status = db.Column(db.String(20), default='Not Started')  # Not Started/In Progress/Completed
#     start_date = db.Column(db.DateTime, nullable=True)
#     due_date = db.Column(db.DateTime, nullable=True)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
#     assignee_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=True)
#     assignee = db.relationship('TeamMember', backref='tasks')

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "title": self.title,
#             "description": self.description,
#             "priority": self.priority,
#             "status": self.status,
#             "start_date": self.start_date.isoformat() if self.start_date else None,
#             "due_date": self.due_date.isoformat() if self.due_date else None,
#             "project_id": self.project_id,
#             "assignee_id": self.assignee_id
#         }        