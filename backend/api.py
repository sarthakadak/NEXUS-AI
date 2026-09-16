from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from orchestrator import run_all_agents
import auth

auth.init_db()

app = FastAPI(
    title="Multi-Agent AI Decision System",
    description="AI-powered multi-domain feasibility analysis system",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProblemRequest(BaseModel):
    problem: str


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/")
def root():
    return {
        "message": "Multi-Agent AI Decision System is running",
        "status": "online"
    }


@app.post("/signup")
def signup(request: SignupRequest):
    if not request.email.strip() or not request.password.strip():
        return {"success": False, "error": "Email and password are required."}
    if len(request.password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}

    result = auth.create_user(request.email.strip().lower(), request.password, request.name.strip())
    return result


@app.post("/login")
def login(request: LoginRequest):
    if not request.email.strip() or not request.password.strip():
        return {"success": False, "error": "Email and password are required."}

    result = auth.verify_user(request.email.strip().lower(), request.password)
    return result


@app.get("/me")
def me(authorization: str = Header(default="")):
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return {"success": False, "error": "No token provided."}

    user = auth.get_user_from_token(token)
    if not user:
        return {"success": False, "error": "Invalid or expired session."}

    return {"success": True, "user": user}


@app.post("/analyze")
def analyze_problem(request: ProblemRequest):

    if not request.problem.strip():
        return {
            "success": False,
            "error": "Problem statement cannot be empty."
        }

    print("\n========================================")
    print("NEW ANALYSIS REQUEST")
    print("========================================")
    print(request.problem)

    result = run_all_agents(request.problem)

    return {
        "success": True,
        "problem": request.problem,
        "result": result
    }