from sqlalchemy.orm import Session
from . import models, schemas, security
from .calculations import execute_calculation

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_pw = security.hash_password(user_in.password)
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pw,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_calculation(db: Session, calc_in: schemas.CalculationCreate) -> models.Calculation:
    result = execute_calculation(calc_in.type, calc_in.a, calc_in.b)
    db_calc = models.Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=calc_in.type,
        result=result,
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc
