import psycopg2
import os
import uuid
from flask import Flask, request, jsonify
from models import db, bcrypt, User, Project , TeamMember, Task, Status, TaskStatus
from datetime import datetime
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')


db.init_app(app)
migrate = Migrate(app, db)
bcrypt.init_app(app)
#  Change CORS During production
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Creating tables before first request incase there are no tables
with app.app_context():
    db.create_all()

# Getting user from Clerk ID
def get_user_by_clerk_id(clerk_id):
    return User.query.filter_by(clerk_id=clerk_id).first()

 # --------------Sign up process for clerk -------------
@app.route('/api/signup/', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     email = data.get('email')
#     clerk_id = data.get('clerk_id')
    
#     if not all([username, email, clerk_id]):
#         return jsonify({"error": "Missing required fields"}), 400
    
#     # # ------------------Checking if user exists
#     existing_user = User.query.filter_by(clerk_id=clerk_id).first()
#     if existing_user:
#         return jsonify({"message": "User already exists", "user_id": existing_user.clerk_id}), 200
    
# #     # --------------------Creating the new user after all checks have been made and requirements are fulfilled
#     new_user = User(username=username, email=email, clerk_id=clerk_id)
#     db.session.add(new_user)
#     db.session.commit()
    
#     return jsonify({"message": "User created successfully", "user_id": new_user.clerk_id}), 201

def signup():
    data = request.get_json()
    required_fields = ['username', 'email', 'clerk_id']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    if User.query.filter_by(clerk_id=data['clerk_id']).first():
        return jsonify({"message": "User already exists"}), 200
    
    try :
        new_user = User(
            username=data['username'],
            email=data['email'],
            clerk_id=data['clerk_id']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully", 
                        "user_id": str(new_user.id)
                        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500    

# # --------------------- Creating a new project ---------------------
@app.route('/api/projects/', methods=['POST'])
# def create_project():
#     data = request.get_json()
#     clerk_id = data.get('user_id')
    
#     if not clerk_id:
#         return jsonify({"error": "Missing Clerk user_id"}), 400
    
#     user = get_user_by_clerk_id(clerk_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404
    

    
#     new_project = Project(
#         title=data.get('title'),
#         client_name=data.get('client_name'),
#         contractor_name=data.get('contractor_name'),
#         currency=data.get('currency', 'USD'),
#         project_cost=data.get('project_cost'),
#         description=data.get('description'),
#         site_location=data.get('site_location'),
#         client_email=data.get('client_email'),
#         contractor_email=data.get('contractor_email'),
#         completion_date=datetime.fromisoformat(data['completion_date']) if data.get('completion_date') else None,
#         start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
#         progress=data.get('progress', 0),
#         user_id=user.id
#     )
    
#     db.session.add(new_project)
#     db.session.commit()
    
#     return jsonify({
#         "message": "Project created successfully",
#         "project_id": new_project.id
#     }), 201


def create_project():
    data = request.get_json()
    required_fields = ['title', 'client_name', 'contractor_name', 'project_cost',
                       'site_location', 'client_email', 'contractor_email', 'completion_date', 'start_date']

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    user = get_user_by_clerk_id(data['clerk_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        new_project = Project(
            id=uuid.uuid4(),
            title=data['title'],
            client_name=data.get['client_name'],
            contractor_name=data.get['contractor_name'],
            currency=data['currency'],
            project_cost=data.get['project_cost'],
            description=data.get('description', ''),
            site_location=data.get['site_location'],
            client_email=data.get['client_email'],
            contractor_email=data.get['contractor_email'],
            completion_date=datetime.fromisoformat(data['completion_date']),
            start_date=datetime.fromisoformat(data['start_date']),
            progress=data.get('progress', 0),
            user_id=user.id
        )

        db.session.add(new_project)
        db.session.commit()

        return jsonify({
            "message": "Project created successfully",
            "project_id": str(new_project.id)
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    

# ------------------- Get All Projects for a User -------------------



@app.route('/api/projects/', methods=['GET'])
def get_projects():
    clerk_id = request.args.get('clerk_id')
    if not clerk_id:
        return jsonify({"error": "Missing Clerk user_id"}), 400
    
    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    projects = Project.query.filter_by(user_id=user.id).all()
    return jsonify([p.to_dict() for p in projects]), 200
    # clerk_id = request.args.get('clerk_id')
    # user = get_user_by_clerk_id(clerk_id)
    # if not user:
    #     return jsonify({"error": "User not found"}), 404

    # projects = Project.query.filter_by(user_id=user.clerk_id).all()
    # return jsonify([p.to_dict() for p in projects]), 200

# ------------------- Get/Update/Delete Individual Project -------------------
@app.route('/api/projects/<uuid:project_id>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(project_id):
    clerk_id = request.args.get('clerk_id')
    if not clerk_id:
        return jsonify({"error": "Missing Clerk user_id"}), 400
    
    user = get_user_by_clerk_id(clerk_id)
    if not user:
            return jsonify({"error": "User not found"}), 404
        
    project = Project.query.get(project_id)  
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    if project.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    if request.method == 'GET':
        return jsonify(project.to_dict()), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        for field in ['title', 'client_name', 'contractor_name', 'currency', 'project_cost',
                      'site_location', 'client_email', 'contractor_email', 'progress']:
            if field in data:
                setattr(project, field, data[field])

        if 'start_date' in data:
            project.start_date = datetime.fromisoformat(data['start_date'])
        if 'completion_date' in data:
            project.completion_date = datetime.fromisoformat(data['completion_date'])

        db.session.commit()
        return jsonify(project.to_dict()), 200
    
    if request.method == 'DELETE':
       try:
            db.session.delete(project)
            db.session.commit()
            return jsonify({"message": "Project deleted"}), 200
        
       except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
# def project_detail(project_id):
#     clerk_id = request.args.get('clerk_id')
#     user = get_user_by_clerk_id(clerk_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     project = Project.query.get_or_404(project_id)

#     if project.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403

#     if request.method == 'GET':
#         return jsonify(project.to_dict()), 200

#     if request.method == 'PUT':
#         data = request.get_json()
#         for field in ['title', 'client_name', 'contractor_name', 'currency', 'project_cost',
#                       'site_location', 'client_email', 'contractor_email', 'progress']:
#             if field in data:
#                 setattr(project, field, data[field])

#         if 'start_date' in data:
#             project.start_date = datetime.fromisoformat(data['start_date'])
#         if 'completion_date' in data:
#             project.completion_date = datetime.fromisoformat(data['completion_date'])

#         db.session.commit()
#         return jsonify(project.to_dict()), 200

#     if request.method == 'DELETE':
#         db.session.delete(project)
#         db.session.commit()
#         return jsonify({"message": "Project deleted"}), 200

# ------------------- Team Members -------------------
@app.route('/api/projects/<uuid:project_id>/team-members/', methods=['GET', 'POST'])
def team_members(project_id):
    clerk_id = request.args.get('clerk_id')
    if not clerk_id:
        return jsonify({"error": "Missing Clerk id"}), 400
    
    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if project.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'GET':
        members = TeamMember.query.filter_by(project_id=project.id).all()
        return jsonify([m.to_dict() for m in members]), 200

    if request.method == 'POST':
        data = request.get_json()
        new_member = TeamMember(
            id=uuid.uuid4(),
            full_name=data['full_name'],
            email=data['email'],
            role=data.get('role', 'Labor'),
            designation=data.get('designation'),
            bio=data.get('bio'),
            user_id=user.id,
            project_id=project.id
        )
        db.session.add(new_member)
        db.session.commit()
        return jsonify(new_member.to_dict()), 201
# def team_members(project_id):
#     clerk_id = request.args.get('user_id')
#     user = get_user_by_clerk_id(clerk_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     project = Project.query.get_or_404(project_id)
#     if project.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403

#     if request.method == 'GET':
#         return jsonify([m.to_dict() for m in project.team_members]), 200

#     if request.method == 'POST':
#         data = request.get_json()
#         new_member = TeamMember(
#             full_name=data['full_name'],
#             email=data['email'],
#             role=data.get('role', 'Labor'),
#             designation=data.get('designation'),
#             bio=data.get('bio'),
#             user_id=user.clerk_id,
#             project_id=project.id
#         )
#         db.session.add(new_member)
#         db.session.commit()
#         return jsonify(new_member.to_dict()), 201

@app.route('/api/team-members/<uuid:member_id>/', methods=['GET', 'PATCH', 'DELETE'])
def team_member_detail(member_id):
    clerk_id = request.args.get('clerk_id')
    if not clerk_id:
        return jsonify({"error": "Missing Clerk id"}), 400
    
    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    member = TeamMember.query.get(member_id)
    if not member:
        return jsonify({"error": "Team member not found"}), 404

    project = Project.query.get(member.project_id)
    if project.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    if request.method == 'GET':
        return jsonify(member.to_dict()), 200

    if request.method == 'PATCH':
        data = request.get_json()
        for field in ['full_name', 'email', 'role', 'designation', 'bio']:
            if field in data:
                setattr(member, field, data[field])
        db.session.commit()
        return jsonify(member.to_dict()), 200

    if request.method == 'DELETE':
        db.session.delete(member)
        db.session.commit()
        return jsonify({"message": "Team member deleted"}), 200
# def team_member_detail(member_id):
#     clerk_id = request.args.get('user_id')
#     user = get_user_by_clerk_id(clerk_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     member = TeamMember.query.get_or_404(member_id)
#     if member.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403

#     if request.method == 'GET':
#         return jsonify(member.to_dict()), 200

#     if request.method == 'PATCH':
#         data = request.get_json()
#         for field in ['full_name', 'email', 'role', 'designation', 'bio']:
#             if field in data:
#                 setattr(member, field, data[field])
#         db.session.commit()
#         return jsonify(member.to_dict()), 200

#     if request.method == 'DELETE':
#         db.session.delete(member)
#         db.session.commit()
#         return jsonify({"message": "Team member deleted"}), 200


# # ------------------- Tasks -------------------
@app.route('/api/projects/<uuid:project_id>/tasks/', methods=['GET', 'POST'])
def tasks(project_id):
    clerk_id = request.args.get('clerk_id')
    if not clerk_id:
        return jsonify({"error": "Missing Clerk id"}), 400
    
    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if project.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'GET':
        tasks = Task.query.filter_by(project_id=project.id).all()
        return jsonify([t.to_dict() for t in tasks]), 200

    if request.method == 'POST':
        data = request.get_json()
        new_task = Task(
            id=uuid.uuid4(),
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Not Started'),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            project_id=project.id,
            assignee_id=data.get('assignee_id')
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify(new_task.to_dict()), 201
# def tasks(project_id):
#     clerk_id = request.args.get('user_id')
#     user = get_user_by_clerk_id(clerk_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     project = Project.query.get_or_404(project_id)
#     if project.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403

#     if request.method == 'GET':
#         return jsonify([t.to_dict() for t in project.tasks]), 200

#     if request.method == 'POST':
#         data = request.get_json()
#         new_task = Task(
#             title=data['title'],
#             description=data.get('description'),
#             priority=data.get('priority', 'Medium'),
#             status=data.get('status', 'Not Started'),
#             start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
#             due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
#             project_id=project.id,
#             assignee_id=data.get('assignee_id')
#         )
#         db.session.add(new_task)
#         db.session.commit()
#         return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>/', methods=['GET', 'PATCH', 'DELETE'])
def task_detail(task_id):
    clerk_id = request.args.get('clerk_id')
    if not clerk_id:
        return jsonify({"error": "Missing Clerk id"}), 400

    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    project = Project.query.get(task.project_id)
    if project.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'GET':
        return jsonify(task.to_dict()), 200

    if request.method == 'PATCH':
        data = request.get_json()
        for field in ['title', 'description', 'priority', 'status', 'assignee_id']:
            if field in data:
                setattr(task, field, data[field])
        if 'start_date' in data:
            task.start_date = datetime.fromisoformat(data['start_date'])
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date'])
        db.session.commit()
        return jsonify(task.to_dict()), 200

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted"}), 200
# def task_detail(task_id):
#     clerk_id = request.args.get('user_id')
#     user = get_user_by_clerk_id(clerk_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     task = Task.query.get_or_404(task_id)
#     if task.project.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403

#     if request.method == 'GET':
#         return jsonify(task.to_dict()), 200

#     if request.method == 'PATCH':
#         data = request.get_json()
#         for field in ['title', 'description', 'priority', 'status', 'assignee_id']:
#             if field in data:
#                 setattr(task, field, data[field])
#         if 'start_date' in data:
#             task.start_date = datetime.fromisoformat(data['start_date'])
#         if 'due_date' in data:
#             task.due_date = datetime.fromisoformat(data['due_date'])
#         db.session.commit()
#         return jsonify(task.to_dict()), 200

#     if request.method == 'DELETE':
#         db.session.delete(task)
#         db.session.commit()
#         return jsonify({"message": "Task deleted"}), 200


# Run the app
if __name__ == '__main__':
    app.run(debug=True)


