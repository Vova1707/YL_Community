from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from db_session import create_session
from models.blog import Poster
from models.projects import Project
from models.users import User
from werkzeug.security import check_password_hash, generate_password_hash


profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Пароли не совпадают.', 'danger')
            return render_template('register/register.html')

        session = create_session()
        try:
            existing_user = session.query(User).filter((User.email == email) | (User.name == username)).first()

            if existing_user:
                flash('Пользователь с таким email или именем уже существует.', 'danger')
                return render_template('register/register.html')

            hashed_password = generate_password_hash(password)
            new_user = User(name=username, email=email, password_hash=hashed_password)  # Правильное присвоение значений экземпляру
            session.add(new_user)
            session.commit()

            flash('Регистрация прошла успешно! Пожалуйста, войдите.', 'success')
            return redirect(url_for('profile.login'))

        except Exception as e:
            session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')  # Show error to user.
            return render_template('register/register.html') # Return to register page on error

        finally:
            session.close()  # Закрываем сессию в блоке finally

    return render_template('register/register.html')

@profile_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        session = create_session()
        user = session.query(User).filter(User.email == email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль.', 'danger')
            return render_template('register/login.html')
    print(request.method)
    return render_template('register/login.html')

@profile_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

@profile_bp.route('/')
@profile_bp.route('/index')
def index():
    flash('Вы вошли в свой профиль.', 'info')
    session = create_session()
    posts = session.query(Poster).filter(Poster.user_id == current_user.id)
    projects = session.query(Project).filter(Project.user_id == current_user.id)
    return render_template('profile/profile.html', posts=posts, projects=projects)