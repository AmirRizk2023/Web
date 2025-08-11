from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/company.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs('instance', exist_ok=True)
db = SQLAlchemy(app)

# Models
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200))
    unit = db.Column(db.String(120))
    devices = db.relationship('Device', backref='employee', lazy=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(200))
    serial = db.Column(db.String(200))
    status = db.Column(db.String(50), default='attached')  # attached / detached / stock
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)

class Call(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(200))
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # active, pending, solved, canceled
    priority = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    solved_at = db.Column(db.DateTime, nullable=True)

# Routes
@app.route('/')
def index():
    return redirect(url_for('inventory'))

@app.route('/inventory')
def inventory():
    units = {}
    employees = Employee.query.order_by(Employee.unit, Employee.name).all()
    for e in employees:
        units.setdefault(e.unit or 'General', []).append(e)
    return render_template('inventory.html', units=units)

@app.route('/employee/<int:emp_id>')
def employee_page(emp_id):
    e = Employee.query.get_or_404(emp_id)
    return render_template('employee.html', employee=e)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    email = request.form.get('email')
    unit = request.form.get('unit')
    emp = Employee(name=name, email=email, unit=unit)
    db.session.add(emp)
    db.session.commit()
    return redirect(url_for('inventory'))

@app.route('/add_device', methods=['POST'])
def add_device():
    model = request.form['model']
    serial = request.form.get('serial')
    emp_id = request.form.get('employee_id')
    dev = Device(model=model, serial=serial)
    if emp_id:
        dev.employee_id = int(emp_id)
    db.session.add(dev)
    db.session.commit()
    return redirect(url_for('inventory'))

@app.route('/attach_device', methods=['POST'])
def attach_device():
    dev_id = int(request.form['device_id'])
    emp_id = int(request.form['employee_id'])
    dev = Device.query.get_or_404(dev_id)
    dev.employee_id = emp_id
    dev.status = 'attached'
    db.session.commit()
    return redirect(url_for('employee_page', emp_id=emp_id))

@app.route('/detach_device', methods=['POST'])
def detach_device():
    dev_id = int(request.form['device_id'])
    dev = Device.query.get_or_404(dev_id)
    dev.employee_id = None
    dev.status = 'stock'
    db.session.commit()
    return redirect(url_for('inventory'))

# Calls (tickets)
@app.route('/calls')
def calls_page():
    # active first, then pending by created_at
    calls = Call.query.order_by(Call.status.desc(), Call.priority.desc(), Call.created_at).all()
    return render_template('calls.html', calls=calls)

@app.route('/submit_call', methods=['GET','POST'])
def submit_call():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # priority: whoever first gets active; we'll compute priority as inverse timestamp
        c = Call(name=name, email=email, message=message, status='active')
        # set other active -> pending
        active = Call.query.filter_by(status='active').all()
        for a in active:
            a.status = 'pending'
        db.session.add(c)
        db.session.commit()
        return render_template('public_submit.html', success=True)
    return render_template('public_submit.html')

@app.route('/calls/action', methods=['POST'])
def calls_action():
    action = request.form['action']
    call_id = int(request.form['call_id'])
    c = Call.query.get_or_404(call_id)
    if action == 'solve':
        c.status = 'solved'
        c.solved_at = datetime.utcnow()
    elif action == 'cancel':
        c.status = 'canceled'
    elif action == 'activate':
        # set current active -> pending
        for a in Call.query.filter_by(status='active').all():
            a.status = 'pending'
        c.status = 'active'
    db.session.commit()
    return redirect(url_for('calls_page'))

if __name__ == '__main__':
    app.run(debug=True)