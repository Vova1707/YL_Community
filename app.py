from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, current_user
from routes.profile_routes import profile_bp
from routes.blog_routes import blog_bp
from routes.project_routes import project_bp
from routes.rating_score import rating_bp
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

@app.context_processor
def utility_change_theme():
    return dict(change_theme=change_theme)

def change_theme():
    global theme
    if theme == "light":
        theme = "dark"
    else:
        theme = "light"
    print(theme)
    # print(request.url)
    # print(request.path)
    # print(request)
    # return redirect(request.args.get("current_page"))
    # print(current_page)
    print(request.url)
    # return redirect(url_for('index'))
    return ""


if __name__ == '__main__':
    app.jinja_env.globals['base64'] = base64
    global_init(app.config['DATABASE_URI'])
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])