from input import start_reading, get_chunk

from langchain_ibm import ChatWatsonx
from ibm_watsonx_ai import APIClient
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from ibm_watsonx_ai.foundation_models.utils import Tool, Toolkit
import json
import requests

result = ""  # Define a global `result`

def get_credentials():
    return {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": "lJwMWNhYrLHynWkgiiERhluoViJJnhpYFPFOPYfdG7ZC"
    }

credentials = get_credentials()
model_id = "ibm/granite-3-3-8b-instruct"
parameters = {
    "frequency_penalty": 0,
    "max_tokens": 2000,
    "presence_penalty": 0,
    "temperature": 0,
    "top_p": 1
}

project_or_space_id = "1388b14c-0ca5-4d3d-b5b4-57b2b3b027d1"
project_id = project_or_space_id
space_id = None
client = APIClient(credentials=credentials, project_id=project_id, space_id=space_id)

from ibm_watsonx_ai.deployments import RuntimeContext
context = RuntimeContext(api_client=client)

vector_index_id = "d7594ea9-78d6-4cd0-abdd-5ca6736d152f"

def create_rag_tool(vector_index_id, api_client):
    config = {
        "vectorIndexId": vector_index_id,
        "projectId": project_id
    }
    tool_description = "Search information in documents to provide context to a user query. Useful when asked to ground the answer in specific knowledge about Anomalies log"
    return create_utility_agent_tool("RAGQuery", config, api_client, tool_description=tool_description)

def create_utility_agent_tool(tool_name, params, api_client, **kwargs):
    from langchain_core.tools import StructuredTool
    utility_agent_tool = Toolkit(api_client=api_client).get_tool(tool_name)

    tool_description = utility_agent_tool.get("description")

    if kwargs.get("tool_description"):
        tool_description = kwargs.get("tool_description")
    elif utility_agent_tool.get("agent_description"):
        tool_description = utility_agent_tool.get("agent_description")

    tool_schema = utility_agent_tool.get("input_schema")
    if tool_schema is None:
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
        if utility_agent_tool.get("input_schema") is None:
            query = tool_input.get("input")

        results = utility_agent_tool.run(
            input=query,
            config=params
        )
        return results.get("output")

    return StructuredTool(
        name=tool_name,
        description=tool_description,
        func=run_tool,
        args_schema=tool_schema
    )

def create_tools(context):
    tools = []
    tools.append(create_rag_tool(vector_index_id, client))
    return tools

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

def create_agent(context):
    chat_model = create_chat_model()
    tools = create_tools(context)
    memory = MemorySaver()
    instructions = """You are a security analyst AI that analyzes log data for potential insider threats and data theft activities.

IMPORTANT: You must ALWAYS respond with valid JSON format containing an array of security incidents. Each incident should have this structure:

{
  "summary": "Brief description of the security incident",
  "risk_level": "Critical|High|Medium|Low",
  "user": "username involved",
  "timestamp": "ISO format timestamp",
  "recommended_action": "What should be done about this incident",
  "details": {
    "timestamp": "ISO format timestamp",
    "user": "username",
    "ip_address": "IP address",
    "session_id": "session identifier",
    "activity_type": "type of activity",
    "severity_score": 1-10
  }
}

Analyze the provided log entries and identify any suspicious activities, unauthorized access attempts, data exfiltration, or other security concerns. Return ONLY the JSON array, no additional text or explanations."""
    agent = create_react_agent(chat_model, tools=tools, checkpointer=memory, prompt=instructions)
    return agent

def convert_messages(messages):
    converted_messages = []
    for message in messages:
        if message["role"] == "user":
            converted_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            converted_messages.append(AIMessage(content=message["content"]))
    return converted_messages

def main():
    global result
    agent = create_agent(context)
    print("Using IBM Watson agent")

    input_filename = "sys_log.txt"
    lines_per_chunk = 5
    delay_between_chunks = 1

    print("Starting log processing...")
    start_reading(input_filename, lines_per_chunk, delay_between_chunks)

    chunk_count = 0
    output_jsons = []

    while True:
        chunk = get_chunk()
        if chunk is None:
            print("No more chunks to process.")
            break

        chunk_count += 1
        print(f"\n--- Processing Chunk {chunk_count} ---")
        print(f"Chunk content:\n{chunk}")

        messages = [{"role": "user", "content": str(chunk)}]

        try:
            generated_response = agent.invoke(
                {"messages": convert_messages(messages)},
                {"configurable": {"thread_id": f"thread_{chunk_count}"}}
            )
            chunk_result = generated_response["messages"][-1].content
            print(f"Agent Response: {chunk_result}")
            output_jsons.append(chunk_result)

        except Exception as e:
            print(f"Error processing chunk {chunk_count}: {e}")
            continue

    result = "[" + ",".join(output_jsons) + "]"
    print(f"\nProcessing complete. Total chunks processed: {chunk_count}")
    
    # If we have multiple JSON responses, we need to combine them properly
    if len(output_jsons) > 1:
        # Parse each JSON response and combine into a single array
        all_incidents = []
        for json_str in output_jsons:
            try:
                incidents = json.loads(json_str)
                if isinstance(incidents, list):
                    all_incidents.extend(incidents)
                else:
                    all_incidents.append(incidents)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON response: {json_str}")
        
        result = json.dumps(all_incidents)
    elif len(output_jsons) == 1:
        # Single response - ensure it's a flat array
        try:
            incidents = json.loads(output_jsons[0])
            if isinstance(incidents, list) and len(incidents) > 0 and isinstance(incidents[0], list):
                # Handle nested array [[...]] -> [...]
                result = json.dumps(incidents[0])
            else:
                result = output_jsons[0]
        except json.JSONDecodeError:
            result = output_jsons[0]
    else:
        result = "[]"

if __name__ == "__main__":
    main() 