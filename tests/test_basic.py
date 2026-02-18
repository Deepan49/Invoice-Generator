def test_app_exists(app):
    assert app is not None

def test_app_is_testing(app):
    assert app.config['TESTING']

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Invoice Generator" in response.data

def test_api_dashboard_unauthorized(client):
    response = client.get('/api/dashboard/')
    assert response.status_code == 401
