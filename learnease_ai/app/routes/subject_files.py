import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from ..ai import config

router = APIRouter()

# Directory constants
DATA_ROOT = os.path.abspath(os.path.join(config.DATA_DIR, "raw"))
SUBJECT_ROOT = os.path.join(DATA_ROOT, "3rd Y", "5th Sem", "CSE")

# category key -> directory name
CATEGORY_DIRS: List[Tuple[str, str]] = [
    ("Textbooks", "Textbooks"),
    ("Notes", "Notes"),
    ("PY_M_QP", "PY_M QP"),
    ("Syllabus", "Syllabus"),
    ("Copy", "Copy"),
]

# Friendly subject name aliases to actual folder names
SUBJECT_ALIASES: Dict[str, List[str]] = {
    "CNS": ["cns", "cryptography and network security", "cryptography", "network security"],
    "ML": ["ml", "machine learning"],
    "TOC": ["toc", "automata theory", "automata theory(toc)", "theory of computation"],
    "FCG": ["fcg", "fundamentals of computer graphics", "computer graphics"],
}


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def resolve_subject_folder(subject: str) -> Optional[str]:
    if not subject:
        return None
    normalized = _normalize(subject)
    for folder, aliases in SUBJECT_ALIASES.items():
        if normalized == _normalize(folder) or normalized in [_normalize(a) for a in aliases]:
            return folder

    if not os.path.isdir(SUBJECT_ROOT):
        return None
    for entry in os.listdir(SUBJECT_ROOT):
        if os.path.isdir(os.path.join(SUBJECT_ROOT, entry)) and _normalize(entry) == normalized:
            return entry
    return None


def format_size(size_bytes: int) -> str:
    power = 1024
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    for unit in units:
        if size < power:
            return f"{size:.1f} {unit}"
        size /= power
    return f"{size:.1f} PB"


@router.get("/api/subject_files")
def get_subject_files(
    request: Request,
    subject: str = Query(..., description="Subject name (e.g., ML, CNS, TOC, FCG)"),
):
    if ".." in subject or "/" in subject or "\\" in subject:
        raise HTTPException(status_code=400, detail="Invalid subject value")

    subject_folder = resolve_subject_folder(subject)
    if not subject_folder:
        raise HTTPException(status_code=404, detail=f"Subject '{subject}' not found")

    subj_path = os.path.join(SUBJECT_ROOT, subject_folder)
    if not os.path.isdir(subj_path):
        raise HTTPException(status_code=404, detail=f"Subject '{subject}' not found")

    files: Dict[str, List[Dict[str, str]]] = {key: [] for key, _ in CATEGORY_DIRS}

    host = request.headers.get("host")
    scheme = request.url.scheme
    base_url = f"{scheme}://{host}"

    # ✅ FIX: define subject_base_url properly
    relative_subject_path = os.path.relpath(subj_path, DATA_ROOT)
    subject_base_url = f"{base_url}/static/data/raw/{relative_subject_path.replace(os.sep, '/')}"

    for json_key, dir_name in CATEGORY_DIRS:
        cat_path = os.path.join(subj_path, dir_name)
        if not os.path.isdir(cat_path):
            continue
        try:
            for fname in sorted(os.listdir(cat_path)):
                fpath = os.path.join(cat_path, fname)
                if not os.path.isfile(fpath):
                    continue
                stat = os.stat(fpath)
                file_url = f"{base_url}/api/files/{quote(subject_folder)}/{quote(dir_name)}/{quote(fname)}"
                files[json_key].append(
                    {
                        "name": fname,
                        "size": format_size(stat.st_size),
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "url": file_url,
                    }
                )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Error reading '{dir_name}': {exc}") from exc

    return JSONResponse(
        content={
            "subject": subject_folder,
            "root_url": subject_base_url,
            "files": files,
        }
    )
