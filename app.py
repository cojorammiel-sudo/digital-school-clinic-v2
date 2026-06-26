from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os

app = Flask(__name__)
app.secret_key = "clinic_secret_key"

USER_FILE = "users.json"


# -------------------------
# Helper functions
# -------------------------
def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump([], f)

    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    return render_template("home.html")


# -------------------------
# Student Portal
# -------------------------
@app.route("/student")
def student_portal():
    return render_template("student_portal.html")


# -------------------------
# Login
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        student_number = request.form["student_number"]
        password = request.form["password"]

        users = load_users()

        for user in users:
            if user["student_number"] == student_number and user["password"] == password:

                session["student_number"] = user["student_number"]
                session["fullname"] = user["fullname"]

                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))

        flash("Invalid student number or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


# -------------------------
# Sign Up
# -------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form["fullname"]
        student_number = request.form["student_number"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        users = load_users()

        # Check duplicate student number
        for user in users:
            if user["student_number"] == student_number:
                flash("Student number already registered.", "danger")
                return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))

        new_user = {
            "fullname": fullname,
            "student_number": student_number,
            "email": email,
            "password": password
        }

        users.append(new_user)
        save_users(users)

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# -------------------------
# Forgot Password
# -------------------------
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        student_number = request.form["student_number"]
        email = request.form["email"]
        new_password = request.form["new_password"]

        users = load_users()
        found = False

        for user in users:
            if user["student_number"] == student_number and user["email"] == email:
                user["password"] = new_password
                found = True
                break

        if found:
            save_users(users)
            flash("Password updated successfully. You can now log in.", "success")
            return redirect(url_for("login"))

        flash("Account not found. Check your student number and email.", "danger")
        return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


# -------------------------
# Student Dashboard
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "student_number" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        fullname=session.get("fullname"),
        student_number=session.get("student_number")
    )


# -------------------------
# Logout
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
