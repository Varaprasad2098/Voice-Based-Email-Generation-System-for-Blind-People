from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from voice_processing.voice_processor import process_voice_command
import imaplib
import email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'prasad321465@gmail.com'
app.config['MAIL_PASSWORD'] = 'tqgx jmmy jsur rcju'

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/inbox')
@login_required
def inbox():
    # Connect to Gmail
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    imap.select("inbox")

    # Fetch all emails (was limited to 5)
    status, messages = imap.search(None, "ALL")
    email_ids = messages[0].split()
    latest_ids = email_ids  # Show all emails

    email_data = []
    for i in reversed(latest_ids):
        res, msg_data = imap.fetch(i, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        subject = msg["subject"]
        sender = msg["from"]
        snippet = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    snippet = part.get_payload(decode=True).decode(errors="ignore")[:200]
                    break
        else:
            snippet = msg.get_payload(decode=True).decode(errors="ignore")[:200]

        email_data.append({
            "subject": subject,
            "sender": sender,
            "snippet": snippet
        })

    imap.logout()

    return render_template("inbox.html", emails=email_data)

@app.route('/compose', methods=['GET', 'POST'])
@login_required
def compose_email():
    if request.method == 'POST':
        recipient = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
        msg.body = body
        mail.send(msg)
        return render_template('compose_email.html', mail_sent=True)
    return render_template('compose_email.html')

@app.route('/process_command', methods=['POST'])
@login_required
def process_command():
    data = request.get_json()
    command = data.get('command', '').lower()

    if "compose email" in command:
        return jsonify(success=True, message="Navigating to compose email.")
    elif "read email" in command:
        return jsonify(success=True, message="Reading your emails.")
    elif "delete email" in command:
        return jsonify(success=True, message="Deleting the email.")
    else:
        return jsonify(success=False, message="Command not recognized.")

@app.route('/read_emails')
@login_required
def read_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    mail.select("inbox")

    result, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    latest_ids = mail_ids[-5:]

    email_list = []
    for i in reversed(latest_ids):
        result, message_data = mail.fetch(i, '(RFC822)')
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = msg['subject']
        sender = msg['from']
        email_list.append(f"<b>From:</b> {sender} <br><b>Subject:</b> {subject}<br><br>")

    mail.logout()
    return "<h2>Last 5 Emails</h2>" + ''.join(email_list)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
