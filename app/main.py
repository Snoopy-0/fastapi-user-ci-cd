from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from .database import SessionLocal, engine, Base
from . import schemas, crud, security

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

@app.post(
    "/register",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # uniqueness checks
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = crud.create_user(db, user_in)
    access_token = security.create_access_token(str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post(
    "/login",
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK,
)
def login(login_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, login_in.identifier, login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = security.create_access_token(str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/register", include_in_schema=False)
def serve_register_page():
    return FileResponse(FRONTEND_DIR / "register.html")

@app.get("/login", include_in_schema=False)
def serve_login_page():
    return FileResponse(FRONTEND_DIR / "login.html")

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