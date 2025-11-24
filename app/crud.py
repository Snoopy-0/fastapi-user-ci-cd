from sqlalchemy.orm import Session

from . import models, schemas, security
from .calculation_factory import get_operation

# User CRUD
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

# Calculation CRUD
def create_calculation(
    db: Session,
    calc_in: schemas.CalculationCreate,
    user_id: int | None = None,
) -> models.Calculation:
    if calc_in.type == schemas.CalculationType.divide and calc_in.b == 0:
        raise ValueError("Division by zero is not allowed")

    operation = get_operation(calc_in.type.value)
    result = operation.calculate(calc_in.a, calc_in.b)

    model_calc_type = models.CalculationType[calc_in.type.name.upper()]

    db_calc = models.Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=model_calc_type,
        result=result,
        user_id=user_id,
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc

def authenticate_user(db: Session, identifier: str, password: str):
    if "@" in identifier:
        user = get_user_by_email(db, identifier)
        if user is None:
            user = get_user_by_username(db, identifier)
    else:
        user = get_user_by_username(db, identifier)
        if user is None:
            user = get_user_by_email(db, identifier)

    if user is None:
        return None

    if not security.verify_password(password, user.password_hash):
        return None

    return user

def get_calculation(db: Session, calc_id: int) -> models.Calculation | None:
    return db.query(models.Calculation).filter(models.Calculation.id == calc_id).first()

def get_calculations(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Calculation)
        .order_by(models.Calculation.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_calculation(
    db: Session,
    calc_id: int,
    calc_in: schemas.CalculationCreate,
    user_id: int | None = None,
) -> models.Calculation | None:
    db_calc = get_calculation(db, calc_id)
    if db_calc is None:
        return None

    operation = get_operation(calc_in.type.value if hasattr(calc_in.type, "value") else str(calc_in.type))
    result = operation.calculate(calc_in.a, calc_in.b)

    model_calc_type = models.CalculationType[calc_in.type.name.upper()]

    db_calc.a = calc_in.a
    db_calc.b = calc_in.b
    db_calc.type = model_calc_type
    db_calc.result = result
    if user_id is not None:
        db_calc.user_id = user_id

    db.commit()
    db.refresh(db_calc)
    return db_calc

def delete_calculation(db: Session, calc_id: int) -> bool:
    db_calc = get_calculation(db, calc_id)
    if db_calc is None:
        return False

    db.delete(db_calc)
    db.commit()
    return True