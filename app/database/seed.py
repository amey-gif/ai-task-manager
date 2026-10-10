from sqlalchemy import select

from app.auth.security import hash_password
from app.database.session import SessionLocal
from app.models import Role, Task, TaskStatus, User

SEED_USERS = [
    {"name": "Admin User", "email": "admin@example.com", "password": "Admin@12345", "role": Role.ADMIN.value},
    {"name": "Test User", "email": "user@example.com", "password": "User@12345", "role": Role.USER.value},
    {"name": "Second User", "email": "user2@example.com", "password": "User@12345", "role": Role.USER.value},
]

SEED_TASKS = {
    "user@example.com": [
        ("Set up project repository", "Create the repo and initial folder structure.", TaskStatus.COMPLETED),
        ("Design database schema", "Define users and tasks tables with relationships.", TaskStatus.IN_PROGRESS),
        ("Write API documentation", "Document all endpoints in the README.", TaskStatus.PENDING),
    ],
    "user2@example.com": [
        ("Prepare Postman collection", "Cover auth, task and AI endpoints.", TaskStatus.PENDING),
        ("Test role based access", "Verify users cannot edit other users' tasks.", TaskStatus.TESTING),
    ],
}


def seed() -> None:
    with SessionLocal() as db:
        for data in SEED_USERS:
            user = db.scalar(select(User).where(User.email == data["email"]))
            if user is None:
                user = User(
                    name=data["name"],
                    email=data["email"],
                    password=hash_password(data["password"]),
                    role=data["role"],
                )
                db.add(user)
                db.flush()  # assigns user.id without committing yet
                print(f"Created user: {user.email} ({user.role})")

            if data["email"] in SEED_TASKS and not user.tasks:
                for title, description, status in SEED_TASKS[data["email"]]:
                    db.add(Task(user_id=user.id, title=title, description=description, status=status.value))
                print(f"Created tasks for: {user.email}")
        db.commit()
    print("Seeding complete.")


if __name__ == "__main__":
    seed()