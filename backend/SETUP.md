# Backend Setup Guide

## ✅ Setup Complete!

Your virtual environment has been created and all dependencies are installed.

## 📦 What Was Installed

- **FastAPI** - Web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI
- **Google GenAI** - For Gemini API integration
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variable management
- **And more...** (see requirements.txt)

## 🚀 Quick Start

### Activate Virtual Environment

**Every time** you open a new terminal, activate the virtual environment:

```powershell
cd backend
.\activate.ps1
```

Or manually:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

You'll see `(venv)` in your terminal prompt when activated.

### Run the Server

```powershell
uvicorn main:app --reload
```

Server will run at: http://localhost:8000

### Deactivate Virtual Environment

When you're done:

```powershell
deactivate
```

## 📁 Project Structure

```
backend/
├── venv/                   # Virtual environment (ignored by git)
├── modules/                # Your modules
│   ├── cache.py
│   ├── ingest.py
│   ├── llm.py
│   └── prompt.py
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── test_api.py            # API test script
├── activate.ps1           # Quick activation script
└── README.md              # Detailed documentation
```

## 🔧 Common Commands

```powershell
# Install a new package
pip install package-name

# Update requirements.txt after installing new packages
pip freeze > requirements.txt

# Check installed packages
pip list

# Update all packages
pip install --upgrade -r requirements.txt
```

## 🌐 Environment Variables

Don't forget to create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
FALLBACK_COUNT=0
ENV=development
```

## 🧪 Testing

Run tests:
```powershell
python test_api.py
```

Run the main test:
```powershell
python main.py
```

## 📚 Documentation

Once the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚠️ Important Notes

1. **Always activate** the virtual environment before running any Python commands
2. The `venv/` folder is **ignored by git** (in .gitignore)
3. Your `.env` file is also **ignored by git** (never commit API keys!)
4. If you get import errors, make sure you're in the `backend/` directory

## 🐛 Troubleshooting

### "cannot be loaded because running scripts is disabled"
Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Module not found errors
Make sure virtual environment is activated and requirements are installed:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port already in use
Change the port:
```powershell
uvicorn main:app --reload --port 8001
```

