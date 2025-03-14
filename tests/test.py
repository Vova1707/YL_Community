from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('test.html')

if __name__ == '__main__':
    app.config['HOST'] = os.environ.get('HOST', '127.0.0.1')
    app.config['PORT'] = int(os.environ.get('PORT', 8086))
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])

# <!doctype html>
# <html lang="ru">
#   <head>
#     <meta charset="utf-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1">
#     <title>Bootstrap demo</title>
#     <link rel="stylesheet"
#           href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
#           integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh"
#           crossorigin="anonymous">
#       <!-- <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap.min.css') }}"> -->
#   </head>
#   <body>
#     <h1>Hello, world!</h1>
#   </body>
# </html>