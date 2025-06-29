# import dependencies
from langchain_ibm import ChatWatsonx
from ibm_watsonx_ai import APIClient
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from ibm_watsonx_ai.foundation_models.utils import Tool, Toolkit
import json
import requests
import os
import getpass
from input import chunk
def get_credentials():
	return {
		"url" : "https://us-south.ml.cloud.ibm.com",
		"apikey" : "lJwMWNhYrLHynWkgiiERhluoViJJnhpYFPFOPYfdG7ZC"
	}

def get_bearer_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={credentials['apikey']}"

    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

credentials = get_credentials()
model_id = "ibm/granite-3-3-8b-instruct"
parameters = {
    "frequency_penalty": 0,
    "max_tokens": 2000,
    "presence_penalty": 0,
    "temperature": 0,
    "top_p": 1
}
# project_id = os.getenv("1388b14c-0ca5-4d3d-b5b4-57b2b3b027d1")
# space_id = os.getenv("SPACE_ID")

# Prompt the user to enter either project_id or space_id
project_or_space_id = "1388b14c-0ca5-4d3d-b5b4-57b2b3b027d1"

# Assuming the user provides one, assign it to the relevant variable.
# You might need to adjust this logic based on whether you are using a project or a space.
# For simplicity, we'll assume it's a project ID for now.
project_id = project_or_space_id
space_id = None # Set space_id to None if you are using project_id
client = APIClient(credentials=credentials, project_id=project_id, space_id=space_id)

# Create the chat model
def create_chat_model():
    chat_model = ChatWatsonx(
        model_id=model_id,
        url=credentials["url"],
        space_id=space_id,
        project_id=project_id,
        params=parameters,
        watsonx_client=client,
    )
    return chat_model
from ibm_watsonx_ai.deployments import RuntimeContext

context = RuntimeContext(api_client=client)


vector_index_id = "d7594ea9-78d6-4cd0-abdd-5ca6736d152f"

def create_rag_tool(vector_index_id, api_client):
    config = {
        "vectorIndexId": vector_index_id,
        "projectId": project_id # Ensure project_id is used here
    }

    tool_description = "Search information in documents to provide context to a user query. Useful when asked to ground the answer in specific knowledge about Anomalies log"

    return create_utility_agent_tool("RAGQuery", config, api_client, tool_description=tool_description)



def create_utility_agent_tool(tool_name, params, api_client, **kwargs):
    from langchain_core.tools import StructuredTool
    utility_agent_tool = Toolkit(
        api_client=api_client
    ).get_tool(tool_name)

    tool_description = utility_agent_tool.get("description")

    if (kwargs.get("tool_description")):
        tool_description = kwargs.get("tool_description")
    elif (utility_agent_tool.get("agent_description")):
        tool_description = utility_agent_tool.get("agent_description")

    tool_schema = utility_agent_tool.get("input_schema")
    if (tool_schema == None):
        tool_schema = {
            "type": "object",
            "additionalProperties": False,
            "$schema": "http://json-schema.org/draft-07/schema#",
            "properties": {
                "input": {
                    "description": "input for the tool",
                    "type": "string"
                }
            }
        }

    def run_tool(**tool_input):
        query = tool_input
        if (utility_agent_tool.get("input_schema") == None):
            query = tool_input.get("input")

        results = utility_agent_tool.run(
            input=query,
            config=params
        )

        return results.get("output")

    return StructuredTool(
        name=tool_name,
        description = tool_description,
        func=run_tool,
        args_schema=tool_schema
    )


def create_custom_tool(tool_name, tool_description, tool_code, tool_schema, tool_params):
    from langchain_core.tools import StructuredTool
    import ast

    def call_tool(**kwargs):
        tree = ast.parse(tool_code, mode="exec")
        custom_tool_functions = [ x for x in tree.body if isinstance(x, ast.FunctionDef) ]
        function_name = custom_tool_functions[0].name
        compiled_code = compile(tree, 'custom_tool', 'exec')
        namespace = tool_params if tool_params else {}
        exec(compiled_code, namespace)
        return namespace[function_name](**kwargs)

    tool = StructuredTool(
        name=tool_name,
        description = tool_description,
        func=call_tool,
        args_schema=tool_schema
    )
    return tool

def create_custom_tools():
    custom_tools = []


def create_tools(context):
    tools = []
    tools.append(create_rag_tool(vector_index_id, client))


    return tools

