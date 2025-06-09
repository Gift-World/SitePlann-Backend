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
    
    #Relationships
    owner = db.relationship('User', back_populates='projects')
    team_members = db.relationship('TeamMember', backref='project', lazy=True)
    tasks = db.relationship('Task', backref='project', lazy=True)
    
    
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
        
class Team(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., "Supervisor", "Labor"
    designation = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('project.id'), nullable=False)

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
    # id = db.Column(db.Integer, primary_key=True)
    id= db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='Medium')  # Low/Medium/High
    status = db.Column(db.String(20), default='Not Started')  # Not Started/In Progress/Completed
    start_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    # project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    # assignee_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=True)
    # assignee = db.relationship('TeamMember', backref='tasks')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "project_id": self.project_id,
            "assignee_id": self.assignee_id
        }      
        
        #A user logs into the saas application using clerk, and the application retrieves their user information from Clerk.and the user is added t the database in supabase where we can see them.The user can then create a project, which is stored in the database. The user can also add team members to the project, and these team members are stored in the database as well. The user can then create tasks for the project, which are also stored in the database. The user can update the status of the project and tasks, and these updates are reflected in the database. The user can also view their projects, team members, and tasks through the application interface.the relationships between the models are as follows:
# User has many Projects or a single project
# Project has many Team Members and Tasks
# Team Member belongs to a Project
# Task belongs to a Project and can be assigned to a Team Member
# Project has many Team Members and Tasks
# Team Member can many Tasks
# a project belongs to a user
