from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
from src.agent import StepsTrackerAgent
from src.database import log_steps, get_steps_history


app = FastAPI()
agent = StepsTrackerAgent()


class StepsTracker(BaseModel):
    user_id: str
    steps_taken : int
    weight : float


@app.post("/log-steps")
async def log_steps_taken(request:StepsTracker):
    log_steps(request.user_id,request.steps_taken,request.weight)
    analysis = agent.analyze_steps(request.steps_taken,request.weight)
    return {"message": "Steps and weight have been logged successfully", "analysis": analysis}


@app.get("/get-step-history/{user_id}")
async def get_history(user_id:str):
    history = get_steps_history(user_id)
    if not history:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id":user_id, "history":history}
