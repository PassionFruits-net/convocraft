import os
import openai
import streamlit as st
from dotenv import load_dotenv

def get_openai_client():
    load_dotenv()
    return openai.OpenAI()