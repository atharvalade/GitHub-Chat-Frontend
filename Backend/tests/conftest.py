"""
Test fixtures and utilities shared across all tests
"""

import pytest
import os
from unittest.mock import patch, Mock
import tempfile
import asyncio


@pytest.fixture
def clean_environment():
    """Provide a clean environment without any Gemini API keys"""
    original_env = os.environ.copy()
    
    # Remove all GEMINI_* environment variables
    for key in list(os.environ.keys()):
        if key.startswith('GEMINI_'):
            del os.environ[key]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def test_environment():
    """Provide a test environment with predefined API keys"""
    test_env = {
        'GEMINI_API_KEY': 'test-primary-key-123',
        'GEMINI_API_KEY_2': 'test-fallback-key-456',
        'GEMINI_API_KEY_3': 'test-fallback-key-789',
        'GEMINI_MODEL': 'gemini-1.5-flash-test'
    }
    
    with patch.dict(os.environ, test_env):
        yield test_env


@pytest.fixture
def mock_gemini_api():
    """Mock the Google Generative AI API"""
    with patch('utils.llm.genai') as mock_genai:
        # Create mock response
        mock_response = Mock()
        mock_response.text = "Mock AI response for testing"
        
        # Create mock model
        mock_model = Mock()
        mock_model.generate_content_async = Mock(return_value=mock_response)
        
        # Configure the mock
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = Mock()
        
        yield {
            'genai': mock_genai,
            'model': mock_model,
            'response': mock_response
        }


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing logging functionality"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    yield log_file_path
    
    # Cleanup
    try:
        os.unlink(log_file_path)
    except FileNotFoundError:
        pass


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class MockWebSocket:
    """Mock WebSocket for testing connection manager"""
    
    def __init__(self):
        self.messages_sent = []
        self.is_closed = False
        self.accept_called = False
    
    async def accept(self):
        """Mock WebSocket accept"""
        self.accept_called = True
    
    async def send_text(self, message: str):
        """Mock sending text message"""
        self.messages_sent.append(message)
    
    async def close(self):
        """Mock WebSocket close"""
        self.is_closed = True
    
    async def receive_text(self):
        """Mock receiving text message"""
        return "mock incoming message"


@pytest.fixture
def mock_websocket():
    """Provide a mock WebSocket for testing"""
    return MockWebSocket()


# Helper functions for tests

def assert_log_contains(caplog, level, message):
    """Assert that logs contain a specific message at a specific level"""
    for record in caplog.records:
        if record.levelname == level and message in record.message:
            return True
    raise AssertionError(f"Expected log message '{message}' at level '{level}' not found")


def create_mock_quota_error(message="Quota exceeded"):
    """Create a mock quota/rate limit error"""
    error = Exception(message)
    return error


def create_mock_api_error(message="API Error"):
    """Create a mock generic API error"""
    error = Exception(message)
    return error