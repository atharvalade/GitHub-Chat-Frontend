"""
Final Working Test for LLM Module

This test validates your llm.py code functionality.
Run with: python final_test_llm.py
"""

import os
import sys
import asyncio
from unittest.mock import patch, Mock, AsyncMock, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_key_manager_functionality():
    """Test all KeyManager functionality"""
    print("🧪 Testing KeyManager...")
    
    # Test successful initialization
    with patch.dict(os.environ, {
        'GEMINI_API_KEY': 'primary-key-123',
        'GEMINI_API_KEY_2': 'fallback-key-1', 
        'GEMINI_API_KEY_3': 'fallback-key-2',
        'GEMINI_MODEL': 'gemini-1.5-pro'
    }):
        from src.utils.llm import KeyManager
        
        manager = KeyManager()
        
        # Test initialization
        assert manager.primary_key == 'primary-key-123'
        assert len(manager.fallback_keys) == 2
        assert manager.model_name == 'gemini-1.5-pro'
        print("  ✅ Initialization successful")
        
        # Test getting current key (should start with primary)
        assert manager.get_current_key() == 'primary-key-123'
        print("  ✅ Current key retrieval works")
        
        # Test first rotation
        result = manager.rotate_key()
        assert result == True
        assert manager.get_current_key() == 'fallback-key-1'
        print("  ✅ First key rotation works")
        
        # Test second rotation  
        result = manager.rotate_key()
        assert result == True
        assert manager.get_current_key() == 'fallback-key-2'
        print("  ✅ Second key rotation works")
        
        # Test rotation when no more keys
        result = manager.rotate_key()
        assert result == False
        assert manager.get_current_key() == 'fallback-key-2'  # Should stay at last key
        print("  ✅ Handles exhausted keys correctly")
        
        # Test reset functionality
        manager.reset()
        assert manager.get_current_key() == 'primary-key-123'
        print("  ✅ Reset functionality works")

    # Test error when no primary key
    with patch.dict(os.environ, {}, clear=True):
        try:
            KeyManager()
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "GEMINI_API_KEY must be set" in str(e)
            print("  ✅ Correctly handles missing API key")

    print("✅ All KeyManager tests passed!\n")


async def test_generate_response_functionality():
    """Test generate_response functionality with mocked API"""
    print("🧪 Testing generate_response...")
    
    with patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-api-key',
        'GEMINI_MODEL': 'gemini-1.5-flash'
    }):
        from src.utils.llm import generate_response
        
        # Test successful response generation
        with patch('src.utils.llm.genai') as mock_genai:
            mock_response = Mock()
            mock_response.text = "This is a successful AI response"
            
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            
            mock_genai.GenerativeModel.return_value = mock_model
            mock_genai.configure = Mock()
            
            result = await generate_response("Test prompt")
            
            assert result == "This is a successful AI response"
            mock_genai.configure.assert_called_once_with(api_key='test-api-key')
            mock_model.generate_content_async.assert_called_once_with("Test prompt")
            print("  ✅ Successful response generation works")

        # Test empty response handling
        with patch('src.utils.llm.genai') as mock_genai:
            mock_response = Mock()
            mock_response.text = None  # Empty response
            
            mock_model = AsyncMock()
            mock_model.generate_content_async.return_value = mock_response
            
            mock_genai.GenerativeModel.return_value = mock_model
            
            try:
                await generate_response("Test prompt")
                assert False, "Should raise exception for empty response"
            except Exception as e:
                assert "Empty response" in str(e)
                print("  ✅ Empty response handling works")

        # Test non-quota error handling (should not retry)
        with patch('src.utils.llm.genai') as mock_genai:
            mock_model = AsyncMock()
            mock_model.generate_content_async.side_effect = Exception("Invalid request format")
            
            mock_genai.GenerativeModel.return_value = mock_model
            
            try:
                await generate_response("Test prompt")
                assert False, "Should raise exception"
            except Exception as e:
                assert "LLM generation failed" in str(e)
                # Should only try once (no retries for non-quota errors)
                assert mock_model.generate_content_async.call_count == 1
                print("  ✅ Non-quota error handling works")

    print("✅ All generate_response tests passed!\n")


async def test_quota_retry_logic():
    """Test quota error retry logic with manual key manager"""
    print("🧪 Testing quota retry logic...")
    
    with patch.dict(os.environ, {
        'GEMINI_API_KEY': 'primary-key',
        'GEMINI_API_KEY_2': 'fallback-key',
        'GEMINI_MODEL': 'gemini-1.5-flash'
    }):
        from src.utils.llm import KeyManager
        
        # Create a key manager manually for testing
        test_key_manager = KeyManager()
        
        # Mock the entire generate_response flow
        with patch('src.utils.llm.get_key_manager', return_value=test_key_manager):
            with patch('src.utils.llm.genai') as mock_genai:
                # Setup responses: first call fails with quota, second succeeds
                quota_error = Exception("quota exhausted")
                success_response = Mock()
                success_response.text = "Success after key rotation"
                
                mock_model = AsyncMock()
                mock_model.generate_content_async.side_effect = [quota_error, success_response]
                
                mock_genai.GenerativeModel.return_value = mock_model
                mock_genai.configure = Mock()
                
                # Import and test
                from src.utils.llm import generate_response
                result = await generate_response("Test prompt")
                
                # Verify results
                assert result == "Success after key rotation"
                assert mock_model.generate_content_async.call_count == 2
                assert test_key_manager.current_key_index == 0  # Should be rotated to fallback
                
                print("  ✅ Quota retry with key rotation works")

    print("✅ Quota retry test passed!\n")


def test_logging_and_edge_cases():
    """Test logging and edge cases"""
    print("🧪 Testing edge cases...")
    
    # Test KeyManager with no fallback keys
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'only-key'}, clear=True):
        from src.utils.llm import KeyManager
        
        manager = KeyManager()
        assert len(manager.fallback_keys) == 0
        
        # Rotation should fail immediately
        result = manager.rotate_key()
        assert result == False
        assert manager.current_key_index == -1  # Should stay at primary
        print("  ✅ Handles single key scenario")

    # Test default model name
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
        manager = KeyManager()
        assert manager.model_name == 'gemini-1.5-flash'  # Default value
        print("  ✅ Default model name works")

    print("✅ Edge case tests passed!\n")


async def run_all_tests():
    """Run all tests"""
    print("🚀 Testing Your LLM Module")
    print("=" * 50)
    
    try:
        # Test KeyManager functionality
        test_key_manager_functionality()
        
        # Test generate_response functionality  
        await test_generate_response_functionality()
        
        # Test quota retry logic
        await test_quota_retry_logic()
        
        # Test edge cases
        test_logging_and_edge_cases()
        
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your LLM module is working correctly!")
        print("\n📋 Test Summary:")
        print("  • KeyManager initialization and key rotation ✅")
        print("  • API key fallback and exhaustion handling ✅")  
        print("  • Response generation and error handling ✅")
        print("  • Quota retry logic with key rotation ✅")
        print("  • Edge cases and logging ✅")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    print(f"\n{'🎊 SUCCESS!' if success else '💥 FAILURE!'}")
    sys.exit(0 if success else 1)