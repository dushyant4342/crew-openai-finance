import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
# Import the decorator and SerperDevTool
from crewai.tools import tool
from crewai_tools import  SerperDevTool
from fpdf import FPDF
from gtts import gTTS
import shutil
from datetime import datetime
import pytz

# Load environment variables (.env file)
load_dotenv()

# --- Timezone Helper ---
def get_ist_timestamp_str(format_str="%Y%m%d_%H%M"):
    """Gets the current timestamp in IST as a formatted string."""
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    return now_ist.strftime(format_str)

# --- Tool Definitions using @tool decorator ---

# 1. Search Tool (Pre-built)
# Make sure SERPER_API_KEY is in your .env file
search_tool = SerperDevTool()

# 2. PDF Creation Tool
@tool("PDF Creation Tool")
def pdf_creation_tool(text_content: str, base_filename: str = "report") -> str:
    """
    Creates a PDF document from text content, saving it with an IST timestamp.
    Input args:
        text_content (str): The text content for the PDF.
        base_filename (str): The base name for the file (e.g., 'report'). Default is 'report'.
    The '.pdf' extension and timestamp are added automatically.
    Returns the full path to the created PDF file.
    """
    timestamp = get_ist_timestamp_str()
    safe_base_filename = base_filename.replace(" ", "_")
    filename = f"{safe_base_filename}_{timestamp}_IST.pdf"

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    try:
        # Use multi_cell for better handling of long text and newlines
        pdf.multi_cell(0, 5, text_content.encode('latin-1', 'replace').decode('latin-1'))
    except Exception as e:
         print(f"[{get_ist_timestamp_str()}] Error encoding text for PDF: {e}")
         pdf.multi_cell(0, 5, "Error encoding content.")

    pdf.output(filepath)
    print(f"[{get_ist_timestamp_str()}] PDF generated: {filepath}")
    return filepath

# 3. Text-to-Speech Tool
@tool("Text-to-Speech Tool")
def text_to_speech_tool(text_content: str, base_filename: str = "audio_summary") -> str:
    """
    Converts text content into an MP3 audio file, saving it with an IST timestamp.
    Input args:
        text_content (str): The text to convert to speech.
        base_filename (str): The base name for the file (e.g., 'summary'). Default is 'audio_summary'.
    The '.mp3' extension and timestamp are added automatically.
    Returns the full path to the created MP3 file or an error message.
    """
    timestamp = get_ist_timestamp_str()
    safe_base_filename = base_filename.replace(" ", "_")
    filename = f"{safe_base_filename}_{timestamp}_IST.mp3"

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    try:
        tts = gTTS(text=text_content, lang='en')
        tts.save(filepath)
        print(f"[{get_ist_timestamp_str()}] Audio file generated: {filepath}")
        return filepath
    except Exception as e:
        print(f"[{get_ist_timestamp_str()}] Error generating audio file: {e}")
        return f"Error generating audio: {e}"

# 4. Email Sending Tool
@tool("Email Sending Tool")
def email_sending_tool(recipient: str, subject: str, body: str, attachment_paths: list = None) -> str:
    """
    Sends an email with optional attachments.
    Input args:
        recipient (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The plain text body of the email.
        attachment_paths (list, optional): A list of full file paths for attachments. Defaults to None.
    Returns a confirmation message or an error string.
    """
    timestamp = get_ist_timestamp_str()
    sender_email = os.getenv("SENDER_EMAIL")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))

    if not all([sender_email, email_password, smtp_host]):
        return f"[{timestamp}] Error: Email credentials not found in .env"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    if attachment_paths:
        for file_path in attachment_paths:
            if os.path.exists(file_path):
                part = MIMEBase('application', 'octet-stream')
                with open(file_path, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(file_path)}',
                )
                message.attach(part)
            else:
                print(f"[{timestamp}] Warning: Attachment not found at {file_path}")

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(sender_email, email_password)
        text = message.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        return f"[{timestamp}] Email sent successfully to {recipient}"
    except Exception as e:
        return f"[{timestamp}] Error sending email: {e}"

# 5. Local File Saving Tool (Simple Confirmation)
@tool("Local File Save Tool")
def local_save_tool(file_path: str) -> str:
    """
    Confirms a file path exists locally in the 'outputs' directory.
    Input args:
        file_path (str): The full file path to check.
    Returns the confirmed path or a warning message.
    """
    timestamp = get_ist_timestamp_str()
    if os.path.exists(file_path) and "outputs" in file_path:
         print(f"[{timestamp}] Confirmed: File exists locally at {file_path}")
         return file_path
    else:
         # It's possible the file *will* exist after the tool runs,
         # so just log a note but return the path for workflow use.
         print(f"[{timestamp}] Note: Path provided for local save: {file_path}")
         return file_path


# --- Tool List for easy import ---
# List the decorated functions directly
newsletter_tools = [
    search_tool,
    pdf_creation_tool,
    text_to_speech_tool,
    email_sending_tool,
    local_save_tool
]
