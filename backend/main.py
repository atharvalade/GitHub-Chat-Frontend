from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from modules.cache import load_repo_cache, save_repo_cache
from modules.ingest import ingest_repo  # type: ignore
from modules.llm import generate_response  # type: ignore
from modules.prompt import generate_prompt  # type: ignore

import os
import sys
import asyncio
from dotenv import load_dotenv
import logging

# Fix for Python 3.13 on Windows - Use ProactorEventLoop for subprocess support
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()

IS_PROD = os.getenv("ENV") == "production"


app = FastAPI(
    title="Talk to GitHub",
    description="A simple chat app to interact with GitHub repositories",
    version="0.1.0",
    license_info={"name": "MIT License"},
    openapi_url=None if IS_PROD else "/openapi.json",
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
)

if not IS_PROD:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# Request/Response Models
class InitializeRepoRequest(BaseModel):
    owner: str
    repo: str


class InitializeRepoResponse(BaseModel):
    status: str
    message: str
    summary: str
    tree: str


class ChatRequest(BaseModel):
    owner: str
    repo: str
    query: str
    history: list[tuple[str, str]] = []


class ChatResponse(BaseModel):
    response: str
    history: list[tuple[str, str]]


class HealthCheckResponse(BaseModel):
    status: str


# API Endpoints
@app.post("/api/repository/initialize", response_model=InitializeRepoResponse)
async def initialize_repository(request: InitializeRepoRequest):
    """
    Initialize and process a GitHub repository.
    
    This endpoint will either load the repository from cache or ingest it fresh.
    """
    owner = request.owner
    repo = request.repo
    repo_url = f"https://github.com/{owner}/{repo}"
    
    logging.info(f"Processing repo: {repo_url}...")
    
    # Try to load from cache first
    cached = load_repo_cache(owner, repo)
    if cached:
        summary, tree, content = cached["summary"], cached["tree"], cached["content"]
        logging.info(f"Loaded repo from cache: {repo_url}")
        return InitializeRepoResponse(
            status="success",
            message="Repository loaded from cache",
            summary=summary,
            tree=tree
        )
    
    # If not in cache, ingest the repository
    try:
        summary, tree, content = await ingest_repo(repo_url)
        logging.info(f"Repo processed - {repo_url}!")
        logging.info(f"Repository Summary:\n{summary}")
        save_repo_cache(owner, repo, summary, tree, content)
        
        return InitializeRepoResponse(
            status="success",
            message="Repository processed successfully",
            summary=summary,
            tree=tree
        )
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "error:repo_too_large":
            raise HTTPException(status_code=413, detail="Repository is too large to process")
        elif error_msg == "error:repo_not_found":
            raise HTTPException(status_code=404, detail="Repository not found")
        elif error_msg == "error:repo_private":
            raise HTTPException(status_code=403, detail="Repository is private or inaccessible")
        else:
            logging.error(f"Error processing repository: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing repository: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a query about the repository and get a response.
    
    The history of previous interactions should be included in the request
    to maintain conversation context.
    """
    owner = request.owner
    repo = request.repo
    query = request.query
    history = request.history
    
    logging.info(f"Received chat query for {owner}/{repo}: {query}...")
    
    # Load repository data from cache
    cached = load_repo_cache(owner, repo)
    if not cached:
        raise HTTPException(
            status_code=404,
            detail="Repository not found in cache. Please initialize it first."
        )
    
    summary = cached["summary"]  # noqa: F841
    tree = cached["tree"]
    content = cached["content"]
    
    # Generate prompt and response
    logging.info(f"Generating prompt for query: {query}...")
    prompt = await generate_prompt(query, history, tree, content)
    logging.info(f"Prompt generated: {prompt[:100]}...")
    
    try:
        response = await generate_response(prompt)
        logging.info(f"Response generated: {response[:100]}...")
        
        # Update history with the new interaction
        updated_history = history + [(query, response)]
        
        return ChatResponse(
            response=response,
            history=updated_history
        )
    except ValueError as e:
        if "OUT_OF_KEYS" in str(e):
            raise HTTPException(
                status_code=429,
                detail="All API keys have been exhausted. Please try again in a few minutes."
            )
        else:
            logging.error(f"Error generating response: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/healthcheck", response_model=HealthCheckResponse)
async def healthcheck():
    """Health check endpoint to verify the API is running."""
    return HealthCheckResponse(status="ok")


async def main():
    """Test function to verify the application works."""
    summary, tree, content = await ingest_repo("https://github.com/aniketlavasare/New-Year-Countdown-WebApp")
    prompt = await generate_prompt(
        "How does this codebase work? What is it built using?", [], tree, content
    )
    response = await generate_response(prompt)
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

