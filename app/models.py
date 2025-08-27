from __future__ import annotations

import sqlite3
import os
from flask import current_app


def _get_connection():
	db_path = os.path.join(current_app.root_path, '..', 'database.db')
	return sqlite3.connect(db_path)


def ensure_tables_exist(app) -> None:
	# Run with app context to read config
	with app.app_context():
		conn = _get_connection()
		try:
			cur = conn.cursor()
			cur.execute(
				"""
				CREATE TABLE IF NOT EXISTS User (
					email VARCHAR(255) NOT NULL PRIMARY KEY,
					password_hash VARCHAR(255) NOT NULL,
					uptime_last_hour DATETIME NULL,
					uptime_last_day DATE NULL,
					uptime_last_week DATE NULL,
					downtime_last_hour DATETIME NULL,
					downtime_last_day DATE NULL,
					downtime_last_week DATE NULL
				);
				"""
			)
			conn.commit()
		finally:
			conn.close()


def create_user(email: str, password_hash: str) -> bool:
	conn = _get_connection()
	try:
		cur = conn.cursor()
		cur.execute(
			"INSERT INTO User (email, password_hash) VALUES (?, ?)",
			(email, password_hash),
		)
		conn.commit()
		return True
	except sqlite3.IntegrityError:
		return False
	finally:
		conn.close()


def get_user(email: str):
	conn = _get_connection()
	try:
		cur = conn.cursor()
		cur.execute("SELECT * FROM User WHERE email=?", (email,))
		row = cur.fetchone()
		if row:
			columns = [description[0] for description in cur.description]
			return dict(zip(columns, row))
		return None
	finally:
		conn.close()


def update_uptime(email: str, dt_hour, d_day, d_week) -> None:
	conn = _get_connection()
	try:
		cur = conn.cursor()
		cur.execute(
			"""
			UPDATE User
			SET uptime_last_hour=?, uptime_last_day=?, uptime_last_week=?
			WHERE email=?
			""",
			(dt_hour, d_day, d_week, email),
		)
		conn.commit()
	finally:
		conn.close()


def update_downtime(email: str, dt_hour, d_day, d_week) -> None:
	conn = _get_connection()
	try:
		cur = conn.cursor()
		cur.execute(
			"""
			UPDATE User
			SET downtime_last_hour=?, downtime_last_day=?, downtime_last_week=?
			WHERE email=?
			""",
			(dt_hour, d_day, d_week, email),
		)
		conn.commit()
	finally:
		conn.close()



