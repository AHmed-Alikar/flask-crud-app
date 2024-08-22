from flask import Flask, render_template, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "my_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Table User / Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    hash_password = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.hash_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hash_password, password)

# Table Tasks / Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', backref=db.backref('tasks', lazy=True))

    def __repr__(self):
        return f"Task {self.id}"

@app.route("/auth")
def auth():
    if "username" in session:
        return redirect(url_for('home'))
    return render_template('auth.html')

# Register
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    user = Users.query.filter_by(username=username).first()
    
    if user:
        return render_template('auth.html', error="User already registered")
    else:
        new_user = Users(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('home'))

# Login
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = Users.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['username'] = username
        session['user_id'] = user.id  # Store user ID in session
        return redirect(url_for('home'))
    else:
        return render_template('auth.html', error="Invalid credentials")

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('auth'))


# Home page
@app.route("/home", methods=["POST", "GET"]) 
def home():
    print(f"Current URL: {url_for('home')}")  # Debugging URL generation
    if "username" in session:   
        username = session['username']  
        user_id = session['user_id']
        if request.method == "POST": 
            current_task = request.form['contant']
            new_task = Task(content=current_task, user_id=user_id)
            try:
                db.session.add(new_task)
                db.session.commit()
                print("Redirecting to:", url_for('home'))  # Debugging redirection
                return redirect(url_for('home'))  # Corrected: Redirect to the 'home' function
            except Exception as error:
                return f"Error: {error}"
        else:
            tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created).all()  # Filter tasks by user
            return render_template('home.html', tasks=tasks, username=username)
    else:
        return redirect(url_for('auth'))

# Delete tasks
@app.route('/delete/<int:id>')
def delete(id: int):
    if "username" in session:
        task = Task.query.get_or_404(id)
        if task.user_id == session['user_id']:  # Ensure user can only delete their own tasks
            try:
                db.session.delete(task)
                db.session.commit()
                return redirect(url_for('home'))
            except Exception as error:
                return f"Error deleting task: {error}"
        else:
            return redirect(url_for('home'))  # Redirect if the task does not belong to the user
    else:
        return redirect(url_for('auth'))

# Edit tasks or update tasks
@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id: int):
    if "username" in session:
        task = Task.query.get_or_404(id)
        if task.user_id == session['user_id']:  # Ensure user can only edit their own tasks
            if request.method == 'POST':
                task.content = request.form['content']
                try:
                    db.session.commit()
                    return redirect(url_for('home'))  # Redirect to prevent form resubmission
                except Exception as error:
                    return f"Error updating task: {error}"
            else:     
                return render_template('edit.html', username=session.get('username'), task=task)
        else:
            return redirect(url_for('home'))  # Redirect if the task does not belong to the user
    else:
        return redirect(url_for('auth'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
