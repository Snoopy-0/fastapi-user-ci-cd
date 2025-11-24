from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .database import SessionLocal, engine, Base
from . import schemas, crud

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post(
    "/users/register",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # uniqueness checks
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = crud.create_user(db, user_in)
    return user

@app.post(
    "/users/login",
    response_model=schemas.UserRead,
    status_code=status.HTTP_200_OK,
)
def login_user(login_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_in.identifier, login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )
    return user

@app.get(
    "/calculations",
    response_model=List[schemas.CalculationRead],
    status_code=status.HTTP_200_OK,
)
def browse_calculations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    calcs = crud.get_calculations(db, skip=skip, limit=limit)
    return calcs

@app.get(
    "/calculations/{calc_id}",
    response_model=schemas.CalculationRead,
    status_code=status.HTTP_200_OK,
)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = crud.get_calculation(db, calc_id)
    if calc is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc

@app.post(
    "/calculations",
    response_model=schemas.CalculationRead,
    status_code=status.HTTP_201_CREATED,
)
def add_calculation(
    calc_in: schemas.CalculationCreate,
    db: Session = Depends(get_db),
):
    calc = crud.create_calculation(db, calc_in, user_id=None)
    return calc

@app.put(
    "/calculations/{calc_id}",
    response_model=schemas.CalculationRead,
    status_code=status.HTTP_200_OK,
)
def edit_calculation(
    calc_id: int,
    calc_in: schemas.CalculationCreate,
    db: Session = Depends(get_db),
):
    calc = crud.update_calculation(db, calc_id, calc_in, user_id=None)
    if calc is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc

@app.delete(
    "/calculations/{calc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_calculation(db, calc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return None