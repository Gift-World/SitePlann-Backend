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
    
class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"    

class User(UserMixin, db.Model):
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    clerk_id = db.Column(db.String(100), nullable=False)
    projects = db.relationship('Project', back_populates='owner', lazy=True)

class Project(db.Model):
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
    
    #Relationships
    owner = db.relationship('User', back_populates='projects')
    team_members = db.relationship('TeamMember', back_populates='project', lazy=True)
    tasks = db.relationship('Task', back_populates='project', lazy=True)
    
    
    def to_dict(self):
        return {
            "id": str(self.id),
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
            "user_id": str(self.user_id),
            "status": self.status.name
        }
        
class TeamMember(db.Model):
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  
    designation = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)

#Relationships
    project = db.relationship('Project', back_populates='team_members')
    tasks = db.relationship('Task', back_populates='assignee', lazy=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "designation": self.designation,
            "bio": self.bio,
            # "project_id": str(self.project_id)
        }

class Task(db.Model):
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='Medium')  # Low/Medium/High
    status = db.Column(db.String(20), default='Not Started')  # Not Started/In Progress/Completed
    start_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('team_members.id'), nullable=True)
    


#Relationships

    project = db.relationship('Project', back_populates='tasks')
    assignee = db.relationship('TeamMember', back_populates='tasks')
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "project_id": str(self.project_id),
            "assignee_id": str(self.assignee_id)
        }      
        
       
