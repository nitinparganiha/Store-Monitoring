from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password: str) -> str:
	return generate_password_hash(plain_password)


def verify_password(pw_hash: str, candidate: str) -> bool:
	return check_password_hash(pw_hash, candidate)


def now_hour() -> datetime:
	return datetime.now()


def today_date() -> date:
	return date.today()


def week_start_date(d: date | None = None) -> date:
	base = d or date.today()
	# ISO weekday: Monday=1, Sunday=7
	return base - timedelta(days=base.isoweekday() - 1)




