# tests/test_app.py

# def test_example():
#   assert 2 + 2 == 4
    
# tests/test_app.py
from app import db, app, Room

def test_basic_math():
    """Dummy test that always passes."""
    assert 1 + 1 == 2


def test_create_dummy_room():
    """Test creating a dummy room in an in-memory DB."""
    # Set up in-memory database
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        # Create a dummy room
        room = Room(
            name="Test Room",
            capacity=20,
            location="Test Floor",
            amenities="Projector"
        )

        db.session.add(room)
        db.session.commit()

        # Fetch it again
        saved_room = Room.query.first()

        assert saved_room is not None
        assert saved_room.name == "Test Room"
        assert saved_room.capacity == 20
