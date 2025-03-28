from flask import Flask, render_template, redirect, url_for, request, abort, flash, session
from flask_login import LoginManager, current_user
from routes.profile_routes import profile_bp
from routes.blog_routes import blog_bp
from routes.project_routes import project_bp
from routes.rating_routes import rating_bp

from settings import settings
from db_session import global_init, create_session
from models.users import User
from models.blog import Poster

import base64
import os
import uuid

import random

app = Flask(__name__)
settings(app)

login_manager = LoginManager(app)
login_manager.login_view = 'profile.login'

@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)

app.register_blueprint(blog_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(project_bp)
app.register_blueprint(rating_bp)

theme = "light"

def random_wallpaper_img():
    coords = [[]]
    paths = ["img/wallpaper_1.png", "img/wallpaper_2.png"]
    sizes = [(200, 200), (150, 150)]
    wallpaper_imgs = []
    for i in range(5):
        random_coord, random_ind_img = random.choice(coords), random.choice(paths)
        wallpaper_imgs.append({
            "coord": random_coord,
            "path": paths[random_ind_img],
            "size": sizes[random_ind_img]
        })
    return wallpaper_imgs

@app.route('/')
def index():
    news_data = []
    for name_file in ["test_new_1", "test_new_2"]:
        with open(f"static/txt/{name_file}.txt", "r", encoding="utf-8") as f:
            new_data = list(map(lambda x: x.split("\n"), f.read().split("\n\n")))
        new_header, new_date = new_data[0][0], new_data[-1][0]
        news_data.append([new_header, new_data, new_date])
    session = create_session()
    posts = session.query(Poster).all()
    return render_template('index.html', news_data=news_data, posts=posts)


data_errors = {
    401: {
        "text": "Неверный логин или пароль",
        "tags": ["абоба"]
    },
    403: {
        "text": "Доступ запрещён (Виктор зарещает)",
        "tags": ["наш слоняра"]
    },
    404: {
        "text": "Ой, ой, ой... Страница не найдена",
        "tags": ["договорничок"]
    },
    405: {
        "text": "Нет такого метода запроса (Виктор не даст вам данные!)",
        "tags": ["авава"]
    },
    418: {
        "text": "Хаха, я чайник (Виктор)",
        "tags": ["авава", "абоба", "договорничок", "наш слоняра"]
    },
    500: {
        "text": "У нас сбой (Виктор вас не наругает, вы не виноваты)",
        "tags": ["наш слоняра"]
    },
    502: {
        "text": "Проблему у нашего сервера",
        "tags": ["абоба"]
    },
    503: {
        "text": "Сервис временно недоступен. Виктор пока чинет сайт, подождите",
        "tags": ["договорничок"]
    },
    504: {
        "text": "Запрос обрабатывается слишком долго. Таймаут, Виктор отключил соединение",
        "tags": ["авава"]
    },
}
def error_handlers(app, errors):
    for code, info in errors.items():
        @app.errorhandler(code)
        def error_handle(_, code=code, info=info):
            return render_template('error.html', code=code, text=info["text"], tags=info["tags"]), code
error_handlers(app, data_errors)


@app.route('/error/<int:code>')
def error(code):
    if code in data_errors.keys():
        abort(code)
    else:
        flash(f'Ошибка с номером {code} не обрабатывается.', 'danger')
        return redirect('/')


if __name__ == '__main__':
    app.jinja_env.globals['base64'] = base64
    global_init(app.config['DATABASE_URI'])
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])