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
    
    try:
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
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    
    db.session.add(new_project)
    db.session.commit()
    return jsonify({
        "message": "Project created successfully",
        "project_id": new_project.id,
        "project": new_project.to_dict()
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

# Changed from PUT to PATCH for partial updates
@app.route('/api/projects/<int:project_id>', methods=['PATCH'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    
    # Update only provided fields
    if 'title' in data:
        project.title = data['title']
    if 'client_name' in data:
        project.client_name = data['client_name']
    if 'contractor_name' in data:
        project.contractor_name = data['contractor_name']
    if 'currency' in data:
        project.currency = data['currency']
    if 'project_cost' in data:
        project.project_cost = data['project_cost']
    if 'site_location' in data:
        project.site_location = data['site_location']
    if 'client_email' in data:
        project.client_email = data['client_email']
    if 'contractor_email' in data:
        project.contractor_email = data['contractor_email']
    if 'progress' in data:
        project.progress = data['progress']
    
    try:
        if 'completion_date' in data:
            project.completion_date = datetime.fromisoformat(data['completion_date'])
        if 'start_date' in data:
            project.start_date = datetime.fromisoformat(data['start_date'])
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    
    db.session.commit()
    return jsonify({
        "message": "Project updated successfully",
        "project": project.to_dict()
    }), 200

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
    with app.app_context():
        db.create_all()
    app.run(debug=True)