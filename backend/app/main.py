from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# In-memory "DB"
# -------------------
users_db = {}

# -------------------
# Models
# -------------------
class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


# -------------------
# Routes
# -------------------
@app.get("/")
def root():
    return {"message": "BiblioAI Running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": True,
        "ai_models": {"recommender": True},
    }


@app.post("/auth/register")
def register(user: RegisterRequest):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    users_db[user.email] = {
        "full_name": user.full_name,
        "password": user.password,
        "phone": user.phone,
    }

    return {"message": "User registered successfully"}


@app.post("/auth/login")
def login(data: LoginRequest):
    user = users_db.get(data.email)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": "demo-jwt-token",
        "token_type": "bearer",
    }
