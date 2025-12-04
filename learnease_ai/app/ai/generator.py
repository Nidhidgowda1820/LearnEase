# app/ai/generator.py
import logging, time
from .clients import openai_client, genai

# collector helper (handles streaming or simple text responses)
def collect_text_from_response(resp):
    # resp can be a string, object with .choices/.text, or generator
    if resp is None:
        return ""
    try:
        # direct string
        if isinstance(resp, str):
            return resp
        # openai response object pattern (new SDK)
        if hasattr(resp, "choices"):
            # try to concatenate choices
            parts = []
            for c in resp.choices:
                txt = getattr(c, "message", None) or getattr(c, "delta", None)
                if isinstance(txt, dict):
                    parts.append(txt.get("content") or txt.get("text") or "")
                else:
                    parts.append(str(txt))
            return "".join(parts).strip()
        # genai response object
        if hasattr(resp, "text"):
            return resp.text
        if isinstance(resp, dict) and "content" in resp:
            return resp["content"]
    except Exception as e:
        logging.debug("collect_text_from_response fallback: %s", e)
    # fallback to str
    try:
        return str(resp)
    except:
        return ""

# wrapper to call OpenAI
def call_openai_chat(prompt, model="gpt-4o-mini", temperature=0.2, max_tokens=800):
    if openai_client is None:
        raise RuntimeError("OpenAI client not configured")
    # new OpenAI SDK style
    resp = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return collect_text_from_response(resp)

# wrapper to call Gemini
def call_gemini(prompt, model=None):
    if genai is None:
        raise RuntimeError("Gemini (genai) client not configured")
    # genai.generate or GenerativeModel usage depends on installed version; this is safe-pattern:
    try:
        # high-level API
        result = genai.generate_text(model=model or "models/text-bison-001", prompt=prompt)
        # result may be an object or dict — attempt to extract
        if hasattr(result, "text"):
            return result.text
        if isinstance(result, dict):
            return result.get("candidates", [{}])[0].get("content", "")
        return str(result)
    except Exception:
        # try alternate API
        try:
            m = genai.GenerativeModel(model or "models/text-bison-001")
            out = m.generate_content(prompt)
            return getattr(out, "text", str(out))
        except Exception as e:
            raise

# generate_with_fallback main function
def generate_with_fallback(prompt, prefer="openai", openai_model="gpt-4o-mini", gemini_model=None):
    errs = []
    start = time.time()
    # choose order
    order = [prefer] if prefer in ("openai","gemini") else ["openai","gemini"]
    # ensure both tried if prefer==both
    if prefer == "both":
        order = ["openai", "gemini"]
    for provider in order:
        try:
            if provider == "openai":
                return {"text": call_openai_chat(prompt, model=openai_model), "provider": "openai", "time": time.time()-start}
            elif provider == "gemini":
                return {"text": call_gemini(prompt, model=gemini_model), "provider": "gemini", "time": time.time()-start}
        except Exception as e:
            logging.warning("Provider %s failed: %s", provider, e)
            errs.append((provider, str(e)))
    # last attempt: try the other provider(s) again
    for provider in ["openai","gemini"]:
        if provider not in order:
            try:
                if provider == "openai":
                    return {"text": call_openai_chat(prompt, model=openai_model), "provider": "openai", "time": time.time()-start}
                else:
                    return {"text": call_gemini(prompt, model=gemini_model), "provider": "gemini", "time": time.time()-start}
            except Exception as e:
                errs.append((provider, str(e)))
    raise RuntimeError("All LLM providers failed: " + str(errs))
