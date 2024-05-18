from flaskapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def __repr__(self):
        return '<User %r>' % self.username
    

class Car(db.Model):
    id = db.Column("carId", db.Integer, primary_key=True)
    model = db.Column(db.String(80), nullable=False)
    registration_number = db.Column(db.String(120), unique=True, nullable=False)
    availability = db.Column(db.Boolean, nullable=False, default=True)
    brand = db.Column(db.String(50), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    thumbnail = db.Column(db.String(255), nullable=True)
    reservations = db.relationship('Reservation', backref='car', lazy=True)
    
    def __repr__(self):
        return '<Car %r>' % self.model


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.carId'), nullable=False)
    reservation_date = db.Column(db.DateTime, nullable=False)
    pick_up_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Confirmed')
    total_price = db.Column(db.Float, nullable=False)


    def __repr__(self):
        return '<Reservation %r>' % self.id