from __future__ import annotations

import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from .utils import hash_password, verify_password, now_hour, today_date, week_start_date
from .models import create_user, get_user, update_uptime, update_downtime


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
	if session.get("user_email"):
		return redirect(url_for("main.dashboard"))
	return render_template("index.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		if not email or not password:
			flash("Email and password are required.", "error")
			return redirect(url_for("main.register"))

		if get_user(email):
			flash("Email already registered.", "error")
			return redirect(url_for("main.register"))

		pw_hash = hash_password(password)
		ok = create_user(email, pw_hash)
		if not ok:
			flash("Registration failed. Try a different email.", "error")
			return redirect(url_for("main.register"))

		flash("Registration successful. Please log in.", "success")
		return redirect(url_for("main.login"))

	return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		user = get_user(email)
		if not user or not verify_password(user["password_hash"], password):
			flash("Invalid email or password.", "error")
			return redirect(url_for("main.login"))

		# Set session and update uptime fields
		session["user_email"] = email
		u_dt = now_hour()
		u_day = today_date()
		u_week = week_start_date(u_day)
		update_uptime(email, u_dt, u_day, u_week)
		return redirect(url_for("main.dashboard"))

	return render_template("login.html")


@bp.route("/logout")
def logout():
	email = session.pop("user_email", None)
	if email:
		d_dt = now_hour()
		d_day = today_date()
		d_week = week_start_date(d_day)
		update_downtime(email, d_dt, d_day, d_week)
	flash("You have been logged out.", "success")
	return redirect(url_for("main.index"))


@bp.route("/dashboard")
def dashboard():
	email = session.get("user_email")
	if not email:
		return redirect(url_for("main.login"))
	user = get_user(email)
	return render_template("dashboard.html", user=user)


@bp.route("/download-csv")
def download_csv():
	email = session.get("user_email")
	if not email:
		return redirect(url_for("main.login"))
	
	user = get_user(email)
	if not user:
		flash("User not found.", "error")
		return redirect(url_for("main.dashboard"))
	
	# Create CSV data
	output = io.StringIO()
	writer = csv.writer(output)
	
	# Write header
	writer.writerow(['Field', 'Value'])
	
	# Write user data
	writer.writerow(['Email', user['email']])
	writer.writerow(['Uptime last hour', user.get('uptime_last_hour', '-')])
	writer.writerow(['Uptime last day', user.get('uptime_last_day', '-')])
	writer.writerow(['Uptime last week', user.get('uptime_last_week', '-')])
	writer.writerow(['Downtime last hour', user.get('downtime_last_hour', '-')])
	writer.writerow(['Downtime last day', user.get('downtime_last_day', '-')])
	writer.writerow(['Downtime last week', user.get('downtime_last_week', '-')])
	
	# Create response
	output.seek(0)
	return Response(
		output.getvalue(),
		mimetype='text/csv',
		headers={'Content-Disposition': f'attachment; filename=user_details_{email}.csv'}
	)


