from flask import Flask


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.update(
		SECRET_KEY="change-this-secret-key",
		MYSQL_HOST="localhost",
		MYSQL_USER="root",
		MYSQL_PASSWORD="1234",
		MYSQL_DATABASE="wordpress",
	)

	
	from .routes import bp as main_bp
	app.register_blueprint(main_bp)


	from .models import ensure_tables_exist
	ensure_tables_exist(app)

	return app
