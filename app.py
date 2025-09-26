from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    amenities = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='room', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meeting_title = db.Column(db.String(200), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    attendees = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    recent_bookings = Booking.query.filter(
        Booking.meeting_date >= date.today()
    ).order_by(Booking.meeting_date, Booking.start_time).limit(5).all()
    
    total_rooms = Room.query.count()
    total_users = User.query.count()
    total_bookings = Booking.query.filter(Booking.meeting_date >= date.today()).count()
    
    return render_template('index.html', 
                         recent_bookings=recent_bookings,
                         total_rooms=total_rooms,
                         total_users=total_users,
                         total_bookings=total_bookings)

@app.route('/rooms')
def rooms():
    rooms = Room.query.all()
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room = Room(
            name=request.form['name'],
            capacity=int(request.form['capacity']),
            location=request.form['location'],
            amenities=request.form['amenities']
        )
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('rooms'))
    return render_template('add_room.html')

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            department=request.form['department']
        )
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('users'))
    return render_template('add_user.html')

@app.route('/bookings')
def bookings():
    bookings = Booking.query.order_by(Booking.meeting_date.desc()).all()
    return render_template('bookings.html', bookings=bookings)

@app.route('/bookings/add', methods=['GET', 'POST'])
def add_booking():
    if request.method == 'POST':
        booking = Booking(
            room_id=int(request.form['room_id']),
            user_id=int(request.form['user_id']),
            meeting_title=request.form['meeting_title'],
            meeting_date=datetime.strptime(request.form['meeting_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(request.form['end_time'], '%H:%M').time(),
            attendees=int(request.form['attendees']),
            notes=request.form['notes']
        )
        db.session.add(booking)
        db.session.commit()
        flash('Booking created successfully!', 'success')
        return redirect(url_for('bookings'))
    
    rooms = Room.query.all()
    users = User.query.all()
    return render_template('add_booking.html', rooms=rooms, users=users)

@app.route('/api/rooms/<int:room_id>/availability')
def check_availability(room_id):
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date parameter required'}), 400
    
    try:
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    bookings = Booking.query.filter_by(room_id=room_id, meeting_date=check_date).all()
    booked_slots = []
    for booking in bookings:
        booked_slots.append({
            'start': booking.start_time.strftime('%H:%M'),
            'end': booking.end_time.strftime('%H:%M'),
            'title': booking.meeting_title
        })
    
    return jsonify({'booked_slots': booked_slots})

@app.route('/bookings/delete/<int:booking_id>')
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('bookings'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample data if tables are empty
        if Room.query.count() == 0:
            sample_rooms = [
                Room(name='Conference Room A', capacity=10, location='Floor 1', amenities='Projector, Whiteboard, WiFi'),
                Room(name='Meeting Room B', capacity=6, location='Floor 2', amenities='TV Screen, WiFi'),
                Room(name='Board Room', capacity=15, location='Floor 3', amenities='Video Conference, Projector, Whiteboard')
            ]
            for room in sample_rooms:
                db.session.add(room)
        
        if User.query.count() == 0:
            sample_users = [
                User(name='John Doe', email='john@company.com', department='IT'),
                User(name='Jane Smith', email='jane@company.com', department='HR'),
                User(name='Mike Johnson', email='mike@company.com', department='Finance')
            ]
            for user in sample_users:
                db.session.add(user)
        
        db.session.commit()
    
    app.run(debug=True)
