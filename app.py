from flask import Flask, render_template, request, redirect, flash, url_for, session
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'mandir-secret-key'  # Use os.getenv("SECRET_KEY") in prod


# 🟢 Homepage → Show Upcoming Events
@app.route('/')
def index():
    events = []
    try:
        with open('data/events.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'date' not in row:
                    continue
                try:
                    event_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    if event_date >= datetime.now().date():
                        events.append({
                            'event_id': row['event_id'],
                            'event_name': row['name'],
                            'event_date': row['date'],
                            'event_time': row['time'],
                            'description': row['desc'],
                            'location': row['location']
                        })
                except ValueError:
                    continue
    except FileNotFoundError:
        events = []

    return render_template('index.html', events=events)


# 🔐 Admin Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin_user = os.getenv("ADMIN_USER")
        admin_pass = os.getenv("ADMIN_PASS")

        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True
            flash("✅ Login successful!")
            return redirect('/dashboard')
        else:
            flash("❌ Invalid credentials.")
            return redirect('/login')

    return render_template('login.html')



'''
# 🔐 Admin Logout
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("👋 Logged out successfully.")
    return redirect('/login')
'''




# 🔐 Admin Dashboard (List All Events)
@app.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        flash("⚠️ Please login to access dashboard.")
        return redirect('/login')

    events = []
    try:
        with open('data/events.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                events.append(row)
    except FileNotFoundError:
        events = []

    return render_template('dashboard.html', events=events)


# 🟠 Admin Adds New Event (Protected)
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():


    if request.method == 'POST':
        event_name = request.form['event_name']
        event_type = request.form.get('event_type', 'General')
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        description = request.form['description']
        location = request.form['location']
        city = request.form.get('city', 'Unknown')
        image = "noimage.jpg"  # Placeholder, optional
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        event_id = datetime.now().strftime('%Y%m%d%H%M%S')

        # Ensure data folder exists
        if not os.path.exists('data'):
            os.makedirs('data')

        file_path = 'data/events.csv'
        file_exists = os.path.isfile(file_path)

        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([
                    'event_id', 'name', 'type', 'date', 'time',
                    'location', 'city', 'desc', 'image', 'created_at'
                ])
            writer.writerow([
                event_id, event_name, event_type, event_date, event_time,
                location, city, description, image, created_at
            ])

        flash('✅ Event added successfully!')
        return redirect(url_for('add_event'))

    return render_template('add_event.html')


# 🟢 RSVP Form + Save to CSV
@app.route('/rsvp', methods=['GET', 'POST'])
def rsvp():
    event_id = request.args.get('event_id')
    selected_event = None

    with open('data/events.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['event_id'] == event_id:
                selected_event = row
                break

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        city = request.form['city']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        rsvp_file = 'data/rsvp.csv'
        file_exists = os.path.isfile(rsvp_file)

        with open(rsvp_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['event_id', 'event_name', 'name', 'email', 'city', 'timestamp'])
            writer.writerow([event_id, selected_event['name'], name, email, city, timestamp])

        flash("✅ RSVP successful! Thank you.")
        return redirect(url_for('index'))

    return render_template('rsvp.html', event_id=event_id, event_name=selected_event['name'])



@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("✅ Logged out successfully.")
    return redirect('/')


# ✅ Start Flask Server
if __name__ == '__main__':
    app.run(debug=True)