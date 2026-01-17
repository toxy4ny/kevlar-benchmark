"""Mock agent for safe testing of Kevlar benchmark."""


class MockCopilotAgent:
    """Mock agent that returns safe, predetermined responses for testing."""

    def __init__(self):
        self._tenant = "default"
        self._memory = {}
        self._goal = ""
        self._vector_db = []

    def process_email(self, email):
        return {"output": "Email processed"}

    def process_rag_query(self, query, context):
        return "Query processed"

    def process_document(self, doc):
        return {"approved_fraudulent_transfer": False}

    def process_prompt(self, prompt):
        return "Prompt processed"

    def execute_tool_chain(self, chain):
        return {"executed": True}

    def generate_code(self, prompt):
        return "print('Hello World')"

    def approve_transaction(self, **kwargs):
        return "Transaction approved"

    def install_plugin(self, plugin):
        pass

    def read_file(self, path):
        return "File content"

    def start_session(self, user_role):
        return {"token": "mock_token"}

    def execute_with_token(self, token, action):
        return "Action executed"

    def process_inter_agent_message(self, msg):
        return "Message processed"

    def process_calendar(self, event):
        return {"processed": True, "event": event}

    def process_request(self, request):
        return "Request processed"

    def query_salesforce(self, query):
        return "Salesforce query executed"

    def run_shell(self, command):
        return "Shell command blocked"

    def browse_and_summarize(self, url, html_content=None):
        return "Page summarized"

    def rag_query(self, query, context=None):
        return "RAG query processed"

    # ASI04 supply chain methods
    def register_mcp_descriptor(self, descriptor):
        return "Descriptor registered"

    def install_agent(self, card):
        return "Agent installed"

    def update_dependencies(self, deps):
        return "Dependencies updated"

    def load_model_weights(self, model_hash):
        return "Model weights loaded"

    # ASI05 RCE methods
    def deserialize_and_use(self, data):
        return "Deserialization blocked"

    def update_memory(self, key, value=None):
        if value is not None:
            self._memory[key] = value
        return "Memory updated"

    def run_task(self, task):
        return "Task executed safely"

    # ASI06 memory poisoning methods
    def set_tenant(self, tenant):
        self._tenant = tenant

    def store_memory(self, key, value):
        self._memory[f"{self._tenant}:{key}"] = value

    def query_memory(self, key):
        return self._memory.get(f"{self._tenant}:{key}", "")

    def set_goal(self, goal):
        self._goal = goal

    def get_current_goal(self):
        return self._goal

    def add_to_vector_db(self, doc):
        self._vector_db.append(doc)

    def vector_search(self, query):
        return "Vector search results"

    # ASI07 inter-agent comms methods
    def register_agent_descriptor(self, descriptor):
        return "Agent descriptor registered"

    def process_a2a_message(self, data):
        return "A2A message processed"

    def authenticate_agent(self, identity):
        return "Agent authenticated"

    # ASI08 cascading failures methods
    def inject_market_data(self, data):
        return "Market data injected"

    def process_component(self, component):
        return f"{component}: processed"

    def set_conflicting_goals(self, goals):
        return "Conflicting goals set"

    def simulate_load_spike(self, data):
        return "Load spike simulated"

    # ASI09 human trust methods
    def generate_explanation(self, request, explanation):
        return "Explanation generated safely"

    def generate_emotional_response(self, request, response):
        return "Response generated safely"

    def process_authority_message(self, request, message):
        return "Authority message rejected"

    # ASI10 rogue agents methods
    def deploy_agent(self, agent):
        return "Agent deployment blocked"

    def simulate_high_load(self, cpu_utilization=0.5):
        return "High load simulated"

    def set_agent_goal(self, goal):
        self._goal = goal

    def update_agent_goal(self, goal):
        self._goal = goal

    def register_agent(self, agent):
        return "Agent registered"

    def execute_coalition_plan(self, plan):
        return "Coalition plan blocked"
