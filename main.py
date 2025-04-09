import os
from crewai import Crew, Process, Task # Task import needed for type hinting if used
from dotenv import load_dotenv
from datetime import datetime
import pytz

# --- Load Environment Variables ---
load_dotenv()
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "") # Get email recipients
if not EMAIL_RECIPIENTS:
    print("Warning: EMAIL_RECIPIENTS not found in .env. Email task will be skipped if requested.")
 

try:
    from agents import (
        researcher_agent,
        writer_agent,
        pdf_creator_agent,
        audio_generator_agent,
        email_sender_agent,
        local_saver_agent  
    )
except ImportError as e:
    print(f"FATAL ERROR: Could not import agents from agents.py: {e}")
    exit(1)

try:
    from tasks import (
        create_research_task,
        create_writing_task,
        create_pdf_task,
        create_audio_task,
        create_email_task,
        create_save_local_task  
    )
except ImportError as e:
    print(f"FATAL ERROR: Could not import task functions from tasks.py: {e}")
    exit(1)

# --- Timezone & Output Setup ---
def get_ist_timestamp_str(format_str="%Y%m%d_%H%M"):
    """Gets the current timestamp in IST for unique filenames."""
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    return now_ist.strftime(format_str)

output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory: '{output_dir}'")

# --- Get User Input & Analyze ---
print(f"\nWelcome! [{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M')}]")
user_prompt = input("Describe newsletter topic & actions:\n> ").lower()

# Basic extraction
topic = user_prompt.split(",")[0].strip()
do_pdf = 'pdf' in user_prompt or 'document' in user_prompt
do_audio = 'audio' in user_prompt or 'mp3' in user_prompt
do_email = 'email' in user_prompt and EMAIL_RECIPIENTS

base_filename = "NewsLetter"
timestamp = get_ist_timestamp_str()
filename_base_ts = f"{base_filename}_{timestamp}" # Base name with timestamp for tools

print(f"Topic: '{topic}' | PDF: {do_pdf} | Audio: {do_audio} | Email: {do_email}")
print(f"Base filename for tools: '{filename_base_ts}'")


email_recipient_list = EMAIL_RECIPIENTS

# --- Calculate expected full paths ---
expected_pdf_filepath = f"{output_dir}/{filename_base_ts}.pdf" if do_pdf else None
expected_audio_filepath = f"{output_dir}/{filename_base_ts}.mp3" if do_audio else None

print(f"Topic: '{topic}' | PDF: {do_pdf} | Audio: {do_audio} | Email: {do_email} to {email_recipient_list}")
print(f"Base filename for tools: '{filename_base_ts}'")
if expected_pdf_filepath: print(f"Expected PDF Path: {expected_pdf_filepath}")
if expected_audio_filepath: print(f"Expected Audio Path: {expected_audio_filepath}")


# --- Create Task List Sequentially using Imported Functions ---
tasks_in_sequence = []
# Use a set for agents to automatically handle uniqueness
agents_in_crew = {researcher_agent, writer_agent}
last_task_object = None # Tracks the last task added for context/dependency

# 1. Research Task
print("Creating Research Task...")
research_task_obj = create_research_task(researcher_agent, topic)
tasks_in_sequence.append(research_task_obj)
last_task_object = research_task_obj

# 2. Write Task
print("Creating Writing Task...")
write_task_obj = create_writing_task(writer_agent, topic, context=[last_task_object])
tasks_in_sequence.append(write_task_obj)
last_task_object = write_task_obj

# 3. PDF Task (Conditional)
pdf_task_object = None # Keep track if this task is created
if do_pdf:
    print("Creating PDF Task...")
    agents_in_crew.add(pdf_creator_agent)
    pdf_task_object = create_pdf_task(
        agent=pdf_creator_agent,
        topic=topic,
        base_filename=filename_base_ts,
        context=[last_task_object]
    )
    tasks_in_sequence.append(pdf_task_object)
    last_task_object = pdf_task_object

    # 3b. Save PDF Task (Conditional on PDF Task)
    print("Creating Save PDF Task...")
    agents_in_crew.add(local_saver_agent)
    # Assuming create_save_local_task uses 'dependencies' to get the file path
    save_pdf_task_obj = create_save_local_task(
        agent=local_saver_agent,
        file_producing_task=pdf_task_object, # Pass the task object that creates the file
        context=[last_task_object] # Context from the pdf task itself
    )
    tasks_in_sequence.append(save_pdf_task_obj)
    last_task_object = save_pdf_task_obj # Now this is the last task

# 4. Audio Task (Conditional)
audio_task_object = None # Keep track if this task is created
if do_audio:
    print("Creating Audio Task...")
    agents_in_crew.add(audio_generator_agent)
    # Audio task depends on the writer's script output
    audio_context = [write_task_obj]
    audio_task_object = create_audio_task(
        agent=audio_generator_agent,
        topic=topic,
        base_filename=filename_base_ts,
        context=audio_context
    )
    tasks_in_sequence.append(audio_task_object)
    last_task_object = audio_task_object # Update last task

    # 4b. Save Audio Task (Conditional on Audio Task)
    print("Creating Save Audio Task...")
    agents_in_crew.add(local_saver_agent)
    save_audio_task_obj = create_save_local_task(
        agent=local_saver_agent,
        file_producing_task=audio_task_object, # Pass the audio task object
        context=[last_task_object] # Context from the audio task
    )
    tasks_in_sequence.append(save_audio_task_obj)
    last_task_object = save_audio_task_obj # Now this is the last task





# 5. Email Task (Conditional)
if do_email:
    print("Creating Email Task...")
    agents_in_crew.add(email_sender_agent)
    email_subject = f"Newsletter: {topic} - {timestamp}"
    email_body = f"Hi,\n\nPlease find attached the newsletter from the prompt:  '{topic}'.\n\nBest regards,\nYour CrewAI Bot"

    # Context is the last task that was actually added to the sequence
    email_context = [last_task_object]

    # Call the MODIFIED create_email_task function
    email_task_obj = create_email_task(
        agent=email_sender_agent,
        recipient_list=EMAIL_RECIPIENTS, # Pass the parsed list
        subject=email_subject,
        body=email_body,
        # Pass the expected paths directly
        expected_pdf_path=expected_pdf_filepath,
        expected_audio_path=expected_audio_filepath,
        context=email_context
    )
    tasks_in_sequence.append(email_task_obj)
    # last_task_object = email_task_obj # Update if needed


# --- Create and Run the Crew ---
final_agent_list = list(agents_in_crew)
print(f"\nCreating crew with {len(tasks_in_sequence)} tasks for agents: {[agent.role for agent in final_agent_list]}")

newsletter_crew = Crew(
    agents=final_agent_list,
    tasks=tasks_in_sequence,
    process=Process.sequential,
    verbose=1
)

print(f"\n[{get_ist_timestamp_str('%Y-%m-%d %H:%M')}] Kicking off the crew...")
result = newsletter_crew.kickoff()

print(f"\n--- Crew Execution Finished [{get_ist_timestamp_str('%Y-%m-%d %H:%M')}] ---")
print("\nFinal Result (Output of the LAST task):")
final_output = getattr(result, 'raw', str(result))
print(final_output)
print(f"\n--- Check '{output_dir}' directory for generated files. ---")