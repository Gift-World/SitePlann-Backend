import os
from flask import Flask, request, jsonify
from models import db, bcrypt, User, Project
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')


db.init_app(app)
bcrypt.init_app(app)
#  Change CORS During production
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Creating tables before first request incase there are no tables
with app.app_context():
    db.create_all()

# Getting user from Clerk ID
def get_user_by_clerk_id(clerk_id):
    return User.query.filter_by(clerk_id=clerk_id).first()

# # --------------Sign up process for clerk users-------------
@app.route('/api/signup/', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    clerk_id = data.get('clerk_id')
    
    if not all([username, email, clerk_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # # ------------------Checking if user exists
    existing_user = User.query.filter_by(clerk_id=clerk_id).first()
    if existing_user:
        return jsonify({"message": "User already exists", "user_id": existing_user.clerk_id}), 200
    
#     # --------------------Creating the new user after all checks have been made and requirements are fulfilled
    new_user = User(username=username, email=email, clerk_id=clerk_id)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully", "user_id": new_user.clerk_id}), 201


# # --------------------- Creating a new project ---------------------
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
    
    return jsonify({
        "message": "Project created successfully",
        "project_id": new_project.id
    }), 201

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


# -----------------------Other--------------------#

        # completion_date=datetime.fromisoformat(data['completion_date']) if data.get('completion_date') else None,
        # start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
