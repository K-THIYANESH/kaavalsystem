"""Load demo data into the database for testing and demonstration."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_session
from app.models.user import User, Admin, MissingPersonReport, FoundPersonReport
from app.models.person import Person
from app.models.embedding import Embedding
from app.auth.security import get_password_hash


def create_demo_users():
    """Create demo user accounts."""
    with db_session() as session:
        # Demo user 1
        user1 = session.query(User).filter(User.email == "demo@kaaval.com").first()
        if not user1:
            user1 = User(
                email="demo@kaaval.com",
                name="Demo User",
                phone="+1234567890",
                password_hash=get_password_hash("demo123"),
                is_active=True,
            )
            session.add(user1)
            print("✓ Created demo user: demo@kaaval.com / demo123")

        # Demo user 2
        user2 = session.query(User).filter(User.email == "reporter@kaaval.com").first()
        if not user2:
            user2 = User(
                email="reporter@kaaval.com",
                name="John Reporter",
                phone="+1987654321",
                password_hash=get_password_hash("reporter123"),
                is_active=True,
            )
            session.add(user2)
            print("✓ Created demo user: reporter@kaaval.com / reporter123")

        session.commit()


def create_demo_admin():
    """Create demo admin account."""
    with db_session() as session:
        admin = session.query(Admin).filter(Admin.username == "admin").first()
        if not admin:
            admin = Admin(
                username="admin",
                email="admin@kaaval.com",
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_super_admin=True,
            )
            session.add(admin)
            session.commit()
            print("✓ Created demo admin: admin / admin123")
        else:
            print("✓ Admin already exists")


def create_demo_persons():
    """Create demo missing persons in the database."""
    demo_persons = [
        {
            "name": "Sarah Johnson",
            "age": 28,
            "gender": "female",
            "ethnicity": "Caucasian",
            "hair_color": "blonde",
            "skin_tone": "fair",
            "eye_color": "blue",
            "missing_since": "2024-01-15",
            "description": "Last seen wearing blue jeans and white t-shirt. Has a small scar on left cheek.",
            "photo_path": "demo/sarah_johnson.jpg",
        },
        {
            "name": "Michael Chen",
            "age": 35,
            "gender": "male",
            "ethnicity": "Asian",
            "hair_color": "black",
            "skin_tone": "medium",
            "eye_color": "brown",
            "missing_since": "2024-01-20",
            "description": "Wearing black jacket. Has tattoo on right arm. Last seen at downtown area.",
            "photo_path": "demo/michael_chen.jpg",
        },
        {
            "name": "Emma Rodriguez",
            "age": 22,
            "gender": "female",
            "ethnicity": "Hispanic",
            "hair_color": "brown",
            "skin_tone": "olive",
            "eye_color": "brown",
            "missing_since": "2024-01-18",
            "description": "Long brown hair, wearing red dress. Last seen at shopping mall.",
            "photo_path": "demo/emma_rodriguez.jpg",
        },
        {
            "name": "David Williams",
            "age": 45,
            "gender": "male",
            "ethnicity": "African American",
            "hair_color": "black",
            "skin_tone": "deep",
            "eye_color": "brown",
            "missing_since": "2024-01-22",
            "description": "Bald, wearing glasses. Has beard. Last seen at park.",
            "photo_path": "demo/david_williams.jpg",
        },
        {
            "name": "Lisa Anderson",
            "age": 19,
            "gender": "female",
            "ethnicity": "Caucasian",
            "hair_color": "red",
            "skin_tone": "fair",
            "eye_color": "green",
            "missing_since": "2024-01-25",
            "description": "Short red hair, freckles. Wearing green hoodie. Last seen at university campus.",
            "photo_path": "demo/lisa_anderson.jpg",
        },
    ]

    with db_session() as session:
        for person_data in demo_persons:
            existing = session.query(Person).filter(Person.name == person_data["name"]).first()
            if not existing:
                person = Person(**person_data)
                session.add(person)
                print(f"✓ Created demo person: {person_data['name']}")
        session.commit()


def create_demo_reports():
    """Create demo missing person reports."""
    demo_reports = [
        {
            "reporter_name": "Jane Smith",
            "reporter_phone": "+1555123456",
            "reporter_email": "jane.smith@example.com",
            "person_name": "Sarah Johnson",
            "person_age": 28,
            "person_gender": "female",
            "last_seen_location": "Central Park, New York",
            "last_seen_date": "2024-01-15",
            "description": "My sister Sarah went missing after leaving work. She was last seen at Central Park around 6 PM. Please help us find her.",
            "status": "pending",
        },
        {
            "reporter_name": "Robert Chen",
            "reporter_phone": "+1555987654",
            "reporter_email": "robert.chen@example.com",
            "person_name": "Michael Chen",
            "person_age": 35,
            "person_gender": "male",
            "last_seen_location": "Downtown District, Main Street",
            "last_seen_date": "2024-01-20",
            "description": "My brother Michael hasn't been seen since Monday. He was supposed to meet me but never showed up.",
            "status": "pending",
        },
        {
            "reporter_name": "Maria Rodriguez",
            "reporter_phone": "+1555555555",
            "reporter_email": "maria.rodriguez@example.com",
            "person_name": "Emma Rodriguez",
            "person_age": 22,
            "person_gender": "female",
            "last_seen_location": "Westfield Shopping Mall",
            "last_seen_date": "2024-01-18",
            "description": "My daughter Emma disappeared while shopping. Security cameras show her leaving the mall alone.",
            "status": "pending",
        },
        {
            "reporter_name": "Patricia Williams",
            "reporter_phone": "+1555444333",
            "reporter_email": "patricia.williams@example.com",
            "person_name": "David Williams",
            "person_age": 45,
            "person_gender": "male",
            "last_seen_location": "Riverside Park",
            "last_seen_date": "2024-01-22",
            "description": "My husband David went for his daily walk and never returned. He usually walks in the park every evening.",
            "status": "pending",
        },
        {
            "reporter_name": "Thomas Anderson",
            "reporter_phone": "+1555666777",
            "reporter_email": "thomas.anderson@example.com",
            "person_name": "Lisa Anderson",
            "person_age": 19,
            "person_gender": "female",
            "last_seen_location": "State University Campus",
            "last_seen_date": "2024-01-25",
            "description": "My daughter Lisa is a student. She didn't return to her dorm after classes. This is very unlike her.",
            "status": "pending",
        },
    ]

    with db_session() as session:
        for report_data in demo_reports:
            # Check if report already exists
            existing = (
                session.query(MissingPersonReport)
                .filter(MissingPersonReport.person_name == report_data["person_name"])
                .first()
            )
            if not existing:
                report = MissingPersonReport(**report_data)
                session.add(report)
                print(f"✓ Created demo report for: {report_data['person_name']}")
        session.commit()


def create_demo_embeddings():
    """Create demo embeddings for persons (placeholder vectors)."""
    import numpy as np

    with db_session() as session:
        persons = session.query(Person).all()
        for person in persons:
            existing = session.query(Embedding).filter(Embedding.person_id == person.id).first()
            if not existing:
                # Create a dummy 512-d embedding vector
                embedding_vector = np.random.rand(512).astype(np.float32).tobytes()
                embedding = Embedding(
                    person_id=person.id,
                    embedding=embedding_vector,
                )
                session.add(embedding)
                print(f"✓ Created demo embedding for: {person.name}")
        session.commit()


def main():
    """Load all demo data."""
    print("=" * 60)
    print("KAAVAL Demo Data Loader")
    print("=" * 60)
    print()

    print("Creating demo users...")
    create_demo_users()
    print()

    print("Creating demo admin...")
    create_demo_admin()
    print()

    print("Creating demo persons...")
    create_demo_persons()
    print()

    print("Creating demo reports...")
    create_demo_reports()
    print()

    print("Creating demo embeddings...")
    create_demo_embeddings()
    print()

    print("=" * 60)
    print("✓ Demo data loaded successfully!")
    print("=" * 60)
    print()
    print("Demo Credentials:")
    print("  User: demo@kaaval.com / demo123")
    print("  User: reporter@kaaval.com / reporter123")
    print("  Admin: admin / admin123")
    print()


if __name__ == "__main__":
    main()

