# app/ai/prompting.py
PROMPT_HEADER = """
You are an expert college teacher. Produce a concise answer suitable for an exam question.
REQUIREMENTS:
- Write answer for EXACTLY {marks} marks.
- If diagrams are necessary, include a labeled diagram placeholder and refer to available figure IDs or image URLs.
- Include the textbook name and page number(s) where the information came from.
- If the extracted page text is garbled/poor-quality, fix spelling/formatting and produce a clean answer. If the page is useless, use your general knowledge to answer but still cite the page(s) you searched (mark them as LOW_QUALITY).
- Keep answer well-structured: Short definition, key points, steps/algorithm (if applicable), and 1–2 example lines if needed.

Below are retrieved source chunks. Each chunk has fields:
[BOOK_TITLE] — the book filename used when ingesting
[PAGE] — page number
[QUALITY] — page quality score (0-1) or null
[FIGURES] — list of figures for that page (with `figure_id` and `image_path` if available)
[TEXT] — the extracted text chunk
---

{retrieved_chunks}

Now, produce the answer (no JSON, just structured text). At the end append a "SOURCES" section listing each cited book and page used, and list FIGURES separately with figure_id and image_path if you included any.
"""

# helper to render the retrieved chunks into the prompt:
def render_chunks_for_prompt(chunks_meta_text):
    # chunks_meta_text is list of dicts: {'book','page','quality','figures','text'}
    parts = []
    for c in chunks_meta_text:
        figs = c.get("figures") or []
        figstr = ", ".join([f"{f.get('figure_id')}|{f.get('image_path')}" for f in figs]) if figs else "[]"
        parts.append(
            f"[BOOK_TITLE] {c['book']}\n[PAGE] {c['page']}\n[QUALITY] {c.get('quality')}\n[FIGURES] {figstr}\n[TEXT]\n{c['text']}\n---"
        )
    return "\n".join(parts)

def build_prompt(chunks_meta_text, question, marks):
    body = render_chunks_for_prompt(chunks_meta_text)
    return PROMPT_HEADER.format(retrieved_chunks=body, marks=marks)
