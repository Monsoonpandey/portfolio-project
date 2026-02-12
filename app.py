from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(300))
    image_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    live_url = db.Column(db.String(500))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    projects = Project.query.limit(3).all()
    return render_template('index.html', projects=projects)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    projects = Project.query.all()
    return render_template('portfolio.html', projects=projects)

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', posts=posts)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_post.html')

@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        flash('You can only edit your own posts!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_post.html', post=post)

@app.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author == current_user:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you for your message! I\'ll get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# Create database and sample data - SIMPLE & WORKING
@app.cli.command("init-db")
def init_db():
    db.create_all()
        # Add projects with REAL, RELATABLE images
    if Project.query.count() == 0:
        projects = [
            Project(
                title="Rent Anime Boyfriend",
                description="An innovative e-commerce platform where users can 'rent' anime boyfriend characters. Features include character profiles, booking system, payment integration, and user reviews. Built with React for dynamic UI.",
                technologies="React, HTML5, CSS3, JavaScript, Node.js",
                image_url="https://images.pexels.com/photos/8474824/pexels-photo-8474824.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop",
                github_url="https://github.com/Monsoonpandey/rent-anime-boyfriend",
                live_url="#"
            ),
            Project(
                title="Movie Booking System",
                description="A full-stack movie ticket booking platform with Firebase integration. Users can browse movies, select seats, make bookings, and receive confirmations. Deployed on Vercel.",
                technologies="React, Firebase, HTML5, CSS3, JavaScript, Vercel",
                image_url="https://images.pexels.com/photos/7991379/pexels-photo-7991379.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop",
                github_url="https://github.com/Monsoonpandey/movie-booking-system",
                live_url="#"
            ),
            Project(
                title="Modern Portfolio Website",
                description="A sleek, responsive portfolio website built with HTML5, CSS3, and Tailwind CSS. Features smooth animations, dark mode, project gallery, and contact form.",
                technologies="HTML5, CSS3, Tailwind CSS, JavaScript",
                image_url="https://images.pexels.com/photos/196644/pexels-photo-196644.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop",
                github_url="https://github.com/Monsoonpandey/tailwind-portfolio",
                live_url="#"
            )
        ]
        
        for project in projects:
            db.session.add(project)
        db.session.commit()
        print("✅ Projects added with REAL images!")
    
        
        
    
    # Add admin user
    if User.query.count() == 0:
        admin = User(username="admin", email="admin@example.com")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created! Username: admin, Password: admin123")
    
    print("✅ Database ready!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)