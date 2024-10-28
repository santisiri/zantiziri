import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GPT_MODELS = [
    {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'default': True},
    {'id': 'gpt-4', 'name': 'GPT-4'},
    {'id': 'gpt-3', 'name': 'GPT-3'}
]

# Load the prompt template
try:
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        SCRIPT_PROMPT = f.read()
except FileNotFoundError:
    SCRIPT_PROMPT = """
    Create a script for a video based on the following summary. 
    The script should be engaging, informative, and suitable for social media.
    """

# Set up OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable in your .env file")

# Configure OpenAI
import openai
openai.api_key = openai_api_key
