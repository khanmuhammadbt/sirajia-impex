import logging
from datetime import datetime, timedelta

from flask import redirect, render_template, request, url_for, flash, session
from extensions import db
from extensions import limiter
from werkzeug.security import check_password_hash
from model.user import User
from . import auth_bp

logger = logging.getLogger(__name__)

# 1. Added 'GET' to methods so the page can actually load
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute', methods=['POST'])
def login():
    if 'username' in session :
        return redirect(url_for('main.bill'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')

        valid_input = (
            1 <= len(username) <= 150
            and isinstance(password, str)
            and 1 <= len(password) <= 256
        )
        user = User.query.filter_by(username=username).first()
        now = datetime.utcnow()
        if user and user.locked_until:
            if user.locked_until > now:
                flash('Account temporarily locked. Try again later.', 'error')
                return render_template('login.html')
            user.failed_login_attempts = 0
            user.locked_until = None

        valid_password = False
        if valid_input and user:
            try:
                valid_password = check_password_hash(user.password_hash, password)
            except (TypeError, ValueError):
                valid_password = False

        if valid_input and user and valid_password:
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()
            session.clear()
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                db.session.commit()
            logger.warning('Failed login attempt for username=%r from IP=%s', username, request.remote_addr)
            flash('Invalid username or password', 'error')
            return render_template("login.html")
    
    # 3. Render the login template for GET requests
    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))