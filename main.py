from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Transaction

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return redirect(url_for("auth.login"))


@main.route("/dashboard")
@login_required
def dashboard():
    txns = Transaction.query.filter_by(user_id=current_user.id).all()

    total_income = sum(t.amount for t in txns if t.t_type == "income")
    total_expense = sum(t.amount for t in txns if t.t_type == "expense")
    balance = total_income - total_expense

    return render_template(
        "dashboard.html",
        transactions=txns,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        category_totals={},  # placeholder
        monthly_totals={}    # placeholder
    )


@main.route("/add_transaction", methods=["POST"])
@login_required
def add_transaction():
    try:
        amount = float(request.form.get("amount"))
        category = request.form.get("category")
        t_type = request.form.get("t_type")
        note = request.form.get("note")
        date = request.form.get("date")

        txn = Transaction(
            user_id=current_user.id,
            amount=amount,
            category=category,
            t_type=t_type,
            note=note,
            date=date
        )
        db.session.add(txn)
        db.session.commit()
        flash("Transaction added!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding transaction: {e}", "error")

    return redirect(url_for("main.dashboard"))


@main.route("/delete_transaction/<int:txn_id>", methods=["POST"])
@login_required
def delete_transaction(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    if txn.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("main.dashboard"))

    db.session.delete(txn)
    db.session.commit()
    flash("Transaction deleted!", "info")
    return redirect(url_for("main.dashboard"))
