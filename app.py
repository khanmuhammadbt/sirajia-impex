from flask import Flask, render_template
from werkzeug.exceptions import TooManyRequests
from extensions import db, limiter
from main import main_bp
from main.auth.auth import auth_bp
from config import config
from model.user import User


def create_app():
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    @app.errorhandler(TooManyRequests)
    def handle_rate_limit(_error):
        return render_template(
            'login.html',
            rate_limit_message='Too many login attempts. Try again later.',
        ), 429

    with app.app_context():
        from model.data import migrate_legacy_database
        migrate_legacy_database()
        db.create_all()
        if User.query.first() is None and app.config.get('ADMIN_PASSWORD_HASH'):
            db.session.add(User(
                username=app.config['ADMIN_USERNAME'],
                password_hash=app.config['ADMIN_PASSWORD_HASH'],
            ))
            db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True, reloader_type='stat')
