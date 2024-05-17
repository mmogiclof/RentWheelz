from flask import flash, render_template, request, session, redirect, url_for
from flaskapp import app, db
from flaskapp.models import User, Car, Reservation
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime


@app.route("/")
def index():
    return render_template('index.html', user=session.get('username'))

@app.route("/api/v1/users")
def users():
    users = User.query.order_by(User.id).all()
    return [{'id': user.id, 'username': user.username, 'email': user.email, 'pwd':user.password} for user in users]

@app.route("/api/v1/users/<int:user_id>/bookings", methods=['GET'])
def get_user_bookings(user_id):
    user = User.query.get(user_id)
    return [{'reservation_id': reservation.id, 
        'car': {
        'model': reservation.car.model, 
        'registration_number': reservation.car.registration_number, 
        'brand': reservation.car.brand, 
        'price_per_hour': reservation.car.price_per_hour, 
        }, 
        'status': reservation.status,
        'passengers': reservation.passengers, 
        'reservation_date': reservation.reservation_date, 
        'pick_up_date': reservation.pick_up_date,
        'return_date': reservation.return_date} for reservation in user.reservations]

@app.route("/api/v1/users/<int:user_id>")
def get_user(user_id):
    user = User.query.get(user_id)
    return {'id': user.id, 'username': user.username, 'email': user.email}

@app.route("/api/v1/users/<int:user_id>", methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}
    else:
        return {'error': 'User not found'}, 404

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_email:
            return render_template('register.html', error="User already exists")
        if existing_user:
            return render_template('register.html', error="Username already exists")
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('index'))

    elif request.method == 'GET' and current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('register.html')



@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        data = request.form
        print(data)
        email = data.get('email')
        password = data.get('password')
        rememberUser = True if data.get('rememberMe') else False
        # Check if email exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if password matches
            if user.password == password:
                login_user(user, remember=rememberUser)
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Incorrect password")
        else:
            return render_template('login.html', error="Invalid email address")
    elif request.method == 'GET' and current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/cars")
def get_cars():
    if not current_user.is_authenticated:
        return redirect(url_for('login_page'))
    cars = Car.query.all()
    return render_template('cars.html', cars=cars)

@app.route("/bookings", methods=['GET', 'POST'])
def bookings():
    if not current_user.is_authenticated:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        data = request.form
        user_email = current_user.email
        car_id = data.get('car_id')
        pick_up_date = data.get('pick-up-date')
        return_date = data.get('return-date')
        reservation_time = datetime.now()
        start_time = datetime.strptime(pick_up_date, '%Y-%m-%d').date()
        end_time = datetime.strptime(return_date, '%Y-%m-%d').date()
        passengers = data.get('passengers')
        car = Car.query.get(car_id)
        total_price = (end_time - start_time).total_seconds() / 3600 * car.price_per_hour

        new_reservation = Reservation(
            user_email=user_email, 
            car_id=car_id, 
            reservation_date=reservation_time, 
            pick_up_date=start_time, 
            return_date=end_time,
            passengers=passengers,
            total_price=total_price
        )
        db.session.add(new_reservation)
        db.session.commit()
    
    current_time = datetime.now().date()  
    reservations = Reservation.query.filter_by(user_email=current_user.email).order_by(Reservation.reservation_date.desc()).all()
    for reservation in reservations:
        if reservation.return_date.date() < current_time:
            reservation.status = 'Completed'
    db.session.commit()

    status_args = request.args.get('status')
    if status_args:
        reservations = Reservation.query.filter_by(user_email=current_user.email, status=status_args).order_by(Reservation.reservation_date.desc()).all()
    return render_template('bookings.html', bookings=reservations)


@app.route("/api/v1/cars")
def get_cars_api():
    cars = Car.query.all()
    return [{'id': car.id, 'model': car.model, 'registration_number': car.registration_number, 'availability': car.availability, 'brand': car.brand, 'price_per_hour': car.price_per_hour, 'thumbnail': car.thumbnail} for car in cars]

