from fastapi import FastAPI
from pydantic import BaseModel
from src.agent import StepsTrackerAgent
from src.logger import log_error, log_message


app = FastAPI()
agent  = StepsTrackerAgent

class StepsTrackerAgent(BaseModel):    
    user_id:str
    steps:int
    weight:float



    