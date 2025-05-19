from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    abort,
    flash,
    session,
)
from flask_login import LoginManager, current_user
from routes.profile_routes import profile_bp
from routes.blog_routes import blog_bp
from routes.project_routes import project_bp
from routes.rating_routes import rating_bp
from routes.forum_routes import forum_bp

from settings import settings
from db_session import global_init, create_session
from models.users import User
from models.blog import Poster, ImagePoster
import logging
import base64
import os
import uuid
import markdown

import random

app = Flask(__name__)
settings(app)
global_init(app.config['DATABASE_URI'])
app.jinja_env.globals['base64'] = base64



login_manager = LoginManager(app)
login_manager.login_view = 'profile.login'


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.get(User, user_id)


app.register_blueprint(blog_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(project_bp)
app.register_blueprint(rating_bp)
app.register_blueprint(forum_bp)


@app.route('/')
def index():
    settings(app)
    global_init(app.config['DATABASE_URI'])
    news_data = []
    for name_file in ["test_new_1", "test_new_2"]:
        with open(f"static/txt/{name_file}.txt", "r", encoding="utf-8") as f:
            new_data = list(
                map(lambda x: x.split("\n"), f.read().split("\n\n"))
            )
        new_header, new_date = new_data[0][0], new_data[-1][0]
        news_data.append([new_header, new_data, new_date])
    try:
        session = create_session()
        posts = session.query(Poster).all()
    except Exception as e:
        raise Exception(f"{app.config['DATABASE_URI']}")
    images = {}
    for post in posts:
        images[post.id] = []
        for image in session.query(ImagePoster).filter(
            ImagePoster.post_id == post.id
        ):
            images[post.id].append(image.image)
    return render_template(
        'index.html',
        news_data=news_data,
        posts=posts,
        images=images,
        base64=base64,
    )


data_errors = {
    401: {"text": "Неверный логин или пароль", "tags": ["абоба"]},
    403: {
        "text": "Доступ запрещён (Виктор зарещает)",
        "tags": ["наш слоняра"],
    },
    404: {
        "text": "Ой, ой, ой... Страница не найдена",
        "tags": ["договорничок"],
    },
    405: {
        "text": "Нет такого метода запроса (Виктор не даст вам данные!)",
        "tags": ["авава"],
    },
    418: {
        "text": "Хаха, я чайник (Виктор)",
        "tags": ["авава", "абоба", "договорничок", "наш слоняра"],
    },
    500: {
        "text": "У нас сбой (Виктор вас не наругает, вы не виноваты)",
        "tags": ["наш слоняра"],
    },
    502: {"text": "Проблему у нашего сервера", "tags": ["абоба"]},
    503: {
        "text": "Сервис временно недоступен. Виктор пока чинет сайт, подождите",
        "tags": ["договорничок"],
    },
    504: {
        "text": "Запрос обрабатывается слишком долго. Таймаут, Виктор отключил соединение",
        "tags": ["авава"],
    },
}


def error_handlers(app, errors):
    for code, info in errors.items():

        @app.errorhandler(code)
        def error_handle(_, code=code, info=info):
            return (
                render_template(
                    'error.html',
                    code=code,
                    text=info["text"],
                    tags=info["tags"],
                ),
                code,
            )


error_handlers(app, data_errors)


@app.route('/error/<int:code>')
def error(code):
    if code in data_errors.keys():
        abort(code)
    else:
        flash(f'Ошибка с номером {code} не обрабатывается.', 'danger')
        return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html', have_parallax=False)


@app.route('/documentation')
def documentation():
    with open("README.md", "r", encoding="utf-8") as f:
        readme_data = f.read()

    check_label = "## скриншоты"
    ind_check_label = readme_data.lower().find(check_label)
    readme_data = (
        readme_data[:ind_check_label]
        + readme_data[
            ind_check_label
            + len(check_label)
            + readme_data[ind_check_label + len(check_label) :].find("##") :
        ]
    )

    readme_data = markdown.markdown(
        readme_data, extensions=['fenced_code', 'tables']
    )
    style_set = {
        "<p>": "style='font-size: 16px'",
        "<small>": "style='font-size: 14px'",
        "<code>": "style='font-size: 18px'",
        "<h2>": "style='margin-top: 30px;'",
        "<h3>": "style='margin-top: 25px;'",
        "<img>": "style='border-radius: 10px; max-width: 100%; height: auto; display: block;'",
        "<a>": "class='btn-link'",
    }
    for kv in style_set.items():
        readme_data = readme_data.replace(kv[0][:-1], f"{kv[0][:-1]} {kv[1]}")

    return render_template('documentation.html', readme_data=readme_data)


if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG'],
    )
