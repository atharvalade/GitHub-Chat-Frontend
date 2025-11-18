import os
import logging
from typing import Optional, List
import google.generativeai as genai

logger = logging.getLogger(__name__)


class KeyManager:
    """Manages API keys with automatic rotation on quota exhaustion."""
    
    def __init__(self):
        self.primary_key = os.getenv("GEMINI_API_KEY")
        if not self.primary_key:
            raise ValueError("GEMINI_API_KEY must be set in environment")
        
        # Load fallback keys (GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.)
        self.fallback_keys: List[str] = []
        i = 2
        while True:
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if not key:
                break
            self.fallback_keys.append(key)
            i += 1
        
        self.current_key_index = -1  # -1 means primary key
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        logger.info(f"KeyManager initialized with primary key and {len(self.fallback_keys)} fallback keys")
    
    def get_current_key(self) -> str:
        """Returns the currently active API key."""
        if self.current_key_index == -1:
            return self.primary_key
        return self.fallback_keys[self.current_key_index]
    
    def rotate_key(self) -> bool:
        """
        Rotates to the next available API key.
        Returns True if rotation was successful, False if no more keys available.
        """
        if self.current_key_index < len(self.fallback_keys) - 1:
            self.current_key_index += 1
            logger.warning(f"Rotated to fallback key #{self.current_key_index + 1}")
            return True
        else:
            logger.error("No more API keys available for rotation")
            return False
    
    def reset(self):
        """Reset to primary key (useful for testing or manual reset)."""
        self.current_key_index = -1
        logger.info("Reset to primary API key")


# Global KeyManager instance
key_manager = KeyManager()


async def generate_response(prompt: str, max_retries: int = 2) -> str:
    """
    Generate a response from Gemini using the prompt.
    Automatically handles key rotation on quota errors.
    
    Args:
        prompt: The complete prompt to send to the LLM
        max_retries: Maximum number of key rotations to attempt
        
    Returns:
        The generated text response
        
    Raises:
        Exception: If all keys are exhausted or other errors occur
    """
    retries = 0
    
    while retries <= max_retries:
        try:
            # Configure the API with current key
            current_key = key_manager.get_current_key()
            genai.configure(api_key=current_key)
            
            # Initialize the model
            model = genai.GenerativeModel(key_manager.model_name)
            
            # Generate response
            logger.info(f"Sending prompt to {key_manager.model_name} (length: {len(prompt)} chars)")
            response = await model.generate_content_async(prompt)
            
            # Extract text from response
            if not response or not response.text:
                raise ValueError("Empty response from LLM")
            
            logger.info(f"Received response (length: {len(response.text)} chars)")
            return response.text
            
        except Exception as e:
            error_message = str(e).lower()
            
            # Check if it's a quota/rate limit error
            if "quota" in error_message or "rate limit" in error_message or "429" in error_message:
                logger.warning(f"Quota exhausted on attempt {retries + 1}: {e}")
                
                # Try to rotate to next key
                if key_manager.rotate_key():
                    retries += 1
                    logger.info(f"Retrying with new key (attempt {retries + 1}/{max_retries + 1})")
                    continue
                else:
                    raise Exception("All API keys exhausted") from e
            else:
                # Non-quota error, don't retry
                logger.error(f"LLM error: {e}")
                raise Exception(f"LLM generation failed: {str(e)}") from e
    
    raise Exception("Max retries exceeded")