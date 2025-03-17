import os
import uuid

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from db_session import create_session
from models.blog import Poster
from models.projects import Project
from models.users import User
from forms.profile import Profile_edit_form
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
    user = session.query(User).filter(User.id == current_user.id).first()
    posts = session.query(Poster).filter(Poster.user_id == current_user.id)
    projects = session.query(Project).filter(Project.user_id == current_user.id)
    print(user.image_profile)
    return render_template('profile/profile.html', posts=posts, projects=projects, user=user)


@profile_bp.route('/edit_profile')
@profile_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = Profile_edit_form()

    if request.method == "POST":
        if form.validate_on_submit():
            name = form.name.data
            surname = form.surname.data
            age = form.age.data
            about = form.about.data
            email = form.email.data
            image_profile = form.image_profile.data

            session = create_session()
            user = session.query(User).filter(User.id == current_user.id).first()

            user.name = name
            user.surname = surname
            user.age = age
            user.about = about
            user.email = email
            user.image_profile = load_photo(image_profile)
            session.commit()
            flash('Профиль успешно обновлен!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Ошибка валидации формы. Проверьте введенные данные.', 'danger')
            return render_template('profile/profile_edit.html', form=form)

    elif request.method == "GET":
        session = create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        if user:
            form.name.data = user.name
            form.surname.data = user.surname
            form.age.data = user.age
            form.about.data = user.about
            form.email.data = user.email
        return render_template('profile/profile_edit.html', form=form)


def load_photo(image_profile):
    if image_profile:
        filename = secure_filename(image_profile.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        if not os.path.exists('static/media/'):
            os.makedirs('static/media')

        filepath = os.path.join('static/media/', unique_filename)
        image_profile.save(filepath)
        return 'media/' + unique_filename