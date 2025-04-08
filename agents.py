import os
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent
from dotenv import load_dotenv
import pytz # Added for timestamp helper
from datetime import datetime # Added for timestamp helper



# Import tools 
from tools import (
    search_tool,
    pdf_creation_tool,
    text_to_speech_tool,
    email_sending_tool,
    local_save_tool
)

load_dotenv()
from crewai import Agent, LLM
from langchain_groq import ChatGroq


# api_key = os.getenv("GOOGLE_API_KEY")
# if not api_key:
#     raise ValueError("GOOGLE_API_KEY environment variable not set.")

#from langchain_openai import ChatOpenAI 
#from langchain.chat_models import ChatOpenAI


from langchain_openai import ChatOpenAI #worked but api quota reached
llm = ChatOpenAI(model="gpt-4", temperature=0.2) # Lower temp for manager might be better


# Initialize Groq LLM (Example using Llama 3 70b)
# llm = ChatGroq(
#     temperature=0.2,
#     groq_api_key=os.getenv("GROQ_API_KEY"),
#     model_name="llama3-70b-8192" # Or other models like mixtral-8x7b-32768
# )
# print("Groq LLM Initialized.")



# # Initialize the LLM with the correct provider and model
# llm = LLM(
#     api_key=os.getenv("GEMINI_API_KEY"),
#     model="gemini/gemini-pro",  # Specify the provider and model
# )



# import google.generativeai as genai

# genai.configure(api_key=api_key)

#llm = genai.GenerativeModel(model_name='gemini-1.5-pro')


# try:
#     llm = ChatGoogleGenerativeAI(
#     model="models/gemini-pro", # Correct format for LiteLLM
#         google_api_key=api_key
#     )
#     print("LLM Initialized Successfully!")
#     # Now try using the llm, e.g., llm.invoke("Hello")
# except Exception as e:
#     print(f"Error initializing LLM: {e}")



def get_ist_timestamp_str(format_str="%Y%m%d_%H%M"):
    """Gets the current timestamp in IST as a formatted string."""
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    return now_ist.strftime(format_str)


# --- Agent Definitions ---

# 1. Project Manager Agent
manager_agent = Agent(
    role="Project Manager",
    goal=(
        "Oversee the newsletter creation process based on user requests. "
        "Analyze the user's prompt to understand the topic, required actions (research, write, pdf, audio, email, save locally), and any parameters (like email recipient, desired base filenames). "
        "Plan the necessary steps and delegate tasks sequentially to the appropriate specialist agents. "
        "Ensure agents are aware that filenames for PDF and audio will be automatically timestamped."
        "Ensure the final output matches the user's request."
    ),
    backstory=(
        "You are an expert project manager, skilled at breaking down complex requests "
        "into actionable steps and coordinating a team of specialists. You meticulously "
        "plan the workflow, ensuring agents know filenames get timestamped, and that each agent receives the necessary information "
        "from previous steps to complete their task effectively."
    ),
    tools=[], # Manager delegates
    llm=llm, # Assign the initialized Gemini LLM    

    allow_delegation=True,
    verbose=True # Keep agent verbose for debugging delegation
)

# 2. Researcher Agent
researcher_agent = Agent(
    role="Researcher",
    goal="Gather comprehensive and relevant information on the topic: {topic}.",
    backstory=(
        "You are a skilled researcher, adept at using search tools to find "
        "the most current and accurate information on any given subject. "
        "You provide detailed findings."
    ),
    tools=[search_tool],
    llm=llm, # Assign the initialized Gemini LLM
    allow_delegation=False,
    verbose=True # Keep agent verbose
)

# 3. Writer Agent
writer_agent = Agent(
    role="Content Writer",
    goal="Synthesize the research findings about {topic} into a clear, concise, and engaging newsletter article.",
    backstory=(
        "You are a talented writer, specialized in transforming research data "
        "into compelling newsletter content. You focus on clarity and engagement."
    ),
    tools=[],
    llm=llm, # Assign the initialized Gemini LLM
    allow_delegation=False,
    verbose=True # Keep agent verbose
)

# 4. PDF Creator Agent
pdf_creator_agent = Agent(
    role="PDF Document Creator",
    goal="Generate a PDF document from the provided text content about {topic}. Use the base filename '{base_filename}'. The tool will automatically add a timestamp and '.pdf' extension.",
    backstory=(
        "You are a meticulous document specialist. You take text content and instruct the PDF tool "
        "to create a timestamped PDF file using the provided base filename."
    ),
    tools=[pdf_creation_tool],
    llm=llm, # Assign the initialized Gemini LLM
    allow_delegation=False,
    verbose=True # Keep agent verbose
)

# 5. Audio Generator Agent
audio_generator_agent = Agent(
    role="Audio Summary Generator",
    goal="Convert the provided text content about {topic} into an MP3 audio file. Use the base filename '{base_filename}'. The tool will automatically add a timestamp and '.mp3' extension.",
    backstory=(
        "You are an audio technician. You use text-to-speech technology to create "
        "clear audio summaries, instructing the tool to save them with a timestamped filename based on the provided base name."
    ),
    tools=[text_to_speech_tool],
    llm=llm, # Assign the initialized Gemini LLM
    allow_delegation=False,
    verbose=True # Keep agent verbose
)

# 6. Email Sender Agent
email_sender_agent = Agent(
    role="Email Dispatcher",
    goal="Compose and send an email to '{recipient}' with the subject '{subject}'. Attach the specified files: {attachment_paths}.",
    backstory=(
        "You are a reliable email dispatcher. You carefully compose emails according "
        "to instructions and ensure all specified attachments (using their full timestamped paths) are included before sending."
    ),
    tools=[email_sending_tool],
    llm=llm, # Assign the initialized Gemini LLM
    allow_delegation=False,
    verbose=True # Keep agent verbose
)

# 7. Local Saver Agent
local_saver_agent = Agent(
    role="File Archiver",
    goal="Confirm the specified file ('{file_path}') exists in the local 'outputs' directory.",
    backstory=(
        "You are responsible for archiving files. You verify that files generated "
        "by other agents exist at their specified timestamped paths in the 'outputs' directory."
    ),
    tools=[local_save_tool],
    llm=llm, # Assign the initialized Gemini LLM
    allow_delegation=False,
    verbose=True # Keep agent verbose
)

# --- Agent List for easy import ---
newsletter_agents = [
    manager_agent,
    researcher_agent,
    writer_agent,
    pdf_creator_agent,
    audio_generator_agent,
    email_sender_agent,
    local_saver_agent
]

