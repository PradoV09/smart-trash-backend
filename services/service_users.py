from models.model_users import User
from schemas.schema_users import UserCreate
from sqlalchemy.orm import Session
from utils.security import hash_password

def get_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise ValueError("El email ya está registrado")

    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user