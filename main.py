from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ===== MODELOS =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# ===== RUTAS =====
@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_email"] = user.email
            return redirect("/index")
        else:
            error = "Credenciales incorrectas"
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=request.form["password"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("registration.html")

@app.route("/index")
def index():
    if "user_email" not in session:
        return redirect("/login")
    cards = Card.query.filter_by(user_email=session["user_email"]).all()
    return render_template("index.html", cards=cards)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        card = Card(
            title=request.form["title"],
            subtitle=request.form["subtitle"],
            text=request.form["text"],
            user_email=session["user_email"]
        )
        db.session.add(card)
        db.session.commit()
        return redirect("/index")
    return render_template("create_card.html")

@app.route("/card/<int:id>")
def card(id):
    card = Card.query.get(id)
    return render_template("card.html", card=card)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
