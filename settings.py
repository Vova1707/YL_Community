import os

from dotenv import load_dotenv

def settings(app):
    load_dotenv()
    # HOST и PORT
    app.config['HOST'] = os.environ.get('HOST', '127.0.0.1')
    app.config['PORT'] = int(os.environ.get('PORT', 8086))

    # Основные настройки
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'
    UPLOAD_FOLDER = 'media'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # if app.config['DEBUG']:
        # toolbar = DebugToolbarExtension(app)
        # app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    # Имена баз данных
    db_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db', 'db.sqlite')

    # Путь до базы данных
    app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI', f'{db_file}')

