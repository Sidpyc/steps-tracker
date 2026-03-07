import httpx
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor


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

Context = ChatPromptTemplate.from_messages([
    ("system", LLM_PROMPT),
    ("placeholder", "{messages}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

class StepsTrackerAgent:
    def __init__(self):
        self.steps_history = []
        self.api_base = "http://127.0.0.1:8000"

    def analyze_steps(self,steps_taken,weight):

        prompt = f""" You are a steps analyze assistant , The use has taken {steps_taken} steps and is of weight {weight} kg today
        provide a status and suggest if the person has made good progress """

        response = llm.invoke([HumanMessage(content = prompt)])
        return response.content

    @tool
    def suggestion(self, user_id: str, query: str = "") -> str:
        """
        Fetch user's step history from API.
        Return raw data + very brief summary.
        Do NOT assume any fixed goal — goal comes from user query/context.
        """
        try:
            with httpx.Client(timeout=6.0) as client:
                url = f"{self.api_base}/get-step-history/{user_id}"
                resp = client.get(url)
                resp.raise_for_status()
                data = resp.json()

            history = data.get("history", [])
            if not history:
                return "No step history found."

            # Minimal processing — let LLM decide goal / suggestion
            latest = history[-1] if history else {}
            today_steps = latest.get("steps", 0)
            date = latest.get("date", "today")

            summary = (
                f"Latest entry ({date}): {today_steps} steps\n"
                f"Full history length: {len(history)} days\n"
                f"Raw data: {str(data)}"
            )

            return summary

        except httpx.HTTPStatusError as e:
            return f"API error: {e.response.status_code}"
        except Exception as e:
            return f"Failed to fetch: {str(e)}"
        

agent = StepsTrackerAgent()
tools = [agent.suggestion]

chain = Context | llm.bind_tools(tools)

agent = create_tool_calling_agent(llm, tools, Context)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({
    "messages": [HumanMessage(content="Analyze my steps for user Yuktheswar")]
})
print(result["output"])
