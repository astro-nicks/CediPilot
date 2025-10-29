from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User, Transaction
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import date

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "replace-this-with-a-secret"  # change for production
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cedi_pilot.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email").strip().lower()
            name = request.form.get("name").strip()
            password = request.form.get("password")
            if User.query.filter_by(email=email).first():
                flash("Email already registered. Try logging in.", "warning")
                return redirect(url_for("login"))

            pw_hash = generate_password_hash(password)
            user = User(email=email, name=name, password_hash=pw_hash)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email").strip().lower()
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid email or password.", "danger")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        # simple aggregates
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        total_income = sum(t.amount for t in transactions if t.t_type == "income")
        total_expense = sum(t.amount for t in transactions if t.t_type == "expense")
        balance = total_income - total_expense

        # category totals for a simple chart later
        category_totals = {}
        for t in transactions:
            if t.t_type == "expense":
                category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

        return render_template(
            "dashboard.html",
            transactions=transactions,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            category_totals=category_totals
        )

    @app.route("/transaction/add", methods=["GET", "POST"])
    @login_required
    def add_transaction():
        if request.method == "POST":
            amount = float(request.form.get("amount"))
            category = request.form.get("category")
            t_type = request.form.get("t_type")
            note = request.form.get("note", "")
            date_str = request.form.get("date")
            t_date = date.fromisoformat(date_str) if date_str else date.today()

            txn = Transaction(
                user_id=current_user.id,
                amount=amount,
                category=category,
                t_type=t_type,
                note=note,
                date=t_date
            )
            db.session.add(txn)
            db.session.commit()
            flash("Transaction added.", "success")
            return redirect(url_for("dashboard"))

        # default categories (you can expand later)
        categories = ["Food", "Transport", "Bills", "Entertainment", "Salary", "Other"]
        return render_template("add_transaction.html", categories=categories)

    @app.route("/transaction/delete/<int:txn_id>", methods=["POST"])
    @login_required
    def delete_transaction(txn_id):
        txn = Transaction.query.get_or_404(txn_id)
        if txn.user_id != current_user.id:
            flash("Not allowed.", "danger")
            return redirect(url_for("dashboard"))
        db.session.delete(txn)
        db.session.commit()
        flash("Transaction deleted.", "info")
        return redirect(url_for("dashboard"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
