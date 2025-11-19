"""
Quick setup verification script.
This will check if all modules can be imported correctly.
"""

import sys

def test_imports():
    """Test all critical imports."""
    print("🔍 Verifying setup...\n")
    
    # Test 1: FastAPI
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__} - OK")
    except Exception as e:
        print(f"❌ FastAPI - FAILED: {e}")
        return False
    
    # Test 2: Uvicorn
    try:
        import uvicorn
        print(f"✅ Uvicorn - OK")
    except Exception as e:
        print(f"❌ Uvicorn - FAILED: {e}")
        return False
    
    # Test 3: Google GenAI
    try:
        from google import genai
        print(f"✅ Google GenAI - OK")
    except Exception as e:
        print(f"❌ Google GenAI - FAILED: {e}")
        return False
    
    # Test 4: GitIngest
    try:
        import gitingest
        print(f"✅ GitIngest - OK")
    except Exception as e:
        print(f"❌ GitIngest - FAILED: {e}")
        return False
    
    # Test 5: Custom modules
    try:
        from modules.cache import load_repo_cache, save_repo_cache
        print(f"✅ Cache Module - OK")
    except Exception as e:
        print(f"❌ Cache Module - FAILED: {e}")
        return False
    
    try:
        from modules.ingest import ingest_repo
        print(f"✅ Ingest Module - OK")
    except Exception as e:
        print(f"❌ Ingest Module - FAILED: {e}")
        return False
    
    try:
        from modules.llm import generate_response
        print(f"✅ LLM Module - OK")
    except Exception as e:
        print(f"❌ LLM Module - FAILED: {e}")
        return False
    
    try:
        from modules.prompt import generate_prompt
        print(f"✅ Prompt Module - OK")
    except Exception as e:
        print(f"❌ Prompt Module - FAILED: {e}")
        return False
    
    # Test 6: Environment variables
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL")
        
        if not api_key:
            print("⚠️  GEMINI_API_KEY not set in .env file")
            print("   Please create a .env file in the project root with:")
            print("   GEMINI_API_KEY=your_key_here")
            print("   GEMINI_MODEL=gemini-1.5-flash")
        else:
            print(f"✅ Environment Variables - OK")
            print(f"   Model: {model or 'not set'}")
    except Exception as e:
        print(f"❌ Environment Variables - FAILED: {e}")
        return False
    
    # Test 7: Cache directory
    import os
    if os.path.exists("cache"):
        print(f"✅ Cache Directory - OK")
    else:
        print(f"⚠️  Cache directory doesn't exist (will be created automatically)")
    
    print("\n" + "=" * 60)
    print("🎉 All critical imports successful!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Make sure you have a .env file with your API keys")
    print("2. Start the server: uvicorn main:app --reload")
    print("3. Run tests: python test_api.py")
    print("4. Or visit: http://localhost:8000/docs")
    
    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