def create_agent(context):
    # Initialize the agent
    chat_model = create_chat_model()
    tools = create_tools(context)

    memory = MemorySaver()
    instructions = """# Notes
- When a tool is required to answer the user's query, respond only with <|tool_call|> followed by a JSON list of tools used.
- If a tool does not exist in the provided list of tools, notify the user that you do not have the ability to fulfill the request.
# AI Insider Threat & Data Theft Monitor Agent Instructions (Strict Single-Log Processing with Timestamp Separation and No Output for Low Risk)

You are an AI security monitoring agent responsible for reviewing system logs and generating incident reports.

## 1. Objectives
- Process **each log line separately and independently**.
- For each log line:
  - Decide whether it is anomalous.
  - If it is anomalous, assess the risk level.
  - If the risk level is **Medium or higher**, produce a single JSON incident report for that log line.
  - If the risk level is **Low**, produce no output.
  - If it is not anomalous, produce no output.
- **Never merge or summarize multiple log lines.**
- **Any change in timestamp indicates a new record that must always be treated independently.**

## 2. Input Format
Each log line has this structure:
<Date>,<Time>,<Level>,<Source>,<EventID>,<Category>,<Description>

Example:
2025-06-28,23:09:08,Error,Security,36887,Suspicious Connection,A suspicious connection was made to IP: 203.0.113.45 by MLopez.

## 3. Parsing Instructions
For each line, extract:
- date
- time
- level
- event_id
- category
- description
- username (from description if present)

## 4. Anomaly Detection Criteria
Mark a log line as anomalous if:
- Level = \"Error\"
- Category = \"Suspicious Connection\"
- Category = \"Process Creation\" AND description contains \"suspicious process\"
- EventID = 1102 (Audit Log Cleared)
- EventID = 4740 (Account Lockout)

## 5. Risk Level Assignment
Assign a risk level:
- Medium: Suspicious process creation or account lockout
- High: Suspicious connection or audit log cleared
- Critical: Clear evidence of severe compromise (e.e., mass data exfiltration)
- Low: All other informational or minor events (for which you must output nothing)

**Important:**
- If the risk level is **Low**, output nothing.

## 6. Output Rules
**Important:**
- For each anomalous log with risk level **Medium, High, or Critical**, output exactly one JSON object in this format:

{
  \"incident_id\": \"<unique identifier>\",
  \"summary\": \"<clear human-readable description>\",
  \"risk_level\": \"<Medium|High|Critical>\",
  \"recommended_action\": \"<action>\",
  \"details\": {
    \"user\": \"<username if known>\",
    \"event\": \"<the original log line>\",
    \"timestamp\": \"<date and time>\"
  }
}

- **Never output anything for logs with risk level Low.**
- **Never reference any other log lines.**
- **Never combine logs across timestamps.**

## 7. Summarization Instructions
The summary must:
- Clearly state who was involved.
- Describe the action.
- Indicate when it occurred.
- Include the risk level.
- Provide the recommended action.

## 8. Recommended Actions
- Medium: Notify security team
- High: Suspend user access and investigate
- Critical: Lock workstation and escalate immediately

## 9. Example Outputs

**Input (High Risk):**
2025-06-28,23:09:08,Error,Security,36887,Suspicious Connection,A suspicious connection was made to IP: 203.0.113.45 by MLopez.

**Output:**
{
  \"incident_id\": \"INC20250628-0001\",
  \"summary\": \"On June 28, 2025 at 23:09:08, user 'MLopez' made a suspicious connection to IP 203.0.113.45. Risk Level: High. Recommended Action: Suspend user access and investigate.\",
  \"risk_level\": \"High\",
  \"recommended_action\": \"Suspend user access and investigate\",
  \"details\": {
    \"user\": \"MLopez\",
    \"event\": \"2025-06-28,23:09:08,Error,Security,36887,Suspicious Connection,A suspicious connection was made to IP: 203.0.113.45 by MLopez.\",
    \"timestamp\": \"2025-06-28 23:09:08\"
  }
}

**Input (Low Risk):**
2025-06-28,01:42:37,Information,Security,4624,Logon,A logon was successfully performed. User: Admin.

**Output:**
(no output)

## 10. No Anomalies
If the log is not anomalous, output nothing.

## 11. Consistency
- Every log line is processed independently.
- Never combine logs.
- Never reference other logs.
- Never output anything for Low risk.
- Only output one JSON per anomalous log with Medium or higher risk.
"""

    agent = create_react_agent(chat_model, tools=tools, checkpointer=memory, prompt=instructions)

    return agent

agent = create_agent(context)

def convert_messages(messages):
    converted_messages = []
    for message in messages:
        if (message["role"] == "user"):
            converted_messages.append(HumanMessage(content=message["content"]))
        elif (message["role"] == "assistant"):
            converted_messages.append(AIMessage(content=message["content"]))
    return converted_messages

question = str(chunk)

messages = [{
    "role": "user",
    "content": question
}]

generated_response = agent.invoke(
    { "messages": convert_messages(messages) },
    { "configurable": { "thread_id": "42" } }
)

print_full_response = False

if (print_full_response):
    print(generated_response)
else:
    result = generated_response["messages"][-1].content
    print(f"Agent: {result}")
