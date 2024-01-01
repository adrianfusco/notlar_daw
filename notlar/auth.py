from flask import request, jsonify, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from notlar import app, db, serializer, resend
from notlar.models import User
from sqlalchemy.exc import IntegrityError
import re
from flask_login import login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from itsdangerous import SignatureExpired
import logging

logger = logging.getLogger(__name__)

# Regex for email validation
EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# Reggex for password validation
PASSWORD_LENGTH_PATTERN = r'^.{8,}$'
PASSWORD_SPECIAL_CHARACTER_PATTERN = r'[!@#$%^&*(),.?":{}|<>]'
PASSWORD_NUMBER_PATTERN = r'\d'

# Allowed extensions for picture uploading
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Default picture for users without a pic configured in the profile
DEFAULT_PIC = 'default.png'


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
    return '.' in filename and file_extension in allowed_extensions


def is_valid_password(password):
    return (
        bool(re.match(PASSWORD_LENGTH_PATTERN, password)) and
        bool(re.search(PASSWORD_SPECIAL_CHARACTER_PATTERN, password)) and
        bool(re.search(PASSWORD_NUMBER_PATTERN, password))
    )


@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    This endpoint handles registration requests, validates the input data, and creates a new user in the database.

    Returns:
        str: JSON response indicating the result of the registration process.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        telegram_user = data.get('telegram_user')

        if not email or not password or not name or not last_name:
            return jsonify({'message': 'Missing required fields (email, username, password, name, or last_name)'}), 400

        if not re.match(EMAIL_PATTERN, email):
            return jsonify({'message': 'Invalid email format'}), 400

        app.logger.info(f"Received registration request for email: {email}")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, username=email, password=hashed_password, name=name, last_name=last_name,
                        phone_number=phone_number, telegram_user=telegram_user)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except IntegrityError as e:
        app.logger.warning(f"Registration failed due to IntegrityError: {e}")
        db.session.rollback()
        if 'email' in e.orig.args[0]:
            return jsonify({'message': 'Email already exists'}), 400
        elif 'username' in e.orig.args[0]:
            return jsonify({'message': 'Username already exists'}), 400
        else:
            return jsonify({'message': 'Registration failed due to a database error'}), 500
    except Exception as e:
        app.logger.error(f"Registration failed due to an unexpected error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Registration failed due to an unexpected error'}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        data = request.get_json(force=True)
        email_or_username = data.get('email') or data.get('username')
        password = data.get('password')
        remember_me = data.get('password')

        user_db = User.query.filter(
            db.or_(User.email == email_or_username, User.username == email_or_username)
        ).first()

        if not user_db or not check_password_hash(user_db.password, password):
            return jsonify({'error': 'Invalid email/username or password'}), 401

        login_user(user_db, remember=remember_me)

        return jsonify({'logged': 'successful'}), 200

    except Exception as e:
        app.logger.warning(e)
        return jsonify({'error': 'Internal Server Error. Ask the administrator'}), 500


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(e)
        raise


@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        user = current_user
        data = request.form
        new_name = data.get('name')
        new_last_name = data.get('last_name')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if (
            new_password or
            old_password or
            confirm_password) and not (
                confirm_password and
                old_password and
                new_password):
            return jsonify(
                {
                    'error': 'Old password, new password and confirmation password '
                             'is required when changing the password'
                }
            ), 401

        if old_password and not check_password_hash(user.password, old_password):
            return jsonify({'error': 'Incorrect old password'}), 401

        if new_password != confirm_password:
            return jsonify({'error': 'New password fields do not match'}), 401

        # Update user data
        user.name = new_name if new_name else user.name
        user.last_name = new_last_name if new_last_name else user.last_name

        if new_password:
            if not is_valid_password(new_password):
                return jsonify({
                    'error': 'Invalid new password. Password must be at least 8 characters long, '
                             'contain at least one special character, one number, and must not be '
                             'the same as the old password'
                }), 401

            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                file.save(file_path)
                user.profile_picture = filename
            elif file and file.filename != '':
                return jsonify({
                    'error': 'Invalid profile picture. '
                    'It must be a valid image file (png, jpg, jpeg, or gif) and have dimensions 64x64 pixels.'
                }
                ), 401

        db.session.commit()

        return jsonify({
            'name': user.name,
            'last_name': user.last_name,
            'telegram_user': user.telegram_user,
            'email': user.email,
            'username': user.username
        }), 200
    except Exception as e:
        app.logger.warning(str(e))
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error. Ask the administrator'}), 500


def generate_token(email):
    """
    Generates a token for password reset using the provided email.

    Parameters:
    - email (str): The email address for which the token is generated.

    Returns:
    str: The generated token.
    """
    return serializer.dumps(email, salt='password-reset-salt')


def create_reset_link(token):
    """
    Creates a reset password link using the given token.

    Parameters:
    - token (str): The token generated for password reset.

    Returns:
    str: The reset password link.
    """
    return url_for('reset_password', token=token, _external=True)


def password_reset(email, new_password):
    """
    Resets the password for the user with the specified email.

    Parameters:
    - email (str): The email address of the user.
    - new_password (str): The new password to set for the user.

    Raises:
    - ValueError: If the user with the given email is not found.
    """

    user = User.query.filter_by(email=email).first()
    if user:
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.password = hashed_password
        db.session.commit()
    else:
        raise ValueError('User not found')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Resets the password based on the provided token.

    Parameters:
    - token (str): The token used for password reset.

    Returns:
    - If method is 'GET':
        render_template: The reset password page.
    - If method is 'POST':
        - If successful:
            redirect: Redirects to the index page.
        - If unsuccessful:
            redirect: Redirects back to the reset password page.

    Raises:
    - SignatureExpired: If the token has expired.
    - Exception: If an error occurs during token decoding or password reset.
    """
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
        logger.info(f"Email retrieved from token: {email}")
    except SignatureExpired:
        logger.error('SignatureExpired: The password reset link has expired.')
        flash('The password reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        flash('An error occurred while processing the password reset link.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not is_valid_password(password):
            flash('Invalid password. Please ensure it meets the requirements.', 'danger')
            return redirect(url_for('reset_password', token=token))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('reset_password', token=token))

        try:
            password_reset(email, password)
            flash('Your password has been successfully reset.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            flash('An error occurred while resetting your password. Please try again.', 'danger')
            return redirect(url_for('reset_password', token=token))

    return render_template('reset_password.html', token=token)


def send_password_reset_email(email):
    """
    Sends a password reset email to the user with the provided email.

    Parameters:
    - email (str): The email address of the user.
    """
    token = generate_token(email)
    reset_link = create_reset_link(token)

    subject = 'Notlar Password Reset'

    html_body = render_template(
        'password_recovery_email.html',
        reset_link=reset_link
    )

    params = {
        "from": "Notlar <onboarding@resend.dev>",
        "to": [f"{email}"],
        "subject": subject,
        "html": html_body
    }

    resend.Emails.send(params)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Handles the forgot password functionality.

    Returns:
    - If method is 'GET':
        render_template: The forgot password page.
    - If method is 'POST':
        - If successful:
            flash: Displays a success message and redirects to the login page.
        - If unsuccessful:
            flash: Displays an error message and stays on the forgot password page.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(email)
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            flash('Invalid email address. Please try again.', 'danger')

    return render_template('forgot_password.html')
