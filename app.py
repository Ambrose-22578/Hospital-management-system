from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database if not exists
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            doctor_id INTEGER,
            date TEXT NOT NULL,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            reason TEXT NOT NULL,
            visit_date TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            service_charge REAL NOT NULL,
            medicine_charge REAL NOT NULL,
            room_charge REAL NOT NULL,
            tax REAL NOT NULL,
            total_cost REAL NOT NULL,
            billing_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# View patient visits
@app.route('/visit', methods=['GET', 'POST'])
def visit():
    conn = get_db_connection()
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        reason = request.form['reason']
        visit_date = request.form['visit_date']

        conn.execute('INSERT INTO visits (patient_name, reason, visit_date) VALUES (?, ?, ?)',
                     (patient_name, reason, visit_date))
        conn.commit()
        flash('Visit added successfully!', 'success')
    
    visits = conn.execute('SELECT * FROM visits').fetchall()
    conn.close()
    return render_template('visit.html', visits=visits)

@app.route('/delete_visit/<int:id>')
def delete_visit(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM visits WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Visit deleted successfully!', 'danger')
    return redirect(url_for('visit'))

# Book appointments
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    conn = get_db_connection()
    doctors = conn.execute('SELECT id, name FROM doctors').fetchall()

    if request.method == 'POST':
        patient_name = request.form['patient_name']
        doctor_id = request.form['doctor']
        date = request.form['date']

        conn.execute('INSERT INTO appointments (patient_name, doctor_id, date) VALUES (?, ?, ?)',
                     (patient_name, doctor_id, date))
        conn.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointment'))

    conn.close()
    return render_template('appointment.html', doctors=doctors)

# Register and manage doctors
@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        specialty = request.form['specialty']

        conn.execute('INSERT INTO doctors (name, specialty) VALUES (?, ?)', (name, specialty))
        conn.commit()
        flash('Doctor added successfully!', 'success')
    
    doctors = conn.execute('SELECT * FROM doctors').fetchall()
    conn.close()
    return render_template('register.html', doctors=doctors)

@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM doctors WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Doctor deleted successfully!', 'danger')
    return redirect(url_for('register'))

# Billing route
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    conn = get_db_connection()
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        service_charge = float(request.form['service_charge'])
        medicine_charge = float(request.form['medicine_charge'])
        room_charge = float(request.form['room_charge'])
        tax = float(request.form['tax'])
        
        subtotal = service_charge + medicine_charge + room_charge
        total_cost = subtotal + (subtotal * tax / 100)
        billing_date = datetime.now().strftime("%Y-%m-%d")

        conn.execute('''
            INSERT INTO bills (patient_name, service_charge, medicine_charge, room_charge, tax, total_cost, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_name, service_charge, medicine_charge, room_charge, tax, total_cost, billing_date))
        
        conn.commit()
        flash('Billing record created successfully!', 'success')
    
    bills = conn.execute('SELECT * FROM bills').fetchall()
    conn.close()
    return render_template('billing.html', bills=bills)

if __name__ == '__main__':
    init_db()  # Initialize the database on start
    app.run(debug=True)