@app.route("/api/v1/cars/<int:car_id>")
def get_car(car_id):
    car = Car.query.get(car_id)
    return {'id': car.id, 'model': car.model, 'registration_number': car.registration_number, 'availability': car.availability, 'brand': car.brand, 'price_per_hour': car.price_per_hour, 'thumbnail': car.thumbnail}

@app.post("/api/v1/cars/create")
def create_car():
    data = request.get_json()
    model = data.get('model')
    registration_number = data.get('registration_number')
    availability = data.get('availability')
    brand = data.get('brand')
    price_per_hour = data.get('price_per_hour')
    thumbnail = data.get('thumbnail')
    
    new_car = Car(model=model, registration_number=registration_number, availability=availability, brand=brand, price_per_hour=price_per_hour, thumbnail=thumbnail)
    db.session.add(new_car)
    db.session.commit()
    return {'message': 'Car created successfully'}, 201

@app.route("/api/v1/cars/<int:car_id>", methods=['DELETE'])
def delete_car(car_id):
    car = Car.query.get(car_id)
    if car:
        db.session.delete(car)
        db.session.commit()
        return {'message': 'Car deleted successfully'}
    else:
        return {'error': 'Car not found'}, 404

@app.route("/api/v1/reservations")
def get_reservations():
    reservations = Reservation.query.all()
    return [{
        'id': reservation.id, 
        'user': reservation.user.username, 
        'car': {
        'model': reservation.car.model, 
        'registration_number': reservation.car.registration_number, 
        'brand': reservation.car.brand, 
        'price_per_hour': reservation.car.price_per_hour, 
        }, 
    'status': reservation.status,
    'total_price': reservation.total_price,
    'passengers': reservation.passengers,
    'reservation_date':reservation.reservation_date,
    'pick_up_date': reservation.pick_up_date, 
    'return_date': reservation.return_date} for reservation in reservations]

@app.route("/api/v1/reservations/<int:reservation_id>")
def get_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    return {
        'id': reservation.id, 
        'user': reservation.user.username, 
        'car': {
        'model': reservation.car.model, 
        'registration_number': reservation.car.registration_number, 
        'brand': reservation.car.brand, 
        'price_per_hour': reservation.car.price_per_hour, 
        }, 
    'status': reservation.status,
    'total_price': reservation.total_price,
    'passengers': reservation.passengers,
    'reservation_date':reservation.reservation_date,
    'pick_up_date': reservation.pick_up_date, 
    'return_date': reservation.return_date}

@app.post("/api/v1/reservations/create")
def create_reservation():
    data = request.get_json()
    user_email = data.get('user_email')
    car_id = data.get('car_id')
    passengers = data.get('passengers')
    reservation_time = datetime.strptime(data.get('reservation_date'), '%Y-%m-%d').date()
    start_time = datetime.strptime(data.get('pick_up_date'), '%Y-%m-%d').date()
    end_time = datetime.strptime(data.get('return_date'), '%Y-%m-%d').date()
    status = data.get('status')
    car = Car.query.get(car_id)
    total_price = (end_time - start_time).total_seconds() / 3600 * car.price_per_hour

    new_reservation = Reservation(
        user_email=user_email, 
        car_id=car_id,
        passengers=passengers, 
        reservation_date=reservation_time, 
        pick_up_date=start_time, 
        return_date=end_time,
        status=status,
        total_price=total_price
    )
    db.session.add(new_reservation)
    db.session.commit()
    return {'message': 'Reservation created successfully'}, 201

@app.route("/api/v1/reservations/<int:reservation_id>", methods=['DELETE'])
def delete_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        return {'message': 'Reservation deleted successfully'}
    else:
        return {'error': 'Reservation not found'}, 404

@app.route('/cancel_booking/<int:booking_id>', methods=['GET'])
@login_required
def cancel_booking(booking_id):
    booking = Reservation.query.get_or_404(booking_id)
    print(booking)
    booking.status = 'Cancelled'
    db.session.commit()
    flash(f"Booking {booking_id} has been cancelled", 'success')
    return redirect(url_for('bookings'))

@app.route("/about")    
def about():
    return render_template('about.html')


