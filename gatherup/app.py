from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ranusharamesh232'
app.config['DATABASE'] = 'university_app.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif','pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            flash('Logged in successfully')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_type = session['user_type']
    
    if user_type == 'faculty':
        return render_template('fdashboard.html')
    elif user_type == 'student':
        return render_template('sdashboard.html')
    elif user_type == 'admin':
        return render_template('dashboard.html')
    else:
        flash('Invalid user type')
        return redirect(url_for('logout'))

@app.route('/event_form', methods=['GET', 'POST'])
def event_form():
    if 'user_id' not in session or session['user_type'] != 'faculty':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        event_description = request.form['event_description']
        faculty_coordinator = request.form['faculty_coordinator']
        
        poster = request.files['poster']
        if poster and allowed_file(poster.filename):
            filename = secure_filename(poster.filename)
            poster.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None
        
        db = get_db()
        db.execute('INSERT INTO event_form (user_id, event_name, event_date, event_time, event_description, faculty_coordinator, poster_filename, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (session['user_id'], event_name, event_date, event_time, event_description, faculty_coordinator, filename, 'pending'))
        db.commit()
        flash('Event form submitted successfully')
        return redirect(url_for('fevent_forms'))
    
    return render_template('event_form.html')

@app.route('/fevent_forms')
def fevent_forms():
    if 'user_id' not in session or session['user_type'] != 'faculty':
        return redirect(url_for('login'))
    
    db = get_db()
    events = db.execute('SELECT * FROM event_form WHERE user_id = ? ORDER BY submitted_date DESC', (session['user_id'],)).fetchall()
    return render_template('fevent_forms.html', events=events)

@app.route('/event_approval')
def event_approval():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    pending_events = db.execute('SELECT ef.*, u.name as faculty_name FROM event_form ef JOIN users u ON ef.user_id = u.id WHERE ef.status = "pending" ORDER BY ef.submitted_date DESC').fetchall()
    return render_template('event_approval.html', pending_events=pending_events)

@app.route('/approve_event/<int:event_id>', methods=['POST'])
def approve_event(event_id):
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    db.execute('UPDATE event_form SET status = "approved" WHERE id = ?', (event_id,))
    db.commit()
    flash('Event approved successfully')
    return redirect(url_for('event_approval'))

@app.route('/reject_event/<int:event_id>', methods=['POST'])
def reject_event(event_id):
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    db.execute('UPDATE event_form SET status = "rejected" WHERE id = ?', (event_id,))
    db.commit()
    flash('Event rejected successfully')
    return redirect(url_for('event_approval'))
@app.route('/venue_history')
def venue_history():
    # Get parameters from the request
    event_name = request.args.get('eventName')
    event_date = request.args.get('eventDate')
    venue = request.args.get('venue')
    timing = request.args.get('timing')
    duration = request.args.get('duration')
    
    # Pass these parameters to the template
    return render_template('venue_history.html', 
                           event_name=event_name, 
                           event_date=event_date, 
                           venue=venue, 
                           timing=timing, 
                           duration=duration)
@app.route('/venue_details')
def venue_details():
    # Get parameters from the request
    event_name = request.args.get('eventName')
    event_date = request.args.get('eventDate')
    venue = request.args.get('venue')
    timing = request.args.get('timing')
    duration = request.args.get('duration')
    
    # Pass these parameters to the template
    return render_template('venue_details.html', 
                           event_name=event_name, 
                           event_date=event_date, 
                           venue=venue, 
                           timing=timing, 
                           duration=duration)
@app.route('/venue')
def index():
    return redirect(url_for('venue_approval'))

@app.route('/venue_approval')
def venue_approval():
    return render_template('avenue_booking.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)