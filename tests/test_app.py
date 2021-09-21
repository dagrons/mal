import pytest
import os

from app import make_app

@pytest.fixture
def client():
    """
    yield a client for test    
    """
    app = make_app('test')

    with app.test_client() as client:
        yield client
    
            
