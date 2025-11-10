from flask import Flask
from flask_login import LoginManager
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cedi_pilot.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # redirects to login page if not logged in
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from auth import auth
    from main import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
