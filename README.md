# FastAPI User Authentication with CI/CD

This project implements a **secure user management system** built with **FastAPI**, **SQLAlchemy**, and **Pydantic**, with password hashing and automated **CI/CD** using **GitHub Actions** and **Docker Hub**.

---

## Overview

This application provides:
- A secure user model (`username`, `email`, hashed password)
- A robust `Calculation` model with validated arithmetic operations (add/subtract/multiply/divide) and a factory that executes each operation
- Input validation using **Pydantic** for both users and calculations
- Password hashing and verification with **Passlib (bcrypt)**
- PostgreSQL database integration with **SQLAlchemy ORM**
- Unit and integration tests using **pytest**
- Automated testing and Docker deployment using **GitHub Actions**

---

## Local Setup

### 1️ Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

### 2️ Install dependencies

```bash 
pip install -r requirements.txt 
```

### 3️ Run the FastAPI app

```bash
uvicorn app.main:app --reload
```

### 4️ Open Swagger UI

Go to: http://127.0.0.1:8000/docs

---

## Running Tests Locally

### To run all tests with SQLite (default): 
```bash
pytest
```

The tests use **SQLite by default** for local development (no PostgreSQL required).

### Integration Tests with PostgreSQL:

If you want to test against PostgreSQL instead, make sure PostgreSQL is running locally and set:
```bash
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db pytest
```

> **Note**: If tests fail with PostgreSQL connection errors, make sure you don't have `TEST_DATABASE_URL` set in your shell environment. You can unset it with: `unset TEST_DATABASE_URL`

--- 

## Link to DockerHub repository:

Dockerhub repo: https://hub.docker.com/repository/docker/snoopy0/fastapi-user-ci-cd/general
