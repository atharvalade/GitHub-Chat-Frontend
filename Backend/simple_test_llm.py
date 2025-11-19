"""
Simple test for the LLM module - Test your code!

This is a simplified test that validates the core functionality
of your llm.py module. Run with: python simple_test_llm.py
"""

import os
import sys
import asyncio
from unittest.mock import patch, Mock, AsyncMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_key_manager_basic():
    """Test KeyManager basic functionality"""
    print("🧪 Testing KeyManager...")
    
    # Test with environment variables
    with patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-primary-key',
        'GEMINI_API_KEY_2': 'test-fallback-1', 
        'GEMINI_API_KEY_3': 'test-fallback-2',
        'GEMINI_MODEL': 'gemini-1.5-flash'
    }):
        from src.utils.llm import KeyManager
        
        # Test initialization
        manager = KeyManager()
        assert manager.primary_key == 'test-primary-key'
        assert len(manager.fallback_keys) == 2
        print("  ✅ Initialization works")
        
        # Test get current key
        assert manager.get_current_key() == 'test-primary-key'
        print("  ✅ Get current key works")
        
        # Test rotation
        result = manager.rotate_key()
        assert result == True
        assert manager.get_current_key() == 'test-fallback-1'
        print("  ✅ Key rotation works")
        
        # Test reset
        manager.reset()
        assert manager.get_current_key() == 'test-primary-key'
        print("  ✅ Reset works")


def test_key_manager_no_fallbacks():
    """Test KeyManager with no fallback keys"""
    print("🧪 Testing KeyManager with no fallbacks...")
    
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'only-key'}, clear=True):
        from src.utils.llm import KeyManager
        
        manager = KeyManager()
        assert manager.primary_key == 'only-key'
        assert len(manager.fallback_keys) == 0
        
        # Rotation should fail
        result = manager.rotate_key()
        assert result == False
        print("  ✅ Handles no fallback keys correctly")


def test_key_manager_missing_key():
    """Test KeyManager error when no API key"""
    print("🧪 Testing KeyManager missing key error...")
    
    with patch.dict(os.environ, {}, clear=True):
        from src.utils.llm import KeyManager
        
        try:
            KeyManager()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "GEMINI_API_KEY must be set" in str(e)
            print("  ✅ Correctly raises error for missing API key")


async def test_generate_response_success():
    """Test successful response generation"""
    print("🧪 Testing generate_response success...")
    
    with patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODEL': 'gemini-1.5-flash'
    }):
        # Import after setting environment
        from src.utils.llm import generate_response
        
        # Mock the Google AI API
        with patch('src.utils.llm.genai') as mock_genai:
            # Setup mock response
            mock_response = Mock()
            mock_response.text = "Test AI response"
            
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Test the function
            result = await generate_response("Test prompt")
            
            # Verify results
            assert result == "Test AI response"
            mock_genai.configure.assert_called_once()
            mock_model.generate_content_async.assert_called_once_with("Test prompt")
            
            print("  ✅ Response generation works")


async def test_generate_response_quota_retry():
    """Test quota error handling and retry"""
    print("🧪 Testing quota error handling...")
    
    with patch.dict(os.environ, {
        'GEMINI_API_KEY': 'key1',
        'GEMINI_API_KEY_2': 'key2',
        'GEMINI_MODEL': 'gemini-1.5-flash'
    }):
        from src.utils.llm import generate_response, get_key_manager
        
        # Get the key manager instance and manually set it up for testing
        key_mgr = get_key_manager()
        
        with patch('src.utils.llm.genai') as mock_genai:
            with patch('src.utils.llm.get_key_manager', return_value=key_mgr) as mock_get_mgr:
                # Setup mock that fails first, succeeds second
                quota_error = Exception("quota exhausted")
                success_response = Mock()
                success_response.text = "Success after retry"
                
                mock_model = AsyncMock()
                mock_model.generate_content_async.side_effect = [quota_error, success_response]
                
                mock_genai.GenerativeModel.return_value = mock_model
                
                # Test
                result = await generate_response("Test prompt")
                
                # Should succeed after retry
                assert result == "Success after retry"
                assert mock_model.generate_content_async.call_count == 2
                
                print("  ✅ Quota retry works")


async def test_generate_response_empty_response():
    """Test handling of empty response"""
    print("🧪 Testing empty response handling...")
    
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
        from src.utils.llm import generate_response
        
        with patch('src.utils.llm.genai') as mock_genai:
            # Mock empty response
            mock_response = Mock()
            mock_response.text = None
            
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Should raise exception
            try:
                await generate_response("Test prompt")
                assert False, "Should have raised exception"
            except Exception as e:
                assert "Empty response" in str(e)
                print("  ✅ Empty response handled correctly")


def run_all_tests():
    """Run all tests"""
    print("🚀 Testing LLM Module")
    print("=" * 40)
    
    try:
        # Synchronous tests
        test_key_manager_basic()
        test_key_manager_no_fallbacks()
        test_key_manager_missing_key()
        
        # Asynchronous tests
        asyncio.run(test_generate_response_success())
        asyncio.run(test_generate_response_quota_retry())
        asyncio.run(test_generate_response_empty_response())
        
        print("\n🎉 All tests passed!")
        print("✅ Your LLM module is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)