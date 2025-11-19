"""
Comprehensive test suite for llm.py module

This test suite covers:
- KeyManager functionality (initialization, rotation, reset)
- generate_response function (success, failure, retries)
- Error handling and edge cases
- Mock integration with Google Generative AI

Run with: python -m pytest tests/test_llm.py -v
"""

import pytest
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import logging

# Add the backend directory to the path for imports
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from src.utils.llm import KeyManager, generate_response


class TestKeyManager:
    """Test suite for the KeyManager class"""
    
    def setup_method(self):
        """Setup before each test method"""
        # Clear any existing environment variables
        self.env_vars_to_clear = []
        for key in os.environ.keys():
            if key.startswith('GEMINI_'):
                self.env_vars_to_clear.append(key)
        
        for key in self.env_vars_to_clear:
            if key in os.environ:
                del os.environ[key]
    
    def teardown_method(self):
        """Cleanup after each test method"""
        # Restore original environment variables if needed
        pass
    
    def test_keymanager_initialization_success(self):
        """Test successful KeyManager initialization with primary key"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key-123',
            'GEMINI_MODEL': 'gemini-1.5-pro'
        }):
            manager = KeyManager()
            
            assert manager.primary_key == 'primary-key-123'
            assert manager.current_key_index == -1
            assert manager.model_name == 'gemini-1.5-pro'
            assert len(manager.fallback_keys) == 0
    
    def test_keymanager_initialization_with_fallback_keys(self):
        """Test KeyManager initialization with multiple fallback keys"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key-123',
            'GEMINI_API_KEY_2': 'fallback-key-1',
            'GEMINI_API_KEY_3': 'fallback-key-2',
            'GEMINI_API_KEY_4': 'fallback-key-3',
            'GEMINI_MODEL': 'gemini-1.5-flash'
        }):
            manager = KeyManager()
            
            assert manager.primary_key == 'primary-key-123'
            assert len(manager.fallback_keys) == 3
            assert manager.fallback_keys[0] == 'fallback-key-1'
            assert manager.fallback_keys[1] == 'fallback-key-2'
            assert manager.fallback_keys[2] == 'fallback-key-3'
            assert manager.model_name == 'gemini-1.5-flash'
    
    def test_keymanager_initialization_failure_no_primary_key(self):
        """Test KeyManager initialization failure when no primary key is set"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY must be set"):
                KeyManager()
    
    def test_keymanager_default_model_name(self):
        """Test KeyManager uses default model name when GEMINI_MODEL is not set"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test-key'
        }):
            manager = KeyManager()
            assert manager.model_name == 'gemini-1.5-flash'
    
    def test_get_current_key_primary(self):
        """Test getting current key when using primary key"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key-123'
        }):
            manager = KeyManager()
            assert manager.get_current_key() == 'primary-key-123'
    
    def test_get_current_key_after_rotation(self):
        """Test getting current key after rotation to fallback"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key-123',
            'GEMINI_API_KEY_2': 'fallback-key-1',
            'GEMINI_API_KEY_3': 'fallback-key-2'
        }):
            manager = KeyManager()
            
            # Rotate to first fallback
            manager.rotate_key()
            assert manager.get_current_key() == 'fallback-key-1'
            
            # Rotate to second fallback
            manager.rotate_key()
            assert manager.get_current_key() == 'fallback-key-2'
    
    def test_rotate_key_success(self):
        """Test successful key rotation"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key',
            'GEMINI_API_KEY_2': 'fallback-1',
            'GEMINI_API_KEY_3': 'fallback-2'
        }):
            manager = KeyManager()
            
            # First rotation should succeed
            assert manager.rotate_key() == True
            assert manager.current_key_index == 0
            
            # Second rotation should succeed
            assert manager.rotate_key() == True
            assert manager.current_key_index == 1
    
    def test_rotate_key_failure_no_more_keys(self):
        """Test key rotation failure when no more keys available"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key',
            'GEMINI_API_KEY_2': 'fallback-1'
        }):
            manager = KeyManager()
            
            # Rotate to only available fallback
            assert manager.rotate_key() == True
            assert manager.current_key_index == 0
            
            # Try to rotate again - should fail
            assert manager.rotate_key() == False
            assert manager.current_key_index == 0  # Should stay at last valid index
    
    def test_rotate_key_no_fallback_keys(self):
        """Test key rotation when no fallback keys exist"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key-only'
        }):
            manager = KeyManager()
            
            # Should fail immediately since no fallback keys
            assert manager.rotate_key() == False
            assert manager.current_key_index == -1  # Should stay at primary
    
    def test_reset_functionality(self):
        """Test reset functionality returns to primary key"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key',
            'GEMINI_API_KEY_2': 'fallback-1',
            'GEMINI_API_KEY_3': 'fallback-2'
        }):
            manager = KeyManager()
            
            # Rotate to fallback keys
            manager.rotate_key()
            manager.rotate_key()
            assert manager.current_key_index == 1
            assert manager.get_current_key() == 'fallback-2'
            
            # Reset should return to primary
            manager.reset()
            assert manager.current_key_index == -1
            assert manager.get_current_key() == 'primary-key'


