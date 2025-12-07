from sqlalchemy.orm import Session

from . import models, schemas, security
from .calculation_factory import get_operation

# User CRUD

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    password_hash = security.hash_password(user_in.password)

    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=password_hash,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(
    db: Session,
    identifier: str,
    password: str,
) -> models.User | None:
    user = (
        db.query(models.User)
        .filter(
            (models.User.username == identifier)
            | (models.User.email == identifier)
        )
        .first()
    )
    if not user:
        return None

    if not security.verify_password(password, user.password_hash):
        return None

    return user

# Calculation CRUD

def _normalize_calc_type(type_value) -> str:
    if hasattr(type_value, "value"):
        return type_value.value
    return str(type_value)

def create_calculation(
    db: Session,
    calc_in: schemas.CalculationCreate,
    user_id: int | None = None,
) -> models.Calculation:
    calc_type_str = _normalize_calc_type(calc_in.type)
    op = get_operation(calc_type_str)
    result = op.calculate(calc_in.a, calc_in.b)

    db_calc = models.Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=models.CalculationType(calc_type_str),
        result=result,
        user_id=user_id,
    )

    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc


def get_calculation(
    db: Session,
    calc_id: int,
    user_id: int | None = None,
) -> models.Calculation | None:
    query = db.query(models.Calculation).filter(models.Calculation.id == calc_id)
    if user_id is not None:
        query = query.filter(models.Calculation.user_id == user_id)
    return query.first()

def get_calculations_for_user(
    db: Session,
    user_id: int | None = None,
) -> list[models.Calculation]:
    query = db.query(models.Calculation)
    if user_id is not None:
        query = query.filter(models.Calculation.user_id == user_id)
    return query.order_by(models.Calculation.id).all()

def update_calculation(
    db: Session,
    calc_id: int,
    calc_in: schemas.CalculationUpdate,
    user_id: int | None = None,
) -> models.Calculation | None:
    db_calc = get_calculation(db, calc_id, user_id=user_id)
    if db_calc is None:
        return None

    if calc_in.a is not None:
        db_calc.a = calc_in.a
    if calc_in.b is not None:
        db_calc.b = calc_in.b
    if calc_in.type is not None:
        db_calc.type = models.CalculationType(_normalize_calc_type(calc_in.type))

    calc_type_str = _normalize_calc_type(db_calc.type)
    op = get_operation(calc_type_str)
    db_calc.result = op.calculate(db_calc.a, db_calc.b)

    db.commit()
    db.refresh(db_calc)
    return db_calc

def delete_calculation(
    db: Session,
    calc_id: int,
    user_id: int | None = None,
) -> bool:
    db_calc = get_calculation(db, calc_id, user_id=user_id)
    if db_calc is None:
        return False

    db.delete(db_calc)
    db.commit()
    return True
