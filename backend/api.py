from fastapi import FastAPI
from pydantic import BaseModel

from orchestrator import run_all_agents


app = FastAPI(
    title="Multi-Agent AI Decision System",
    description="AI-powered multi-domain feasibility analysis system",
    version="1.0.0"
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
            "error": "Problem statement cannot be empty."
        }

    result = run_all_agents(request.problem)

    return result