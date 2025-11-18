"""
Example of how to integrate llm.py and prompt.py into ConnectionManager.
This shows the key methods that need to be updated in main.py
"""

from typing import Dict, List, Tuple
from fastapi import WebSocket
import logging

from src.utils.llm import generate_response
from src.utils.prompt import generate_prompt

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store active connections: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Store repo context: client_id -> {summary, tree, content}
        self.repo_contexts: Dict[str, Dict[str, str]] = {}
        
        # Store chat history: client_id -> [(user_msg, assistant_msg), ...]
        self.chat_histories: Dict[str, List[Tuple[str, str]]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, owner: str, repo: str):
        """
        Handle new WebSocket connection.
        This is where you'd call ingest_repo and store the context.
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # Initialize empty history for this client
        self.chat_histories[client_id] = []
        
        try:
            # Check cache first (from cache.py)
            # cached_data = get_cached_repo(owner, repo)
            # if cached_data:
            #     summary, tree, content = cached_data
            # else:
            #     # Ingest the repo (from ingest.py)
            #     summary, tree, content = await ingest_repo(owner, repo)
            #     cache_repo(owner, repo, summary, tree, content)
            
            # For this example, assume we got the data:
            # summary, tree, content = ... (from ingest)
            
            # Store repo context for this client
            # self.repo_contexts[client_id] = {
            #     "summary": summary,
            #     "tree": tree,
            #     "content": content
            # }
            
            # Send success message to frontend
            await websocket.send_text("repo_processed")
            logger.info(f"Client {client_id} connected and repo processed")
            
        except Exception as e:
            logger.error(f"Error processing repo for client {client_id}: {e}")
            error_type = "error:unknown"
            
            # Map specific errors to error codes
            if "too large" in str(e).lower():
                error_type = "error:repo_too_large"
            elif "not found" in str(e).lower():
                error_type = "error:repo_not_found"
            elif "private" in str(e).lower():
                error_type = "error:repo_private"
            
            await websocket.send_text(error_type)
            await websocket.close()
    
    async def handle_message(self, client_id: str, message: str):
        """
        Handle incoming chat message from user.
        This is where Task 2 integration happens.
        """
        websocket = self.active_connections.get(client_id)
        if not websocket:
            logger.error(f"No active connection for client {client_id}")
            return
        
        try:
            # Get repo context for this client
            repo_context = self.repo_contexts.get(client_id)
            if not repo_context:
                await websocket.send_text("error:no_repo_context")
                return
            
            # Get chat history for this client
            history = self.chat_histories.get(client_id, [])
            
            # Build the prompt using Task 2 function
            prompt = generate_prompt(
                query=message,
                history=history,
                tree=repo_context["tree"],
                content=repo_context["content"]
            )
            
            # Generate response using LLM with key rotation
            response = await generate_response(prompt)
            
            # Send response back to client
            await websocket.send_text(response)
            
            # Update history with this turn
            history.append((message, response))
            self.chat_histories[client_id] = history
            
            logger.info(f"Processed message for client {client_id}")
            
        except Exception as e:
            logger.error(f"Error handling message for client {client_id}: {e}")
            
            # Send error to client
            error_message = "error:llm_failed"
            if "exhausted" in str(e).lower():
                error_message = "error:quota_exhausted"
            
            await websocket.send_text(error_message)
    
    def disconnect(self, client_id: str):
        """Clean up when client disconnects."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.repo_contexts:
            del self.repo_contexts[client_id]
        if client_id in self.chat_histories:
            del self.chat_histories[client_id]
        
        logger.info(f"Client {client_id} disconnected and cleaned up")


# Usage in main.py FastAPI app:
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
manager = ConnectionManager()

@app.websocket("/{owner}/{repo}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, owner: str, repo: str, client_id: str):
    await manager.connect(websocket, client_id, owner, repo)
    
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await manager.handle_message(client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
"""