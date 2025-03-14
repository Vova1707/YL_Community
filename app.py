from flask import Flask, render_template
from flask_login import LoginManager, current_user
from routes.profile_routes import profile_bp
from routes.blog_routes import blog_bp
from routes.project_routes import project_bp
from routes.rating_score import rating_bp
from settings import settings
from db_session import global_init, create_session
from models.users import User

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


@app.route('/')
def index():
    news_data = []
    for name_file in ["test_new_1", "test_new_2"]:
        with open(f"static/txt/{name_file}.txt", "r", encoding="utf-8") as f:
            new_data = list(map(lambda x: x.split("\n"), f.read().split("\n\n")))
        new_header, new_date = new_data[0][0], new_data[-1][0]
        new_data = new_data[1:-1]
        print(new_header)
        print(new_data)
        print(new_date)
        news_data.append([new_header, new_data, new_date])
    # Дальше будет состовлятся список новостей из отдельной бд
    return render_template('index.html', news_data=news_data)

if __name__ == '__main__':
    global_init(app.config['DATABASE_URI'])
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])