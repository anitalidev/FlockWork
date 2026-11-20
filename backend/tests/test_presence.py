import os
import tempfile
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(tempfile.mkdtemp(), 'presence.db')
from fastapi.testclient import TestClient
from app import auth
from app.main import app

EMAIL = {'value': 'presence@student.ubc.ca'}
app.dependency_overrides[auth.current_email] = lambda: EMAIL['value']
client = TestClient(app)

def profile():
    app.dependency_overrides[auth.current_email] = lambda: EMAIL['value']
    assert client.post('/users', json={'name': 'Presence test'}).status_code == 200

def test_presence_persists_until_explicit_delete_and_rejects_out_of_range():
    profile()
    assert client.get('/presence/me').json() == {'sharing': False, 'lat': None, 'lng': None}
    r = client.post('/presence', json={'lat': 49.2628, 'lng': -123.2505})
    assert r.status_code == 200
    assert client.get('/presence/me').json()['sharing'] is True
    assert len(client.get('/presence/heatmap').json()['areas']) == 1
    assert client.get('/presence/heatmap').json()['active_students'] == 1
    assert client.post('/presence', json={'lat': 91, 'lng': 0}).status_code == 400
    assert client.delete('/presence').json()['sharing'] is False
    assert client.get('/presence/me').json()['sharing'] is False


def test_stale_presence_expires_after_ttl():
    from datetime import datetime, timedelta
    from app import models
    from app.database import SessionLocal
    from app.main import PRESENCE_TTL_SECONDS
    EMAIL['value'] = 'stale@student.ubc.ca'
    profile()
    assert client.post('/presence', json={'lat': 49.26, 'lng': -123.25}).status_code == 200
    db = SessionLocal()
    try:
        user = db.query(models.User).filter_by(email='stale@student.ubc.ca').one()
        row = db.get(models.Presence, user.id)
        row.updated_at = datetime.utcnow() - timedelta(seconds=PRESENCE_TTL_SECONDS + 5)
        db.commit()
    finally:
        db.close()
    assert client.get('/presence/me').json()['sharing'] is False
    assert client.get('/presence/heatmap').json()['active_students'] == 0
    EMAIL['value'] = 'presence@student.ubc.ca'


def test_database_health_check():
    r = client.get('/health/db')
    assert r.status_code == 200
    assert r.json()['database'] == 'ok'
