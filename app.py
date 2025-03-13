from flask import Flask, render_template
from flask_login import LoginManager, current_user
from routes.profile_routes import profile_bp
from routes.blog_routes import blog_bp
from routes.project_routes import project_bp
from routes.rating_score import rating_bp
from settings import settings  # Импортируем settings
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
    return render_template('index.html')

if __name__ == '__main__':
    global_init(app.config['DATABASE_URI'])
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])