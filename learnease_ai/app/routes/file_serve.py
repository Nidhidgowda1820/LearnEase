import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from ..ai import config

router = APIRouter()

# Directory constants
DATA_ROOT = os.path.abspath(os.path.join(config.DATA_DIR, "raw"))
SUBJECT_ROOT = os.path.join(DATA_ROOT, "3rd Y", "5th Sem", "CSE")

# MIME type mapping
MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.zip': 'application/zip',
}

@router.get("/api/files/{subject}/{category}/{filename:path}")
async def serve_file(
    subject: str,
    category: str,
    filename: str,
):
    """
    Serve files with proper content-type headers.
    Example: /api/files/ML/Textbooks/book.pdf
    """
    # Security: prevent path traversal
    if ".." in subject or ".." in category or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # Clean path components
    subject = subject.strip()
    category = category.strip()
    filename = filename.strip()
    
    # Build file path
    file_path = os.path.join(SUBJECT_ROOT, subject, category, filename)
    
    # Normalize path to prevent directory traversal
    file_path = os.path.normpath(file_path)
    
    # Verify it's within the allowed directory
    if not file_path.startswith(os.path.abspath(SUBJECT_ROOT)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type
    ext = Path(filename).suffix.lower()
    media_type = MIME_TYPES.get(ext, 'application/octet-stream')
    
    # For PDFs, add inline disposition so they open in browser
    headers = {}
    if ext == '.pdf':
        headers['Content-Disposition'] = f'inline; filename="{filename}"'
    else:
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return FileResponse(
        file_path,
        media_type=media_type,
        headers=headers,
        filename=filename,
    )

