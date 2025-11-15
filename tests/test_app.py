import pytest
from datetime import datetime
from app import app, db, Room, User, Booking

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add a room and a user
            db.session.add(Room(name="Room 1", capacity=10, location="1st Floor", amenities="Projector"))
            db.session.add(User(name="Jane Doe", email="jane@example.com", department="HR"))
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_bookings_page(client):
    """Check that /bookings page loads."""
    response = client.get('/bookings')
    assert response.status_code == 200

def test_add_booking(client):
    """Check that we can add a booking."""
    with app.app_context():
        room_id = Room.query.first().id
        user_id = User.query.first().id

    booking_data = {
        'room_id': room_id,
        'user_id': user_id,
        'meeting_title': 'Team Sync',
        'meeting_date': datetime.now().strftime('%Y-%m-%d'),
        'start_time': '10:00',
        'end_time': '11:00',
        'attendees': '5',
        'notes': 'Weekly meeting'
    }

    response = client.post('/bookings/add', data=booking_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Booking created successfully!' in response.data
