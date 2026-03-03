from flask import Flask, render_template, request, redirect, session
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 🔐 Secret Key
app.secret_key = "your_secret_key"

# 🔹 Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ================= USER MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"{self.username}"


# ================= TODO MODEL =================
class Database(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"{self.sno} - {self.title}"


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "User already exists!"

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/")
        else:
            return "Invalid Credentials"

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


# ================= HOME =================
@app.route("/", methods=['GET', 'POST'])
def home():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        data = Database(title=title, desc=desc)
        db.session.add(data)
        db.session.commit()

    alldata = Database.query.all()

    return render_template("index.html", alldata=alldata)


# ================= UPDATE =================
@app.route("/update/<int:sno>", methods=['GET', 'POST'])
def update(sno):

    data = Database.query.filter_by(sno=sno).first()

    if request.method == "POST":
        data.title = request.form.get('title')
        data.desc = request.form.get('desc')
        db.session.commit()
        return redirect("/")

    return render_template("update.html", data=data)


# ================= DELETE =================
@app.route("/delete/<int:sno>")
def delete(sno):
    data = Database.query.filter_by(sno=sno).first()
    db.session.delete(data)
    db.session.commit()
    return redirect("/")


# ================= ABOUT =================
@app.route("/about")
def about():
    return render_template("about.html")


# ================= MAIN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
