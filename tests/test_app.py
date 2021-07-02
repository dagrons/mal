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
    
def test_v2_create(client):
    """
    test for uploading samples

    TODO: drop database mal first
    """

    fpath = os.path.join(os.path.dirname(__file__), 'upload', 'malware2')    
    with open(fpath, 'rb') as f:        
        r = client.post('/api/v2/task/create', 
        data=dict(file=f), 
        content_type='multipart/form-data'
        ).json['filename']
        done = False
        while not done:
            re = client.get('/api/v2/feature/report/get/{}'.format(r)).json['status']
            assert re == 'running' or re == 'reported'                                
            if re == 'reported':
                done = True

            
