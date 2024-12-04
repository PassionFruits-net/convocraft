from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

def get_openai_client():
    return OpenAI()
