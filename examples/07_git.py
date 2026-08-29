"""Git operations on cloud workspaces."""

from computer_agents import ComputerAgentsClient

client = ComputerAgentsClient()

env_id = "env_xxx"

# Check for uncommitted changes
status = client.git.get_status(env_id)
changed_files = status.get("changedFiles", [])
print(f"Files changed: {len(changed_files)}")
for file in changed_files:
    print(f"  {file.get('status', '')} {file.get('path', '')}")

# Commit changes
if changed_files:
    client.git.stage(env_id, all=True)
    result = client.git.commit(
        env_id,
        message="Update from Computer Agents",
    )
    print(f"Committed: {result['sha']}")

    # Push to remote
    push = client.git.push(env_id)
    print(f"Pushed to {push['branch']}")

client.close()
