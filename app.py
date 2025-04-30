from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
import json
import os

app = Flask(__name__)

# --- Flask-Mail Configuration ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'Sonikatk15@gmail.com'  # Your Gmail
app.config['MAIL_PASSWORD'] = 'kszwqupcwbvdbbvs'      # Your App Password
app.config['MAIL_DEFAULT_SENDER'] = 'Sonikatk15@gmail.com'

mail = Mail(app)

# --- File to Store Reports ---
REPORT_FILE = 'reports.json'

# --- Utility: Load Reports ---
def load_reports():
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, 'r') as f:
            return json.load(f)
    return []

# --- Utility: Save a Report ---
def save_report(report):
    reports = load_reports()
    reports.append(report)
    with open(REPORT_FILE, 'w') as f:
        json.dump(reports, f, indent=4)

# --- Optional: Alert via SMTP to other addresses ---
def send_smtp_alert(subject, body, recipients):
    sender_email = 'Sonikatk15@gmail.com'
    sender_password = 'kszw qupc wbvd bbvs'  # Gmail App Password

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
    except Exception as e:
        print(f"SMTP alert failed: {e}")

# --- Routes ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        location = request.form['location']
        description = request.form['description']
        user_email = request.form['email']

        report_data = {
            'location': location,
            'description': description,
            'email': user_email
        }

        # Save report to JSON file
        save_report(report_data)

        # 1. Send to Admin Team
        admin_recipients = ['rakshithat876@gmail.com']
        admin_msg = Message(
            'New Disaster Report Submitted',
            recipients=admin_recipients
        )
        admin_msg.body = f"""
📍 Location: {location}
📝 Description: {description}
📧 Reporter Email: {user_email}
"""
        mail.send(admin_msg)

        # 2. Confirm to Reporter
        user_msg = Message(
            'Your Disaster Report Was Received',
            recipients=[user_email]
        )
        user_msg.body = f"""Thank you for reporting a disaster.

We have received your report and will act as soon as possible.

📍 Location: {location}
📝 Description: {description}

Stay safe,
Disaster Management Team
"""
        mail.send(user_msg)

        # 3. (Optional) Send alert to other emergency contacts via smtplib
        smtp_recipients = ['rakshithat876@gmail.com', 'Sonikatk8@gmail.com']
        subject = f"Disaster Reported at {location}"
        smtp_message = f"A disaster has been reported.\n\nLocation: {location}\nDescription: {description}\nReporter Email: {user_email}"
        send_smtp_alert(subject, smtp_message, smtp_recipients)

        return redirect('/')

    return render_template('report.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/tips')
def tips():
    return render_template('tips.html')

@app.route('/reports')
def view_reports():
    reports = load_reports()
    return render_template('reports.html', reports=reports)

if __name__ == '__main__':
    app.run(debug=True)
