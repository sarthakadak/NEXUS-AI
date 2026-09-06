from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from orchestrator import run_all_agents


app = FastAPI(
    title="Multi-Agent AI Decision System",
    description="AI-powered multi-domain feasibility analysis system",
    version="1.0.0"
)


# =========================
# CORS CONFIGURATION
# =========================

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


@app.get("/")
def root():
    return {
        "message": "Multi-Agent AI Decision System is running",
        "status": "online"
    }


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