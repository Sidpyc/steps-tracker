import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

load_dotenv()

def get_llm():
    print("Using LOCAL Ollama LLM")
    return ChatOllama(model="llama3:8b", temperature=0.3)

llm = get_llm()

LLM_PROMPT = """You are a strict, encouraging steps tracker assistant.
Daily goal: 10,000 steps
Always respond concisely, positively and motivationally.
Use units: steps, km (1 km ≈ 1250 steps), calories (1 step ≈ 0.04 kcal).
Current user weight: {weight} kg
Analyze honestly. Suggest realistic next actions."""

prompt = ChatPromptTemplate.from_messages([
    ("system", LLM_PROMPT),
    ("placeholder", "{messages}"),
])

class StepsTrackerAgent:
    def __init__(self):
        self.steps_history = []

    @tool
    def analyze_steps(self, steps_today: int) -> str:
        """Analyze today's steps and give suggestion"""
        # real logic / API call here
        return f"{steps_today} steps today → {max(0, 10000 - steps_today)} more needed."

agent = StepsTrackerAgent()
tools = [agent.analyze_steps]

chain = prompt | llm.bind_tools(tools)
