import requests  
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore
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
    API_BASE = "http://localhost:8000"
    session = None  # Class-level session (shared, setup once)

    def __init__(self):
        self.steps_history = []
        self.weight_history = []
        # No need to call setup here — it's done once at class level

    @classmethod
    def _setup_connection(cls):
        """Separate class-level method to set up the backend connection session with retries (called once)."""
        cls.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        cls.session.mount('http://', adapter)
        cls.session.mount('https://', adapter)

    @staticmethod
    @tool
    def backend_call(method: str = "GET", endpoint: str = "", user_id: str = "", json_body: dict = None) -> str:
        """
        Call any endpoint on the steps-tracker backend API based on query intent/context.

        IMPORTANT RULES:
        - Do NOT invent or guess endpoint names—only use the EXACT ones listed below.
        - Infer the best endpoint from the user's intent/context (not something made up).
        - If no exact match for the intent, use the closest one or respond without calling if not needed.
        - For expansion: New endpoints can be added here in the future without code changes.

        Known endpoints and what do they do 
        - GET /get-step-history/{user_id}: To get specific user history of one person 
        - POST /log-steps: Use when the user wants to add or log new steps/weight (e.g., "I walked 12000 steps today").

        Arguments:
        - method: HTTP method ("GET", "POST", "PUT", ...)
        - endpoint: API path—must be one from the list above.
        - user_id: User identifier (used to replace {user_id} in path if present).
        - params: Optional query parameters (dict).
        - json_body: Optional JSON body for POST/PUT (dict).

        Returns raw JSON string or error message. Parse it in your reasoning.
        """
        if not endpoint:
            return "Error: endpoint is required"

        try:
            # Use the class-level session (no local creation)
            url = f"{StepsTrackerAgent.API_BASE}{endpoint}"
            if "{user_id}" in url and user_id:
                url = url.format(user_id=user_id)

            kwargs = {
                "timeout": 60.0,
                "proxies": None
            }
            if json_body:
                kwargs["json"] = json_body

            method_upper = method.upper()
            if method_upper == "GET":
                resp = StepsTrackerAgent.session.get(url, **kwargs)
            elif method_upper == "POST":
                resp = StepsTrackerAgent.session.post(url, **kwargs)
            elif method_upper == "PUT":
                resp = StepsTrackerAgent.session.put(url, **kwargs)
            else:
                return f"Unsupported HTTP method: {method}"

            resp.raise_for_status()
            data = resp.json()

            
            return str(data)

        except requests.exceptions.RequestException as e:
            return f"Request failed: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

# Setup the class-level session once (after class definition)
StepsTrackerAgent._setup_connection()

if __name__ == "__main__":
    agent_instance = StepsTrackerAgent()

    # Use the static method directly via the class name
    tools = [StepsTrackerAgent.backend_call]

    agent = create_tool_calling_agent(llm, tools, Context)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke({
        "messages": [HumanMessage(content="Analyze the steps of different users Yuktheswar and Siddharth")]
    })

    print(result["output"]) 