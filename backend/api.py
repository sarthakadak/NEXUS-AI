from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from orchestrator import run_all_agents
import auth
import history

auth.init_db()
history.init_history_table()

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

GOOGLE_CLIENT_ID = "591855603162-98h9g3d28r4ccrrg2g0h7eapclrni16b.apps.googleusercontent.com"


class ProblemRequest(BaseModel):
    problem: str


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    credential: str


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


@app.post("/google-login")
def google_login(request: GoogleLoginRequest):
    try:
        idinfo = id_token.verify_oauth2_token(
            request.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        return {"success": False, "error": "Invalid Google token."}

    email = idinfo.get("email", "").lower()
    name = idinfo.get("name", "")

    if not email:
        return {"success": False, "error": "Google account has no email."}

    result = auth.get_or_create_google_user(email, name)
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


def _get_user(authorization: str):
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    return auth.get_user_from_token(token)


@app.post("/analyze")
def analyze_problem(request: ProblemRequest, authorization: str = Header(default="")):

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

    # Save to the database only if the user is logged in
    analysis_id = None
    user = _get_user(authorization)
    if user:
        analysis_id = history.save_analysis(user["id"], request.problem, result)

    return {
        "success": True,
        "problem": request.problem,
        "analysis_id": analysis_id,
        "result": result
    }


@app.get("/history")
def get_history(authorization: str = Header(default="")):
    user = _get_user(authorization)
    if not user:
        return {"success": False, "error": "Please log in."}
    return {"success": True, "history": history.list_analyses(user["id"])}


@app.get("/history/{analysis_id}")
def get_one_history(analysis_id: str, authorization: str = Header(default="")):
    user = _get_user(authorization)
    if not user:
        return {"success": False, "error": "Please log in."}
    item = history.get_analysis(user["id"], analysis_id)
    if not item:
        return {"success": False, "error": "Analysis not found."}
    return {"success": True, "analysis": item}


@app.delete("/history/{analysis_id}")
def delete_history(analysis_id: str, authorization: str = Header(default="")):
    user = _get_user(authorization)
    if not user:
        return {"success": False, "error": "Please log in."}
    if not history.delete_analysis(user["id"], analysis_id):
        return {"success": False, "error": "Analysis not found."}
    return {"success": True}