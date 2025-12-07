from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator, List, Optional

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Header,
    status,
)
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import SessionLocal, engine, Base
from . import schemas, crud, models
from .security import SECRET_KEY, ALGORITHM, create_access_token

# App & DB setup

Base.metadata.create_all(bind=engine)

app = FastAPI()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth helper

def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
) -> models.User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.split()[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        user_id = int(sub)
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# Static pages

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(FRONTEND_DIR / "login.html")

@app.get("/register", include_in_schema=False)
def serve_register_page():
    return FileResponse(FRONTEND_DIR / "register.html")

@app.get("/login", include_in_schema=False)
def serve_login_page():
    return FileResponse(FRONTEND_DIR / "login.html")

@app.get("/calculations.html", include_in_schema=False)
def serve_calculations_page():
    return FileResponse(FRONTEND_DIR / "calculations.html")

# User helpers (shared logic)

def _register_user_impl(user_in: schemas.UserCreate, db: Session) -> schemas.UserRead:
    """Shared logic for user registration."""
    if crud.get_user_by_username(db, user_in.username) or crud.get_user_by_email(
        db, user_in.email
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that username or email already exists",
        )

    user = crud.create_user(db, user_in)
    access_token = create_access_token(str(user.id))

    return schemas.UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        access_token=access_token,
    )

def _login_user_impl(login_in: schemas.UserLogin, db: Session) -> schemas.UserRead:
    user = crud.authenticate_user(
        db,
        identifier=login_in.identifier,
        password=login_in.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )

    access_token = create_access_token(str(user.id))

    return schemas.UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        access_token=access_token,
    )

# User API endpoints

@app.post(
    "/users/register",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user_api(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    return _register_user_impl(user_in, db)

@app.post("/users/login", response_model=schemas.UserRead)
def login_user_api(
    login_in: schemas.UserLogin,
    db: Session = Depends(get_db),
):
    return _login_user_impl(login_in, db)

@app.post(
    "/register",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user_html(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    return _register_user_impl(user_in, db)

@app.post("/login", response_model=schemas.UserRead)
def login_user_html(
    login_in: schemas.UserLogin,
    db: Session = Depends(get_db),
):
    return _login_user_impl(login_in, db)

# Calculation BREAD endpoints (per user)

@app.post(
    "/calculations",
    response_model=schemas.CalculationRead,
    status_code=status.HTTP_201_CREATED,
)
def add_calculation(
    calc_in: schemas.CalculationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    calc = crud.create_calculation(db, calc_in, user_id=current_user.id)
    return calc

@app.get(
    "/calculations",
    response_model=List[schemas.CalculationRead],
)
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    calcs = crud.get_calculations_for_user(db, user_id=current_user.id)
    return calcs

@app.get(
    "/calculations/{calc_id}",
    response_model=schemas.CalculationRead,
)
def read_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    calc = crud.get_calculation(db, calc_id, user_id=current_user.id)
    if calc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    return calc

@app.put(
    "/calculations/{calc_id}",
    response_model=schemas.CalculationRead,
)
@app.patch(
    "/calculations/{calc_id}",
    response_model=schemas.CalculationRead,
)
def edit_calculation(
    calc_id: int,
    calc_in: schemas.CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    calc = crud.update_calculation(
        db,
        calc_id,
        calc_in,
        user_id=current_user.id,
    )
    if calc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    return calc

@app.delete(
    "/calculations/{calc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ok = crud.delete_calculation(db, calc_id, user_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    return None
