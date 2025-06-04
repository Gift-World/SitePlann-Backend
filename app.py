import os
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from models import db, bcrypt, User, Project
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables before first request
# @app.before_first_request
# def create_tables():
#     db.create_all()

# --------------------- Authentication Routes ---------------------
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user exists
    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return jsonify({"error": "Email or username already exists"}), 409
    
    # Create new user
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({"error": "Email and password required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username
        }), 200
        
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

# --------------------- Project CRUD Routes ---------------------
@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({"error": "Project title is required"}), 400
    
    new_project = Project(
        title=data.get('title'),
        client_name=data.get('client_name'),
        contractor_name=data.get('contractor_name'),
        currency=data.get('currency', 'USD'),
        project_cost=data.get('project_cost'),
        site_location=data.get('site_location'),
        client_email=data.get('client_email'),
        contractor_email=data.get('contractor_email'),
        completion_date=datetime.fromisoformat(data['completion_date']) if data.get('completion_date') else None,
        start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
        progress=data.get('progress', 0),
        user_id=current_user.id
    )
    
    db.session.add(new_project)
    db.session.commit()
    return jsonify({
        "message": "Project created successfully",
        "project_id": new_project.id
    }), 201

@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify([p.to_dict() for p in projects]), 200

@app.route('/api/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(project.to_dict()), 200

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    
    # Update fields
    project.title = data.get('title', project.title)
    project.client_name = data.get('client_name', project.client_name)
    project.contractor_name = data.get('contractor_name', project.contractor_name)
    project.currency = data.get('currency', project.currency)
    project.project_cost = data.get('project_cost', project.project_cost)
    project.site_location = data.get('site_location', project.site_location)
    project.client_email = data.get('client_email', project.client_email)
    project.contractor_email = data.get('contractor_email', project.contractor_email)
    project.progress = data.get('progress', project.progress)
    
    if 'completion_date' in data:
        project.completion_date = datetime.fromisoformat(data['completion_date'])
    if 'start_date' in data:
        project.start_date = datetime.fromisoformat(data['start_date'])
    
    db.session.commit()
    return jsonify(project.to_dict()), 200

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)