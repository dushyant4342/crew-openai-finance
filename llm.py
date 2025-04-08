import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key
    )
    print("LLM Initialized Successfully!")
    # Now try using the llm, e.g., llm.invoke("Hello")
except Exception as e:
    print(f"Error initializing LLM: {e}")
    # Provide this full error message if you still have problemspytho


from google import genai

# Initialize the client with your API key
client = genai.Client(api_key=api_key)

# Retrieve the list of available models
models = client.models.list()

# Print the model names
for model in models:
    print(model.name)