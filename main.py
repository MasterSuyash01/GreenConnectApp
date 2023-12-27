from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_url,logout_user,current_user,login_required


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/suyash/Downloads/RunVerve-main/database.db'  # SQLite database file path
db = SQLAlchemy(app)

# Define Models
class Users(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(120), nullable=False)
    Address = db.Column(db.String(200), nullable=False)

class Trees(db.Model):
    TreeID = db.Column(db.Integer, primary_key=True)
    TreeType = db.Column(db.String(50), nullable=False)
    TreeLocation = db.Column(db.String(100), nullable=False)
    DatePlanted = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(20), nullable=False)

class TreeAdoptions(db.Model):
    AdoptionID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    TreeID = db.Column(db.Integer, db.ForeignKey('trees.TreeID'), nullable=False)
    AdoptionDate = db.Column(db.String(20), nullable=False)

class ProduceDistribution(db.Model):
    DistributionID = db.Column(db.Integer, primary_key=True)
    TreeID = db.Column(db.Integer, db.ForeignKey('trees.TreeID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    DistributionDate = db.Column(db.String(20), nullable=False)
    SharePercentage = db.Column(db.Numeric, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template("Landingpage.html")

# ---------- Admin Login Page ------------
@app.route('/admin_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            return redirect('Admin_dashboard')
        else:
            message = 'Invalid username or password.'
            return render_template('admin_login.html', message=message)
    else:
        return render_template('admin_login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(UserName=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('user_login.html')

login_manager = LoginManager()
login_manager.login_view = 'user_login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get((user_id))



@app.route('/user_logout', methods=['GET', 'POST'])
def user_logout():   
    logout_user()
    return redirect("user_login")    

#user page
@app.route('/New_user')
def New_user():
    return render_template('New_user.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['password']
    
    user = Users(Username=username, Name=name, Email=email, Password=password, Confirm_Password=password)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return 'User created successfully'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
