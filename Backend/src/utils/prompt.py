"""
Prompt generation utilities for the GitHub repository chat system.
"""

from typing import List, Tuple


def generate_prompt(query: str, history: List[Tuple[str, str]], tree: str, content: str) -> str:
    """
    Generate a comprehensive prompt for the LLM based on user query and repository context.
    
    Args:
        query: User's question or request
        history: List of (user_message, assistant_response) tuples from chat history
        tree: Repository file tree structure
        content: Repository file contents and metadata
        
    Returns:
        Formatted prompt string for the LLM
    """
    # Format chat history (limit to last 5 exchanges to avoid token limits)
    history_text = ""
    if history:
        recent_history = history[-5:]  # Get last 5 exchanges
        history_items = []
        for user_msg, assistant_msg in recent_history:
            history_items.append(f"User: {user_msg}")
            history_items.append(f"Assistant: {assistant_msg}")
        history_text = "\n".join(history_items)
    
    # Build the comprehensive prompt
    prompt = f"""You are an AI assistant specialized in analyzing GitHub repositories. Your role is to help users understand codebases, answer questions about implementation details, explain architectural decisions, and provide insights about the project.

## Repository Context

### File Structure:
{tree}

### Repository Content:
{content}

## Chat History:
{history_text if history_text else "No previous conversation"}

## Current User Query:
{query}

## Instructions:
- Provide accurate, helpful responses based on the repository content
- Reference specific files, functions, or code sections when relevant
- If the query is about code implementation, explain the logic clearly
- If asking about architecture or design patterns, provide high-level insights
- If the information isn't available in the repository, clearly state that
- Keep responses conversational but informative
- Use markdown formatting for better readability when showing code snippets

Please respond to the user's query:"""

    return prompt


def generate_system_prompt() -> str:
    """
    Generate a system prompt that sets the context for the AI assistant.
    """
    return """You are an expert GitHub repository analyst and code assistant. You help developers understand codebases by:

1. Analyzing code structure and architecture
2. Explaining implementation details and design patterns  
3. Answering questions about specific functions, classes, or modules
4. Providing insights about project setup, dependencies, and configuration
5. Helping with debugging and troubleshooting based on code context

Always base your responses on the provided repository content and be honest about limitations."""


def format_code_snippet(code: str, language: str = "python", file_path: str = "") -> str:
    """
    Format a code snippet for inclusion in LLM responses.
    
    Args:
        code: The code content
        language: Programming language for syntax highlighting
        file_path: Optional file path for context
        
    Returns:
        Formatted code snippet string
    """
    header = f" {file_path}" if file_path else ""
    return f"```{language}{header}\n{code}\n```"


def truncate_content(content: str, max_tokens: int = 100000) -> str:
    """
    Truncate content to fit within token limits while preserving important information.
    
    Args:
        content: Content to truncate
        max_tokens: Approximate maximum token count (rough estimate: 4 chars = 1 token)
        
    Returns:
        Truncated content string
    """
    max_chars = max_tokens * 4  # Rough approximation
    
    if len(content) <= max_chars:
        return content
    
    # Try to truncate at a reasonable boundary (end of file or function)
    truncated = content[:max_chars]
    
    # Find last complete line
    last_newline = truncated.rfind('\n')
    if last_newline > max_chars * 0.8:  # If we're not losing too much
        truncated = truncated[:last_newline]
    
    return truncated + "\n\n... (content truncated due to length)"
