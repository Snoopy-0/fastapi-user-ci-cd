import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models, schemas, crud

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_db",
)

engine = create_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_calculation_persists_in_db():
    db = TestingSessionLocal()
    try:
        calc_in = schemas.CalculationCreate(
            a=10,
            b=5,
            type=schemas.CalculationType.sub,
        )
        calc = crud.create_calculation(db, calc_in)

        assert calc.id is not None
        assert calc.a == 10
        assert calc.b == 5
        assert calc.type == models.CalculationType.SUB
        assert calc.result == 5

        db_obj = db.query(models.Calculation).filter_by(id=calc.id).first()
        assert db_obj is not None
        assert db_obj.result == 5
    finally:
        db.close()
