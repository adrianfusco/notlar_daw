from flask import request, jsonify, render_template, session, flash
from notlar import app, db, resend, babel
from notlar.models import User, Note
from datetime import datetime
from flask import redirect, url_for
from . import login_manager, current_user
from sqlalchemy import desc


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.errorhandler(500)
@app.errorhandler(400)
def internal_server_error(error):
    """
    Render error template. Doesn't matter if it's
    a client or server error
    """
    return render_template('error.html'), error.code


@app.errorhandler(404)
def not_found(error):
    """
    In case of 404 error render not found template
    """
    return render_template('not_found.html'), error.code


@app.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer)


@babel.localeselector
def get_locale():
    return session.get('language', 'en')


@app.route('/', methods=['GET'])
def index():
    """
    Render index template
    Redirecto to dashboard if there's a user logged
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_notes_management'))
    return render_template('index.html')


@app.route('/dashboard_notes_management', methods=['GET'])
def dashboard_notes_management():
    """
    Render notes management dashboard template
    """
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    current_date_time = datetime.now()
    today_formatted_date = current_date_time.strftime('%d/%m/%Y')

    return render_template(
        'dashboard_notes_management.html',
        user_email=current_user.email,
        user_name=current_user.name,
        todays_date=today_formatted_date,
        profile_picture=current_user.profile_picture
    ), 200


@app.route('/dashboard_all_notes', methods=['GET'])
def dashboard_all_notes():
    """
    Render all notes dashboard template
    """
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template(
        'dashboard_all_notes.html',
        user_email=current_user.email,
        user_name=current_user.name,
        profile_picture=current_user.profile_picture
    ), 200


@app.route('/dashboard_home', methods=['GET'])
def dashboard_home():
    """
    Render dashboard home template
    """
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template(
        'dashboard_home.html',
        user_email=current_user.email,
        user_name=current_user.name,
        profile_picture=current_user.profile_picture
    ), 200


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Handle contact form submissions.

    If the request method is POST, validate the form data (name, email, and message).
    If any of the required fields is missing, display an error message using flash
    and redirect back to the contact form. Otherwise, send a confirmation email and
    display a success message.

    Returns:
        render_template: Renders the 'contact.html' template.

    """
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # We can fetch the message and do something with this)...
        # message = request.form.get('message')
        # It's a feedback and the company should check it
        # Since we just wanna show we can send an email from this project then
        # I won't implement anything for this

        if not name or not email or not message:
            flash('All fields are required.', 'danger')
            return render_template('contact.html')

        html_body = render_template('contact_email.html', name=name)

        params = {
            "from": "Notlar <onboarding@resend.dev>",
            "to": [f"{email}"],
            "subject": "Notlar Feedback received!",
            "html": html_body
        }

        resend.Emails.send(params)

        flash('We have received your message.', 'success')

    return render_template('contact.html')


@app.route('/settings', methods=['GET'])
def settings():
    """
    Route to display user settings.

    Returns:
        str: Rendered HTML template for settings.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template(
        'settings.html',
        email=current_user.email,
        name=current_user.name,
        last_name=current_user.last_name,
        profile_picture=current_user.profile_picture
    ), 200


@app.route('/password-recovery', methods=['GET'])
def password_recovery():
    """
    Route to render password recovery template
    """
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('password_recovery.html'), 200


@app.route('/get_notes', methods=['GET'])
def get_notes():
    """
    Route to retrieve notes for a specific date.

    Returns:
        JSON: Notes data in JSON format.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    date_str = request.args.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    notes = Note.query.filter_by(user_id=current_user.id, created_at=selected_date).all()

    notes_data = [
        {
            "date": note.created_at.strftime('%Y-%m-%d'),
            "content": note.text,
            "number": note.id,
            "color": note.color
        } for note in notes]
    return jsonify(notes_data), 200


@app.route('/all_notes', methods=['GET'])
def list_notes_by_date_range():
    """
    Route to retrieve notes within a date range.

    Returns:
        JSON: Notes data in JSON format.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

    query = Note.query.filter_by(user_id=current_user.id)

    if start_date and end_date:
        query = query.filter(Note.created_at >= start_date, Note.created_at <= end_date)
    elif start_date:
        query = query.filter(Note.created_at >= start_date)
    elif end_date:
        query = query.filter(Note.created_at <= end_date)

    query = query.order_by(desc(Note.created_at))

    notes = query.all()

    notes_data = [
        {
            "date": note.created_at.strftime('%Y-%m-%d'),
            "content": note.text,
            "number": note.id,
            "color": note.color
        } for note in notes]

    return jsonify(notes_data), 200


@app.route('/create_note', methods=['POST'])
def create_note():
    """
    Route to create a new note.

    Returns:
        JSON: Response message in JSON format.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    data = request.json
    title = data.get('title', '')
    text = data.get('text', '')

    color = data.get('color', '#FFFFFF')

    created_at = datetime.strptime(data.get('created_at'), '%Y-%m-%d').date()

    new_note = Note(title=title, text=text, color=color, user=current_user, created_at=created_at)
    db.session.add(new_note)
    db.session.commit()

    return jsonify({"message": "Note created successfully"}), 201


@app.route('/delete_note/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """
    Route to delete a note.

    Args:
        note_id (int): ID of the note to be deleted.

    Returns:
        JSON: Response message in JSON format.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    note = Note.query.get(note_id)

    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": "Note deleted successfully"}), 200
    else:
        return jsonify({"error": "Note not found or unauthorized"}), 404
