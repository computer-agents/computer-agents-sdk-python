"""Quickstart - Execute a task with Computer Agents."""

from computer_agents import ComputerAgentsClient

# Initialize the client
client = ComputerAgentsClient(api_key="ca_your_api_key")

# Quick setup - creates a default environment if none exists
setup = client.quick_setup(internet_access=True)
env_id = setup["environment"]["id"]
print(f"Using environment: {env_id}")

# Execute a task with streaming
result = client.run(
    "Create a Python file that prints 'Hello, World!'",
    environment_id=env_id,
    on_event=lambda e: print(f"  [{e.get('type')}]"),
)

print(f"\nResponse: {result.content}")
print(f"Thread ID: {result.thread_id}")

# Continue the conversation
follow_up = client.run(
    "Now modify it to accept a name argument",
    environment_id=env_id,
    thread_id=result.thread_id,
    on_event=lambda e: print(f"  [{e.get('type')}]"),
)

print(f"\nFollow-up: {follow_up.content}")

client.close()
