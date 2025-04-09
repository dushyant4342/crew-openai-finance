# CrewAI Autonomous Newsletter Generator

## Overview

This project utilizes the CrewAI framework to automate the creation and distribution of newsletters based on a user-provided topic. It follows a sequential workflow where different AI agents, each specialized for a specific task, collaborate to research, write, format (PDF/Audio), and distribute the content.

## Features

* **Topic-Based Content:** Generates newsletters on user-specified topics.
* **Automated Research:** Employs a researcher agent to gather up-to-date information using web search.
* **Content Writing:** A writer agent synthesizes research into a newsletter format and prepares an audio script.
* **Multi-Format Output:** Conditionally generates PDF documents and MP3 audio files based on user request.
* **Local Saving:** Saves generated PDF and Audio files locally in an `outputs` directory with timestamps.
* **Email Distribution:** Conditionally sends the generated files via email to recipients specified in the environment settings.
* **Sequential Workflow:** Tasks are executed one after another in a predefined order (Research -> Write -> PDF -> Audio -> Email).
* **Modular Design:** Uses separate files for agents (`agents.py`), task definitions (`tasks.py`), and tools (`tools.py`).

## Workflow

The process is orchestrated by the `main.py` script:

1.  **User Input:** The script prompts the user for a topic and desired actions (e.g., "latest AI news, pdf, audio, email").
2.  **Analysis:** `main.py` parses the input to identify the core topic and determine if PDF, Audio, or Email actions are requested. It also retrieves email recipients from environment variables.
3.  **Task Creation:** Based on the analysis, `main.py` creates a sequence of `Task` objects using functions imported from `tasks.py`. Tasks are added conditionally (e.g., PDF task only added if 'pdf' is in the prompt). Context is passed sequentially from one task to the next.
4.  **Agent Assignment:** The appropriate pre-defined agent (from `agents.py`) is assigned to each task.
5.  **Crew Execution:** A `Crew` object is created with the necessary agents and the ordered list of tasks. The `process` is set to `sequential`.
6.  **`crew.kickoff()`:** The crew executes the tasks one by one. Agents use tools defined in `tools.py` (like search, PDF creation, text-to-speech, email sending).
7.  **Output:** Generated files (PDF, MP3) are saved in the `./outputs` directory. The final status message from the last task (usually the email task if run) is printed.

## File Structure

.├── outputs/              # Directory where generated files (PDF, MP3) are saved├── agents.py             # Defines all specialist AI agents (Researcher, Writer, etc.) and initializes LLM├── tasks.py              # Defines functions to create Task objects for each agent├── tools.py              # Defines custom tools (@tool decorated functions) used by agents├── main.py               # Main script to run the crew: gets input, creates tasks, runs crew├── .env                  # Stores API keys and configuration (MUST BE CREATED)└── requirements.txt      # Lists Python dependencies
## Requirements

* Python 3.9+
* `pip` package installer
* API Keys:
    * **Gemini API Key:** For the LLM used by the agents (from Google AI Studio).
    * **Serper API Key:** For the web search tool used by the researcher (from Serper.dev).
* Email Credentials (for Email Task):
    * **Sender Email Address:** The email address to send from.
    * **Email Password/App Password:** **Important:** For Gmail, you'll likely need to generate an "App Password" if using 2-Factor Authentication. Do not use your main Google account password directly.
    * **SMTP Host:** (e.g., `smtp.gmail.com` for Gmail)
    * **SMTP Port:** (e.g., `587` for Gmail TLS)
    * **Recipient Email(s):** Comma-separated list of emails to send the newsletter to.

## Setup

1.  **Clone/Download:** Get the project files.
2.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```
    *(See `requirements.txt` content below)*
4.  **Create `.env` File:** Create a file named `.env` in the project root and add your keys and credentials. Use `.env.example` as a template:

    ```dotenv
    # .env.example - Copy this to .env and fill in your values

    # LLM & Search APIs
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    SERPER_API_KEY="YOUR_SERPER_API_KEY"

    # Email Configuration
    SENDER_EMAIL="your_sender_email@example.com"
    EMAIL_PASSWORD="YOUR_EMAIL_APP_PASSWORD" # Use App Password for Gmail 2FA
    EMAIL_HOST="smtp.example.com" # e.g., smtp.gmail.com
    EMAIL_PORT="587" # Common port for TLS
    EMAIL_RECIPIENTS="recipient1@example.com,recipient2@example.com" # Comma-separated
    ```

## Running the Script

1.  Activate your virtual environment (if using one).
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  Follow the prompt to enter the newsletter topic and desired actions (e.g., `latest developments in quantum computing, pdf, email`).

## Output

* The script will print logs to the console showing the progress of the agents and tasks (`verbose=1` or `2`).
* Generated PDF and MP3 files will be saved in the `outputs/` directory with a timestamped filename (e.g., `quantum_computing_20250409_173000_IST.pdf`).
* If requested, an email with the attachments will be sent to the specified recipients.
* The final output message from the last executed task will be printed.

## `requirements.txt`

```txt
crewai>=0.30.0,<0.31.0 # Or latest compatible version
crewai-tools>=0.2.0,<0.3.0 # Or latest compatible version
python-dotenv>=1.0.0,<2.0.0
langchain-google-genai>=1.0.0,<2.0.0 # Or the specific LLM integration you use
google-generativeai>=0.5.0,<0.6.0
pytz>=2024.1
fpdf>=1.7.2,<2.0.0 # For PDF generation tool
gTTS>=2.5.0,<3.0.0 # For Text-to-Speech tool
# Add any other specific dependencies your tools might require
CustomizationAgents/Prompts: Modify agent roles, goals, backstories,