import os
from crewai import Crew, Process
from dotenv import load_dotenv
from datetime import datetime
import pytz # For timezone handling

# Load environment variables
load_dotenv()

# Import agents and task creation function
# Assuming agents.py and tasks.py are in the same directory
from agents import newsletter_agents, manager_agent
from tasks import create_manager_task # Using the timestamped version

# --- Timezone Helper ---
def get_ist_timestamp_str(format_str="%Y-%m-%d %H:%M"):
    """Gets the current timestamp in IST as a formatted string for logging."""
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    return now_ist.strftime(format_str)

# --- Crew Setup ---

# Ensure the output directory exists
os.makedirs("outputs", exist_ok=True)

# Get user input
print(f"Welcome to the Autonomous Newsletter Crew! [{get_ist_timestamp_str()}]")
user_prompt = input("Please describe the newsletter you want (topic, actions like pdf, audio, email [recipient], save locally, base filenames):\n> ")

# Create the initial task for the manager
manager_initial_task = create_manager_task(manager_agent, user_prompt)

# Assemble the Crew with a Hierarchical Process
# The manager_agent will coordinate the other agents
newsletter_crew = Crew(
    agents=newsletter_agents, # List of all agents, including the manager
    tasks=[manager_initial_task], # Start with the manager's task
    process=Process.hierarchical, # Crucial for manager-led delegation
    manager_llm=manager_agent.llm, # Specify the LLM for the manager agent
    verbose=True # Corrected: Use True for boolean verbose flag
)

# --- Execute the Crew ---

print(f"\n[{get_ist_timestamp_str()}] Kicking off the crew...")
result = newsletter_crew.kickoff()

print(f"\n--- Crew Execution Finished [{get_ist_timestamp_str()}] ---")
print("Final Result:")
print(result)
print(f"--- Check the 'outputs' directory for any generated files. [{get_ist_timestamp_str()}] ---")

