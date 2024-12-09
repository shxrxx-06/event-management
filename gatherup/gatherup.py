from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_from_directory

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
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
@app.route('/event_form')
def event_form():
    return render_template('event_form.html')

@app.route('/fevent_forms')
def fevent_forms():
    return render_template('fevent_forms.html')

@app.route('/event_approval')
def event_approval():
    return render_template('event_approval.html')

@app.route('/approve_event')
def approve_event(event_id):
    return redirect(url_for('event_approval'))

@app.route('/reject_event')
def reject_event(event_id):
    return redirect(url_for('event_approval'))

@app.route('/venue_history')
def venue_history():
     return render_template('venue_history.html')
 
@app.route('/venue_details')
def venue_details():
    return render_template('venue_details.html')

@app.route('/venue')
def index():
    return redirect(url_for('venue_approval'))

@app.route('/venue_approval')
def venue_approval():
    return render_template('avenue_booking.html')

@app.route('/static')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
