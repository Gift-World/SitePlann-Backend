# import os
# from flask import Flask, request, jsonify
# # from flask_login import LoginManager, login_user, current_user, login_required, logout_user
# from models import db, bcrypt, User, Project
# from datetime import datetime
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# db = SQLAlchemy()

# CORS(app, origins="*")


# # Initialize extensions
# db.init_app(app)
# bcrypt.init_app(app)

# # Flask-Login setup
# # login_manager = LoginManager(app)
# # login_manager.login_view = 'login'

# # @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # Create tables before first request
# # @app.before_first_request
# # def create_tables():
# #     db.create_all()

# # --------------------- Authentication Routes ---------------------
# @app.route('/api/signup/', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     email = data.get('email')
#     clerk_id = data.get('clerk_id')
    
#     if not all([username, email, clerk_id]):
#         return jsonify({"error": "Missing required fields"}), 400
    
#     # Check if user exists
#     existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
#     if existing_user:
#         return jsonify({"error": "Email or username already exists"}), 409
    
#     # Create new user
#     new_user = User(username=username, email=email, clerk_id=clerk_id)
#     db.session.add(new_user)
#     db.session.commit()
    
#     return jsonify({
#         "message": "User created successfully",
#         "user_id": new_user.id,
#         "username": new_user.username
#     }), 201

# # @app.route('/api/login', methods=['POST'])
# # def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
    
#     if not all([email, password]):
#         return jsonify({"error": "Email and password required"}), 400
    
#     user = User.query.filter_by(email=email).first()
    
#     if user and bcrypt.check_password_hash(user.password, password):
#         login_user(user)
#         return jsonify({
#             "message": "Login successful",
#             "user_id": user.id,
#             "username": user.username
#         }), 200
        
#     return jsonify({"error": "Invalid credentials"}), 401

# # @app.route('/api/logout', methods=['POST'])
# # @login_required
# # def logout():
#     logout_user()
#     return jsonify({"message": "Logged out successfully"}), 200

# # --------------------- Project CRUD Routes ---------------------
# @app.route('/api/projects/', methods=['POST'])
# # @login_required
# def create_project():
#     data = request.get_json()

#     required_fields = ['title', 'user_id']
#     missing = [field for field in required_fields if not data.get(field)]
#     if missing:
#         return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400


#     clerk_id = data.get("user_id")
#     user = User.query.filter_by(clerk_id=clerk_id).first()
#     if not user:
#         return jsonify({"error": "User not found"}), 404
    
#     new_project = Project(
#         title=data.get('title'),
#         client_name=data.get('client_name'),
#         contractor_name=data.get('contractor_name'),
#         currency=data.get('currency', 'USD'),
#         project_cost=data.get('project_cost'),
#         site_location=data.get('site_location'),
#         client_email=data.get('client_email'),
#         contractor_email=data.get('contractor_email'),
#         completion_date=datetime.fromisoformat(data['completion_date']) if data.get('completion_date') else None,
#         start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
#         progress=data.get('progress', 0),
#         user_id=user.clerk_id
#     )
    
#     db.session.add(new_project)
#     db.session.commit()
    
#     return jsonify({
#         "message": "Project created successfully",
#         "project_id": new_project.id
#     }), 201

# @app.route('/api/projects/', methods=['GET'])
# # @login_required
# def get_projects():
#     user = User()
#     projects = Project.query.filter_by(user_id=user.clerk_id).all()
#     return jsonify([p.to_dict() for p in projects]), 200

# @app.route('/api/projects/<int:project_id>/', methods=['GET'])
# # @login_required
# def get_project(project_id):
#     user = User()
#     project = Project.query.get_or_404(project_id)
#     if project.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403
#     return jsonify(project.to_dict()), 200

# @app.route('/api/projects/<int:project_id>/', methods=['PUT'])
# # @login_required
# def update_project(project_id):
#     user = User()
#     project = Project.query.get_or_404(project_id)
#     if project.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403
        
#     data = request.get_json()
    
#     # Update fields
#     project.title = data.get('title', project.title)
#     project.client_name = data.get('client_name', project.client_name)
#     project.contractor_name = data.get('contractor_name', project.contractor_name)
#     project.currency = data.get('currency', project.currency)
#     project.project_cost = data.get('project_cost', project.project_cost)
#     project.site_location = data.get('site_location', project.site_location)
#     project.client_email = data.get('client_email', project.client_email)
#     project.contractor_email = data.get('contractor_email', project.contractor_email)
#     project.progress = data.get('progress', project.progress)
    
#     if 'completion_date' in data:
#         project.completion_date = datetime.fromisoformat(data['completion_date'])
#     if 'start_date' in data:
#         project.start_date = datetime.fromisoformat(data['start_date'])
    
#     db.session.commit()
#     return jsonify(project.to_dict()), 200

# @app.route('/api/projects/<int:project_id>/', methods=['DELETE'])
# # @login_required
# def delete_project(project_id):
#     user = User()
#     project = Project.query.get_or_404(project_id)
#     if project.user_id != user.clerk_id:
#         return jsonify({"error": "Unauthorized"}), 403
        
#     db.session.delete(project)
#     db.session.commit()
#     return jsonify({"message": "Project deleted successfully"}), 200

# if __name__ == '__main__':
#     app.run(debug=True)



# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from models import db, bcrypt, User, Project

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Create tables before first request
with app.app_context():
    db.create_all()


# Helper: Get user from Clerk ID
def get_user_by_clerk_id(clerk_id):
    return User.query.filter_by(clerk_id=clerk_id).first()


# ------------------- Signup (for Clerk users) -------------------
@app.route('/api/signup/', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    clerk_id = data.get('clerk_id')

    if not all([username, email, clerk_id]):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(clerk_id=clerk_id).first()
    if existing_user:
        return jsonify({"message": "User already exists", "user_id": existing_user.clerk_id}), 200

    # Create new user
    new_user = User(username=username, email=email, clerk_id=clerk_id)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.clerk_id}), 201


# ------------------- Create Project -------------------
@app.route('/api/projects/', methods=['POST'])
def create_project():
    data = request.get_json()
    clerk_id = data.get('user_id')

    if not clerk_id:
        return jsonify({"error": "Missing Clerk user_id"}), 400

    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

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
        user_id=user.clerk_id
    )

    db.session.add(new_project)
    db.session.commit()

    return jsonify({"message": "Project created", "project_id": new_project.id}), 201


# ------------------- Get All Projects for a User -------------------
@app.route('/api/projects/', methods=['GET'])
def get_projects():
    clerk_id = request.args.get('user_id')
    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    projects = Project.query.filter_by(user_id=user.clerk_id).all()
    return jsonify([p.to_dict() for p in projects]), 200


# ------------------- Get/Update/Delete Individual Project -------------------
@app.route('/api/projects/<int:project_id>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(project_id):
    clerk_id = request.args.get('user_id')
    user = get_user_by_clerk_id(clerk_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    project = Project.query.get_or_404(project_id)

    if project.user_id != user.clerk_id:
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
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted"}), 200


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
