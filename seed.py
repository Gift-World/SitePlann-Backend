from app import app
from models import db, User, Project
from datetime import datetime, timedelta

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users
        users = [
            User(
                username="john_doe", 
                email="john@example.com", 
                password=bcrypt.generate_password_hash("Password123").decode('utf-8')
            ),
            User(
                username="jane_smith", 
                email="jane@example.com", 
                password=bcrypt.generate_password_hash("SecurePass456").decode('utf-8')
            ),
            User(
                username="bob_builder", 
                email="bob@example.com", 
                password=bcrypt.generate_password_hash("BuildIt789").decode('utf-8')
            )
        ]
        
        # Add users
        db.session.add_all(users)
        db.session.commit()
        
        # Create projects for each user
        projects = []
        today = datetime.now()
        
        # John's projects
        projects.append(Project(
            title="Office Tower Construction",
            client_name="Acme Corp",
            contractor_name="BuildRight Inc",
            currency="USD",
            project_cost=2500000,
            site_location="123 Main St, New York",
            client_email="contact@acme.com",
            contractor_email="info@buildright.com",
            start_date=today - timedelta(days=30),
            completion_date=today + timedelta(days=180),
            progress=35,
            user_id=users[0].id
        ))
        
        projects.append(Project(
            title="Residential Complex",
            client_name="Housing Authority",
            contractor_name="City Builders",
            currency="EUR",
            project_cost=1800000,
            site_location="456 Oak Ave, London",
            progress=15,
            user_id=users[0].id
        ))
        
        # Jane's projects
        projects.append(Project(
            title="Shopping Mall Renovation",
            client_name="Retail Group",
            contractor_name="Renovate Pro",
            currency="USD",
            project_cost=950000,
            site_location="789 Market St, Chicago",
            client_email="projects@retailgroup.com",
            start_date=today - timedelta(days=15),
            completion_date=today + timedelta(days=120),
            progress=60,
            user_id=users[1].id
        ))
        
        # Bob's projects
        projects.append(Project(
            title="Bridge Construction",
            client_name="City Council",
            contractor_name="InfraBuild Co",
            currency="USD",
            project_cost=4200000,
            site_location="Riverfront, Portland",
            client_email="engineering@city.gov",
            contractor_email="contact@infrabuild.com",
            start_date=today - timedelta(days=90),
            progress=85,
            user_id=users[2].id
        ))
        
        # Add projects
        db.session.add_all(projects)
        db.session.commit()
        
        print("Database seeded successfully!")
        print(f"Created {len(users)} users and {len(projects)} projects")

if __name__ == '__main__':
    seed_database()