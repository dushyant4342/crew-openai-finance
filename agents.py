from crewai import Agent
from tools import tool  # Import the SerperDevTool from tools.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import the OpenAI Chat model
from langchain_openai import ChatOpenAI

# Initialize the OpenAI model
try:
    llm = ChatOpenAI(
        model="gpt-4",  # Use GPT-4 or another OpenAI model
        verbose=True,
        temperature=0.5,
        api_key=os.getenv("OPENAI_API_KEY")  # Ensure this is set in .env
    )
    print("OpenAI model initialized successfully!")
except Exception as e:
    print(f"Error initializing OpenAI model: {e}")
    raise

# Creating a senior researcher agent with memory and verbose mode
news_researcher = Agent(
    role="Senior Researcher",
    goal='Find groundbreaking tech in {topic}',  # Shorter goal
    verbose=True,
    memory=True,
    backstory=(
        "Curious innovator exploring cutting-edge tech to change the world."  # Shorter backstory
    ),
    tools=[tool],  # Use the SerperDevTool for internet search
    llm=llm,
    allow_delegation=True
)

# Creating a writer agent responsible for writing news blogs
news_writer = Agent(
    role='Writer',
    goal='Write engaging stories about {topic}',  # Shorter goal
    verbose=True,
    memory=True,
    backstory=(
        "Skilled at simplifying complex topics into captivating narratives."  # Shorter backstory
    ),
    tools=[tool],  # Use the SerperDevTool for internet search
    llm=llm,
    allow_delegation=False
)

# Print success message
print("Agents created successfully!")