# FastAPI User Authentication with CI/CD

This project implements a **secure user management system** built with **FastAPI**, **SQLAlchemy**, and **Pydantic**, with password hashing and automated **CI/CD** using **GitHub Actions** and **Docker Hub**.

---

## Overview

This application provides a simple user model with:
- `username`, `email`, and hashed password fields  
- Input validation using **Pydantic**  
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

Go to:http://127.0.0.1:8000/docs