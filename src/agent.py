import os
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

load_dotenv()

AI_MODE = 'local'
def get_llm():
    if AI_MODE == "local":
        print("✅ Using LOCAL Ollama LLM")
        return ChatOllama(
            model="llama3:8b",
            temperature=0.5
        )
    
llm = get_llm()

class StepsTrackerAgent:
    def __init__(self):
        self.steps_history=[]

    def analyzer(self, no_of_steps, weight):
        prompt = f"""
    You are a personal health assistant,
    You will guide the user in their fitness journey.
    The user has taken {no_of_steps} steps and is currently of the weight
    {weight} kgs. Provide a status and suggest on how much more or less they should walk
    """
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content


agent = StepsTrackerAgent()
no_of_steps = 10000
weight = 60
answer = agent.analyzer(no_of_steps, weight)
print(f"Your Analysis:", {answer})
    