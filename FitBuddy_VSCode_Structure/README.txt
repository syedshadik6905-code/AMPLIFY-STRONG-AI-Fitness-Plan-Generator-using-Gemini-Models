FitBuddy VS Code starter structure

1. Extract this ZIP.
2. In VS Code choose File > Open Folder and select the extracted FitBuddy_VSCode_Structure folder.
3. Open each file and paste the code into the matching file.
4. Copy .env.example to a new file named .env and put your Gemini API key there. Do not share or commit .env.
5. In the VS Code terminal, from the project root:
   python -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
6. Open http://127.0.0.1:8000

The files are placeholders, not a working app yet. Paste the implementation code into them first.
