import os
from .config import OPENAI_API_KEY, GENIE_API_KEY, LOCAL_LLM
try:
    import openai
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
except Exception:
    openai = None

try:
    import google.generativeai as genai
    if GENIE_API_KEY:
        genai.configure(api_key=GENIE_API_KEY)
except Exception:
    genai = None

_local_pipe = None
def call_local(prompt, max_len=256):
    global _local_pipe
    if _local_pipe is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        tokenizer = AutoTokenizer.from_pretrained(LOCAL_LLM)
        model = AutoModelForSeq2SeqLM.from_pretrained(LOCAL_LLM)
        _local_pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_length=max_len)
    out = _local_pipe(prompt, do_sample=False, num_beams=2)
    return out[0]["generated_text"]

def call_openai(prompt, model="gpt-4o-mini", max_tokens=500, temperature=0.0):
    if openai is None:
        raise RuntimeError("OpenAI not available or API key not set")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"user","content":prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return resp.choices[0].message.content

def call_gemini(prompt, model=None):
    if genai is None:
        raise RuntimeError("Gemini not available or API key not set")
    model = model or "gemini-1.0"
    gm = genai.GenerativeModel(model)
    r = gm.generate_content(prompt)
    return r.text
