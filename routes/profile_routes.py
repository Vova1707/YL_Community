import os
import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from db_session import create_session
from models.blog import Poster
from models.projects import Project
from models.users import User
from werkzeug.security import check_password_hash, generate_password_hash
from forms.profile import Profile_edit_form
from models.blog import ImagePoster, Subscribes_User


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
            existing_user = (
                session.query(User)
                .filter((User.email == email) | (User.name == username))
                .first()
            )

            if existing_user:
                flash(
                    'Пользователь с таким email или именем уже существует.',
                    'danger',
                )
                return render_template('register/register.html')

            hashed_password = generate_password_hash(password)
            new_user = User(
                name=username, email=email, password_hash=hashed_password
            )  # Правильное присвоение значений экземпляру
            session.add(new_user)
            session.commit()

            flash(
                'Регистрация прошла успешно! Пожалуйста, войдите.', 'success'
            )
            return redirect(url_for('profile.login'))

        except Exception as e:
            session.rollback()
            flash(
                f'An error occurred: {str(e)}', 'danger'
            )  # Show error to user.
            return render_template(
                'register/register.html'
            )  # Return to register page on error

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
    return render_template('register/login.html')


@profile_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


@profile_bp.route('/')
@profile_bp.route('/index')
@profile_bp.route('/other_profile/<int:user_id>')
@login_required
def index(user_id=False):
    session = create_session()
    if not user_id or user_id == current_user.id:
        user_id = current_user.id
        flash('Вы вошли в свой профиль.', 'info')
    user = session.query(User).filter(User.id == user_id).first()
    posts = session.query(Poster).filter(Poster.user_id == user_id)
    subscribes = len(
        list(
            session.query(Subscribes_User).filter(
                Subscribes_User.user_id == user_id
            )
        )
    )
    projects = session.query(Project).filter(Project.user_id == user_id)
    user_subscribe = session.query(Subscribes_User).filter(
        Subscribes_User.user_id == user_id,
        Subscribes_User.subscribes_user_id == int(current_user.id),
    )
    if user_subscribe:
        user_subscribe = user_subscribe.first()
    images = {}
    for post in posts:
        images[post.id] = []
        for image in session.query(ImagePoster).filter(
            ImagePoster.post_id == post.id
        ):
            images[post.id].append(image.image)

    return render_template(
        'profile/profile.html',
        posts=posts,
        projects=projects,
        user=user,
        images=images,
        user_subscribe=user_subscribe,
        subscribes=subscribes,
    )


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
            user = (
                session.query(User).filter(User.id == current_user.id).first()
            )

            user.name = name
            user.surname = surname
            user.age = age
            user.about = about
            user.email = email
            if image_profile:
                if image_profile.filename != '':
                    image_data = image_profile.read()
                    user.image_profile = image_data
            session.commit()
            flash('Профиль успешно обновлен!', 'success')
            return redirect(url_for('index'))
        else:
            flash(
                'Ошибка валидации формы. Проверьте введенные данные.',
                'danger',
            )
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


@profile_bp.route(
    '/add_subscribes_user/<int:user_id>/<int:subscribes_user_id>'
)
def add_subscribes_user(user_id, subscribes_user_id):
    session = create_session()
    subscribes_user = Subscribes_User(
        subscribes_user_id=subscribes_user_id, user_id=user_id
    )
    session.add(subscribes_user)
    session.commit()
    return redirect(request.referrer)


@profile_bp.route('/subscribes/<int:user_id>')
def subscribes(user_id):
    session = create_session()
    subscribes = session.query(Subscribes_User).filter(
        Subscribes_User.user_id == user_id
    )
    users = []
    for subscribe in subscribes:
        users.append(
            session.query(User)
            .filter(User.id == subscribe.subscribes_user_id)
            .first()
        )
        print(users)
    return render_template('profile/subscribes.html', users=users)


@profile_bp.route(
    '/delete_subscribes_user/<int:user_id>/<int:subscribes_user_id>'
)
def delete_subscribes_user(user_id, subscribes_user_id):
    session = create_session()
    subscribes_user = (
        session.query(Subscribes_User)
        .filter(
            Subscribes_User.subscribes_user_id == subscribes_user_id,
            Subscribes_User.user_id == user_id,
        )
        .first()
    )
    session.delete(subscribes_user)
    session.commit()
    return redirect(request.referrer)


def load_photo(image_profile):
    if image_profile:
        filename = secure_filename(image_profile.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        if not os.path.exists('static/media/'):
            os.makedirs('static/media')

        filepath = os.path.join('static/media/', unique_filename)
        image_profile.save(filepath)
        return 'media/' + unique_filename