class TestGenerateResponse:
    """Test suite for the generate_response function"""
    
    def setup_method(self):
        """Setup before each test method"""
        # Reset global key_manager state
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test-primary-key',
            'GEMINI_API_KEY_2': 'test-fallback-key',
            'GEMINI_MODEL': 'gemini-1.5-flash'
        }):
            # Import and reset the global key_manager
            from src.utils.llm import key_manager
            key_manager.reset()
    
    @pytest.mark.asyncio
    @patch('src.utils.llm.genai')
    async def test_generate_response_success(self, mock_genai):
        """Test successful response generation"""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini"
        
        mock_model = AsyncMock()
        mock_model.generate_content_async.return_value = mock_response
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test
        result = await generate_response("Test prompt")
        
        # Assertions
        assert result == "This is a test response from Gemini"
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash')
        mock_model.generate_content_async.assert_called_once_with("Test prompt")
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    async def test_generate_response_empty_response(self, mock_genai):
        """Test handling of empty response from API"""
        # Setup mock with empty response
        mock_response = Mock()
        mock_response.text = None
        
        mock_model = AsyncMock()
        mock_model.generate_content_async.return_value = mock_response
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test should raise exception
        with pytest.raises(Exception, match="Empty response from LLM"):
            await generate_response("Test prompt")
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    async def test_generate_response_no_response_object(self, mock_genai):
        """Test handling when no response object is returned"""
        mock_model = AsyncMock()
        mock_model.generate_content_async.return_value = None
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test should raise exception
        with pytest.raises(Exception, match="Empty response from LLM"):
            await generate_response("Test prompt")
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    @patch('utils.llm.key_manager')
    async def test_generate_response_quota_error_with_successful_retry(self, mock_key_manager, mock_genai):
        """Test quota error handling with successful key rotation and retry"""
        # Setup mock key manager
        mock_key_manager.get_current_key.side_effect = ['key1', 'key2']
        mock_key_manager.rotate_key.return_value = True
        mock_key_manager.model_name = 'gemini-1.5-flash'
        
        # Setup mock model that fails first time, succeeds second time
        mock_model = AsyncMock()
        quota_error = Exception("quota exhausted")
        
        success_response = Mock()
        success_response.text = "Success after retry"
        
        mock_model.generate_content_async.side_effect = [quota_error, success_response]
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test
        result = await generate_response("Test prompt")
        
        # Assertions
        assert result == "Success after retry"
        assert mock_key_manager.rotate_key.called
        assert mock_model.generate_content_async.call_count == 2
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    @patch('utils.llm.key_manager')
    async def test_generate_response_quota_error_all_keys_exhausted(self, mock_key_manager, mock_genai):
        """Test quota error when all keys are exhausted"""
        # Setup mock key manager
        mock_key_manager.get_current_key.return_value = 'test-key'
        mock_key_manager.rotate_key.return_value = False  # No more keys
        mock_key_manager.model_name = 'gemini-1.5-flash'
        
        # Setup mock model that always fails with quota error
        mock_model = AsyncMock()
        quota_error = Exception("quota exhausted")
        mock_model.generate_content_async.side_effect = quota_error
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test should raise exception
        with pytest.raises(Exception, match="All API keys exhausted"):
            await generate_response("Test prompt")
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    async def test_generate_response_non_quota_error(self, mock_genai):
        """Test handling of non-quota related errors (should not retry)"""
        # Setup mock model that fails with non-quota error
        mock_model = AsyncMock()
        api_error = Exception("Invalid request format")
        mock_model.generate_content_async.side_effect = api_error
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test should raise exception without retrying
        with pytest.raises(Exception, match="LLM generation failed"):
            await generate_response("Test prompt")
        
        # Should only call once (no retries for non-quota errors)
        assert mock_model.generate_content_async.call_count == 1
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    @patch('utils.llm.key_manager')
    async def test_generate_response_max_retries_exceeded(self, mock_key_manager, mock_genai):
        """Test max retries exceeded scenario"""
        # Setup mock key manager that always allows rotation
        mock_key_manager.get_current_key.return_value = 'test-key'
        mock_key_manager.rotate_key.return_value = True
        mock_key_manager.model_name = 'gemini-1.5-flash'
        
        # Setup mock model that always fails with quota error
        mock_model = AsyncMock()
        quota_error = Exception("quota exhausted")
        mock_model.generate_content_async.side_effect = quota_error
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test with max_retries=1 should fail after 2 attempts
        with pytest.raises(Exception, match="Max retries exceeded"):
            await generate_response("Test prompt", max_retries=1)
        
        # Should call twice (initial + 1 retry)
        assert mock_model.generate_content_async.call_count == 2
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    async def test_generate_response_rate_limit_detection(self, mock_genai):
        """Test detection of rate limit errors (429, 'rate limit')"""
        # Test different quota/rate limit error messages
        error_messages = [
            "429 Too Many Requests",
            "Rate limit exceeded",
            "QUOTA_EXCEEDED",
            "quota exhausted"
        ]
        
        for error_msg in error_messages:
            mock_model = AsyncMock()
            mock_model.generate_content_async.side_effect = Exception(error_msg)
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Should treat as quota error and attempt retry logic
            with patch('utils.llm.key_manager') as mock_key_manager:
                mock_key_manager.get_current_key.return_value = 'test-key'
                mock_key_manager.rotate_key.return_value = False  # Fail rotation to stop retry
                mock_key_manager.model_name = 'gemini-1.5-flash'
                
                with pytest.raises(Exception, match="All API keys exhausted"):
                    await generate_response("Test prompt")


