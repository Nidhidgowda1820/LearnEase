# LearnEase Subject Files Feature Implementation

## Completed Tasks
- [x] Create `learnease_ai/app/routes/subject_files.py` with GET `/api/subject_files` route
  - Case-insensitive subject folder search in `data/raw`
  - File categorization: Textbooks, Notes, PY_M QP, Syllabus, Copy
  - Filter allowed extensions: .pdf, .txt, .docx, .png, .jpg, .jpeg
  - Return JSON with subject, base_path, and categorized files
- [x] Edit `learnease_ai/app/ai/server.py` to include the subject_files router
- [x] Create `LearnEase-frontend/LearnEase/lib/screens/subject_files_screen.dart`
  - StatefulWidget that fetches and displays files in collapsible sections
  - Open files using url_launcher
- [x] Edit `LearnEase-frontend/LearnEase/lib/screens/syllabus_screen.dart`
  - Add onTap to ListTile for navigation to SubjectFilesScreen
  - Import SubjectFilesScreen

## Verification
- [ ] Test API endpoint: GET /api/subject_files?subject=Machine%20Learning
- [ ] Test frontend navigation from syllabus to subject files screen
- [ ] Test file opening functionality
- [ ] Verify static file serving from /static route

## Notes
- url_launcher dependency already present in pubspec.yaml
- Server already mounts /static to data/raw directory
- Files are served via /static/{subject_folder}/{filename} URLs
