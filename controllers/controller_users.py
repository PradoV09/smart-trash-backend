from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.connection import get_db
from schemas.schema_users import UserCreate, ResponseUser
from services.service_users import get_users, create_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[ResponseUser])
def list_users(db: Session = Depends(get_db)):
    return get_users(db)

@router.post("/", response_model=ResponseUser, status_code=201)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))