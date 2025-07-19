"""Tests for secure error handling patterns to prevent information exposure."""

import json
import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Add the project root to Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_ai_router_error_handling():
    """Test that ai_router doesn't expose exception details to clients."""
    # Mock the routing_logic module before importing ai_router.main
    mock_routing_logic = Mock()
    sys.modules['routing_logic'] = mock_routing_logic
    
    from ai_router.main import app
    
    with app.test_client() as client:
        # Mock route_query to raise an exception
        mock_routing_logic.route_query.side_effect = Exception("Sensitive database connection error")
        
        response = client.post('/route', 
                             json={'query': 'test query'},
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        
        # Should return generic error, not expose exception details
        assert data['error'] == 'Internal server error'
        assert 'Sensitive database connection error' not in data['error']
        assert 'database' not in data['error'].lower()


def test_flask_app_version_endpoint_error_handling():
    """Test that app.py version endpoint doesn't expose git command errors."""
    from app import app
    
    with app.test_client() as client:
        with patch('subprocess.check_output') as mock_subprocess:
            mock_subprocess.side_effect = Exception("git: fatal: not a git repository")
            
            response = client.get('/sterling/version')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Should return 'unknown' instead of error details
            assert data['commit_hash'] == 'unknown'
            assert 'fatal' not in data['commit_hash']
            assert 'git repository' not in data['commit_hash']


def test_flask_app_webhook_rebuild_error_handling():
    """Test that webhook rebuild endpoint doesn't expose subprocess errors."""
    from app import app
    
    with app.test_client() as client:
        with patch('subprocess.call') as mock_subprocess:
            mock_subprocess.side_effect = Exception("Permission denied: /usr/bin/git")
            
            response = client.post('/webhook/rebuild')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            
            # Should return generic error message
            assert data['status'] == 'error'
            assert data['detail'] == 'Rebuild operation failed'
            assert 'Permission denied' not in data['detail']
            assert '/usr/bin/git' not in data['detail']


def test_memory_engine_error_handling():
    """Test that memory engine doesn't expose filesystem errors."""
    from addons.sterling_os.memory_engine import adaptive_memory_match
    
    with patch('builtins.open') as mock_open:
        mock_open.side_effect = FileNotFoundError("/secret/path/memory.json: No such file")
        
        result = adaptive_memory_match("test query", "test_context")
        
        # Should return generic error message
        assert len(result) == 1
        assert result[0]['error'] == 'Memory access temporarily unavailable'
        assert 'secret/path' not in str(result)
        assert 'No such file' not in str(result)


def test_logging_is_called_for_errors():
    """Test that errors are properly logged server-side."""
    # Mock the routing_logic module before importing ai_router.main
    mock_routing_logic = Mock()
    sys.modules['routing_logic'] = mock_routing_logic
    
    from ai_router.main import app
    
    with app.test_client() as client:
        with patch('logging.exception') as mock_logging:
            mock_routing_logic.route_query.side_effect = Exception("Test exception")
            
            response = client.post('/route', 
                                 json={'query': 'test query'},
                                 content_type='application/json')
            
            # Verify that logging.exception was called
            mock_logging.assert_called_once_with("Routing error occurred")


if __name__ == '__main__':
    pytest.main([__file__])