from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from db_session import create_session
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
        existing_user = session.query(User).filter((User.email == email) | (User.username == username)).first()

        if existing_user:
            flash('Пользователь с таким email или именем уже существует.', 'danger')
            return render_template('register/register.html')

        hashed_password = generate_password_hash(password)
        is_admin = True # Исправить
        new_user = User(username=username, email=email, password_hash=hashed_password, is_admin=is_admin)
        session.add(new_user)
        session.commit()

        flash('Регистрация прошла успешно! Пожалуйста, войдите.', 'success')
        return redirect(url_for('profile.login'))

    return render_template('register/register.html')

@profile_bp.route('/login', methods=['GET', 'POST'])
def login():
    print(1)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        session = create_session()
        user = session.query(User).filter(User.email == email).first()
        print(2)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            print(3)
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль.', 'danger')
            print(4)
            return render_template('register/login.html')
    print(request.method)
    print(5)
    return render_template('register/login.html')

@profile_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('other.index'))
