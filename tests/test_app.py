# tests/test_app.py

# def test_example():
#   assert 2 + 2 == 4
    
import pytest
from datetime import datetime
from app import app, db, Booking, Room, User

@pytest.fixture
def client():
    # this one configures test client and in-memory database
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()

        # Create dummy Room and User for testing
        room = Room(name="Conference Room A",capacity=10,location="1st Floor",amenities="Projector, Whiteboard")
        capacity=10,
        location="1st Floor",
        amenities="Projector, Whiteboard"
        user = User(name="Jane", email="jane@example.com")

        db.session.add_all([room, user])
        db.session.commit()

    yield client

    # Teardown
    with app.app_context():
        db.drop_all()


def test_get_bookings_page(client):
    """Make sure that the /bookings page loads successfully."""
    response = client.get('/bookings')
    assert response.status_code == 200

    assert b'bookings' in response.data.lower()                                      # checks template content


def test_add_booking_post(client):
    """Test that a new booking can be added successfully."""
    with app.app_context():
        room = Room.query.first()
        user = User.query.first()

    booking_data = {
        'room_id': room.id,
        'user_id': user.id,
        'meeting_title': 'Team Sync',
        'meeting_date': datetime.now().strftime('%Y-%m-%d'),
        'start_time': '10:00',
        'end_time': '11:00',
        'attendees': '5',
        'notes': 'Weekly sync-up'
    }

    response = client.post('/bookings/add', data=booking_data, follow_redirects=True)

    # Check redirect and flash message
    assert response.status_code == 200
    assert b'Booking created successfully!' in response.data

    # Verify booking exists in the database
    with app.app_context():
        booking = Booking.query.filter_by(meeting_title='Team Sync').first()
        assert booking is not None
        assert booking.attendees == 5

