# app/ai/clients.py
import os
import logging
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------- OpenAI new-style client ----------
openai_client = None
try:
    from openai import OpenAI as OpenAIClient
    if OPENAI_API_KEY:
        openai_client = OpenAIClient(api_key=OPENAI_API_KEY)
except Exception as e:
    logging.warning("OpenAI client not available: %s", e)

# ---------- Gemini (Google) client ----------
genai = None
try:
    import google.generativeai as genai_m
    if GEMINI_API_KEY:
        genai_m.configure(api_key=GEMINI_API_KEY)
        genai = genai_m
except Exception as e:
    logging.warning("Gemini client not available: %s", e)