class TestIntegration:
    """Integration tests combining KeyManager and generate_response"""
    
    @pytest.mark.asyncio
    @patch('utils.llm.genai')
    async def test_full_key_rotation_cycle(self, mock_genai):
        """Test complete key rotation cycle during response generation"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'primary-key',
            'GEMINI_API_KEY_2': 'fallback-1',
            'GEMINI_API_KEY_3': 'fallback-2'
        }):
            # Create fresh KeyManager instance
            from src.utils.llm import KeyManager
            test_key_manager = KeyManager()
            
            # Setup mock model that fails twice, then succeeds
            mock_model = AsyncMock()
            quota_error = Exception("quota exhausted")
            success_response = Mock()
            success_response.text = "Finally successful"
            
            mock_model.generate_content_async.side_effect = [
                quota_error,  # Fail with primary key
                quota_error,  # Fail with fallback-1
                success_response  # Success with fallback-2
            ]
            
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Patch the global key_manager with our test instance
            with patch('utils.llm.key_manager', test_key_manager):
                result = await generate_response("Test prompt", max_retries=3)
            
            # Should succeed with final key
            assert result == "Finally successful"
            assert test_key_manager.current_key_index == 1  # Should be at fallback-2
            assert mock_model.generate_content_async.call_count == 3


# Test fixtures and utilities
@pytest.fixture
def mock_environment():
    """Fixture providing a clean test environment"""
    env_patch = patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-primary-key',
        'GEMINI_API_KEY_2': 'test-fallback-1',
        'GEMINI_API_KEY_3': 'test-fallback-2',
        'GEMINI_MODEL': 'gemini-1.5-flash'
    })
    with env_patch:
        yield


def test_logging_output(caplog):
    """Test that appropriate log messages are generated"""
    with patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_API_KEY_2': 'fallback-key'
    }):
        with caplog.at_level(logging.INFO):
            manager = KeyManager()
            
        # Check initialization log
        assert "KeyManager initialized" in caplog.text
        assert "1 fallback keys" in caplog.text


if __name__ == "__main__":
    print("🧪 Running LLM Module Tests...")
    print("=" * 50)
    
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short", "--color=yes"])