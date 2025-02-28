from flask import Flask, render_template
from routes import routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

app.register_blueprint(routes)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
