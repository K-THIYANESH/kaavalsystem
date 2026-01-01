"""Script to create an initial admin user."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_session
from app.models.user import Admin
from app.auth.security import get_password_hash


def create_admin(username: str, email: str, password: str, full_name: str, is_super: bool = False):
    """Create an admin user in the database."""
    with db_session() as session:
        existing = session.query(Admin).filter(
            (Admin.username == username) | (Admin.email == email)
        ).first()
        
        if existing:
            print(f"Admin with username '{username}' or email '{email}' already exists.")
            return False
        
        admin = Admin(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            is_super_admin=is_super,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f"Admin '{username}' created successfully!")
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--name", required=True, help="Full name")
    parser.add_argument("--super", action="store_true", help="Make super admin")
    
    args = parser.parse_args()
    
    create_admin(args.username, args.email, args.password, args.name, args.super)

