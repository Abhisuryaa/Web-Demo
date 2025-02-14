from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import logging

# Create Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Replace with a real secret key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techvritti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    certifications = db.Column(db.Text)
    experience = db.Column(db.Text)
    known_software = db.Column(db.String(200))
    soft_skills = db.Column(db.String(200))
    resume_path = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        # Log the input password and user password hash
        logging.debug(f'Input Password: {password}')
        if user:
            logging.debug(f'User Password Hash: {user.password_hash}')
        else:
            logging.debug('User not found')
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
            
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for admin dashboard
    total_students = User.query.count()
    total_quizzes = Quiz.query.count()
    
    # Calculate average score
    quizzes = Quiz.query.all()
    avg_score = sum(quiz.score for quiz in quizzes) / total_quizzes if total_quizzes > 0 else 0
    
    # Get all students with their latest quiz scores
    students = User.query.all()
    for student in students:
        latest_quiz = Quiz.query.filter_by(user_id=student.id).order_by(Quiz.completed_at.desc()).first()
        student.quiz_score = latest_quiz.score if latest_quiz else None
    
    return render_template('dashboard.html',
                         total_students=total_students,
                         total_quizzes=total_quizzes,
                         avg_score=round(avg_score),
                         students=students)

@app.route('/student/<int:student_id>')
@login_required
def get_student(student_id):
    student = User.query.get_or_404(student_id)
    latest_quiz = Quiz.query.filter_by(user_id=student_id).order_by(Quiz.completed_at.desc()).first()
    
    return jsonify({
        'id': student.id,
        'full_name': student.full_name,
        'email': student.email,
        'qualification': student.qualification,
        'graduation_year': student.graduation_year,
        'skills': student.skills,
        'certifications': student.certifications,
        'experience': student.experience,
        'known_software': student.known_software,
        'soft_skills': student.soft_skills,
        'quiz_score': latest_quiz.score if latest_quiz else None
    })

@app.route('/export-students')
@login_required
def export_students():
    import csv
    from io import StringIO
    
    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Full Name', 'Email', 'Qualification', 'Skills', 'Quiz Score'])
    
    # Write student data
    students = User.query.all()
    for student in students:
        latest_quiz = Quiz.query.filter_by(user_id=student.id).order_by(Quiz.completed_at.desc()).first()
        writer.writerow([
            student.full_name,
            student.email,
            student.qualification,
            student.skills,
            latest_quiz.score if latest_quiz else 'Not taken'
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=students.csv'}
    )

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.qualification = request.form.get('qualification')
        current_user.graduation_year = request.form.get('graduation_year')
        current_user.skills = request.form.get('skills')
        current_user.certifications = request.form.get('certifications')
        current_user.experience = request.form.get('experience')
        current_user.known_software = request.form.get('known_software')
        current_user.soft_skills = request.form.get('soft_skills')
        
        if 'resume' in request.files:
            resume = request.files['resume']
            if resume:
                filename = secure_filename(f"resume_{current_user.id}_{resume.filename}")
                resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.resume_path = filename
        
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('profile'))
        
    return render_template('profile.html')

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    data = request.get_json()
    score = data.get('score')
    quiz = Quiz(user_id=current_user.id, score=score)
    db.session.add(quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz submitted successfully'})

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
