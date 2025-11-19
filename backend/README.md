# GitHub Chat Backend

FastAPI backend for interacting with GitHub repositories using AI.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (or backend directory) with the following:

```env
# Required
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Optional - for fallback keys
FALLBACK_COUNT=0
# FALLBACK_1=your_backup_key_here
# FALLBACK_2=your_backup_key_here

# Optional - environment setting
ENV=development
```

Get your Gemini API key from: https://aistudio.google.com/apikey

### 3. Run the Server

**Development mode (with auto-reload):**
```bash
cd backend
uvicorn main:app --reload
```

**Production mode:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start at: `http://localhost:8000`

### 4. Test the API

#### Option 1: Use the Interactive Docs (Recommended)
Open your browser and go to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Option 2: Use the Test Script
Run the built-in test in main.py:
```bash
cd backend
python main.py
```

#### Option 3: Use curl or PowerShell

**Health Check:**
```powershell
curl http://localhost:8000/healthcheck
```

**Initialize a Repository:**
```powershell
curl -X POST http://localhost:8000/api/repository/initialize `
  -H "Content-Type: application/json" `
  -d '{\"owner\": \"facebook\", \"repo\": \"react\"}'
```

**Chat with the Repository:**
```powershell
curl -X POST http://localhost:8000/api/chat `
  -H "Content-Type: application/json" `
  -d '{\"owner\": \"facebook\", \"repo\": \"react\", \"query\": \"What is this repo about?\", \"history\": []}'
```

## API Endpoints

### `GET /healthcheck`
Check if the API is running.

### `POST /api/repository/initialize`
Initialize and process a GitHub repository.

**Request Body:**
```json
{
  "owner": "facebook",
  "repo": "react"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Repository processed successfully",
  "summary": "...",
  "tree": "..."
}
```

### `POST /api/chat`
Send a query about the repository.

**Request Body:**
```json
{
  "owner": "facebook",
  "repo": "react",
  "query": "What is this repo about?",
  "history": []
}
```

**Response:**
```json
{
  "response": "This is a library for building user interfaces...",
  "history": [["What is this repo about?", "This is a library..."]]
}
```

## Troubleshooting

### Import Errors
Make sure you're running from the backend directory:
```bash
cd backend
python main.py
```

### Module Not Found
Install missing dependencies:
```bash
pip install -r requirements.txt
```

### API Key Issues
- Verify your `.env` file is in the correct location (project root or backend directory)
- Check that your `GEMINI_API_KEY` is valid
- Make sure the `.env` file has no extra spaces or quotes around values

### Port Already in Use
Change the port:
```bash
uvicorn main:app --reload --port 8001
```

