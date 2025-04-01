import os
from dotenv import load_dotenv

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not ASTRA_DB_APPLICATION_TOKEN or not ASTRA_DB_ID or not GROQ_API_KEY:
    raise ValueError("Missing environment variables! Check your .env file.")
