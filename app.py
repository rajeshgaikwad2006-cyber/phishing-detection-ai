from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import joblib

app = Flask(__name__)
app.secret_key = "secret123"

# SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Load ML model
model = joblib.load("model.pkl")


# ---------------- DATABASE MODEL ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# Create DB
with app.app_context():
    db.create_all()


# ---------------- FEATURES ----------------
def extract_features(url):
    return [
        len(url),
        url.count("."),
        url.count("-"),
        url.count("/"),
        url.count("@"),
        1 if "https" in url else 0,
        1 if "login" in url.lower() else 0,
        1 if "secure" in url.lower() else 0,
        1 if "verify" in url.lower() else 0,
        1 if "update" in url.lower() else 0
    ]


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_exists = User.query.filter_by(username=username).first()

        if user_exists:
            msg = "User already exists!"
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            msg = "User created successfully! Please login."

    return render_template("register.html", msg=msg)


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        print("USERNAME:", username)
        print("USER:", user)

        if user:
            print("HASH:", user.password)

        if user and check_password_hash(user.password, password):
            session["user"] = username
            print("LOGIN SUCCESS")
            return redirect(url_for("home"))
        else:
            print("LOGIN FAILED")
            msg = "Invalid username or password"

    return render_template("login.html", msg=msg)
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    result = ""

    total_scans = 0
    safe_urls = 0
    phishing_urls = 0

    if request.method == "POST":
        url = request.form["url"]
        features = extract_features(url)

        prediction = model.predict([features])[0]

        total_scans += 1

        if prediction == 1:
            result = "⚠️ Phishing Website"
            phishing_urls += 1
        else:
            result = "✅ Safe Website"
            safe_urls += 1

    return render_template(
        "index.html",
        result=result,
        user=session["user"],
        total_scans=total_scans,
        safe_urls=safe_urls,
        phishing_urls=phishing_urls
    )


if __name__ == "__main__":
    app.run(debug=True)