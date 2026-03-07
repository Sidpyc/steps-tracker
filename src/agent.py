import requests  
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry # type: ignore
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

def get_llm():
    print("Using LOCAL Ollama LLM")
    return ChatOllama(model="llama3.1", temperature=0.3)

llm = get_llm()

LLM_PROMPT = """You are a strict, encouraging steps tracker assistant.
Daily goal: 10,000 steps
Always respond concisely, positively and motivationally.
Analyze honestly. Suggest realistic next actions."""

Context = ChatPromptTemplate.from_messages([
    ("system", LLM_PROMPT),
    ("placeholder", "{messages}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

class StepsTrackerAgent:
    # Class-level constant (recommended when no instance state is needed)
    API_BASE = "http://localhost:8000"  # Changed to localhost; revert to 127.0.0.1 if needed

    def __init__(self):
        self.steps_history = []
        self.weight_history = []

    def analyze_steps(self, steps_taken, weight):
        prompt = f"""You are a steps analyze assistant. The user has taken {steps_taken} steps and weighs {weight} kg today.
        Provide a status and suggest if the person has made good progress."""
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

    @staticmethod
    @tool
    def suggestion(user_id: str, query: str = "") -> str:
        """
        Retrieve the step history for the specified user from the API.
        Returns latest entry info, total history days, and a preview of the raw JSON data.
        """
        try:
            print(f"Attempting to fetch from {StepsTrackerAgent.API_BASE}/get-step-history/{user_id}")
            
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            resp = session.get(
                f"{StepsTrackerAgent.API_BASE}/get-step-history/{user_id}",
                timeout=60.0,
                proxies=None
            )
            resp.raise_for_status()
            data = resp.json()

            history = data.get("history", [])
            if not history:
                return "No step history found."

            latest_entry = history[-1]  # most recent = last item

            if not isinstance(latest_entry, list) or len(latest_entry) < 2:
                return f"Unexpected entry format in history. Raw: {str(data)}"

            steps = int(latest_entry[0])          # first value = steps
            weight = float(latest_entry[1])       # second value = weight

            
            summary = (
                f"Latest entry (today): {steps} steps\n"
                f"Recorded weight: {weight} kg\n"
                f"Full history length: {len(history)} entries\n"
                f"Raw data preview: {str(data)[:300]}..."
            )

            print("Fetch successful")
            return summary

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch: {str(e)}"
            print(error_msg)
            return error_msg
        except Exception as e:
            return f"Processing error: {str(e)} - Raw response: {str(data) if 'data' in locals() else 'no data'}"


if __name__ == "__main__":
    agent_instance = StepsTrackerAgent()

    tools = [StepsTrackerAgent.suggestion]

    agent = create_tool_calling_agent(llm, tools, Context)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke({
        "messages": [HumanMessage(content="Analyze my steps for user Yuktheswar")]
    })

    print(result["output"])