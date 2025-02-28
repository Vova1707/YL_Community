from flask import Blueprint, render_template

routes = Blueprint('routes', __name__)


@routes.route('/register')
def register():
    return render_template('index.html')


@routes.route('/login')
def login():
    return render_template('index.html')


@routes.route('/blog/create')
def create_blog_post():
    return render_template('index.html')


@routes.route('/blog/<int:post_id>')
def view_blog_post(post_id):
    post = {
        'id': post_id,
        'title': f'Blog Post {post_id}',
        'content': 'Detailed content of the blog post...',
        'author': 'Some Author',
        'date': '2023-10-27',
    }
    return render_template('index.html', post=post)


@routes.route('/blog/<int:post_id>/edit')
def edit_blog_post(post_id):
    post = {
        'id': post_id,
        'title': f'Blog Post {post_id}',
        'content': 'Detailed content of the blog post...',
        'author': 'Some Author',
        'date': '2023-10-27',
    }
    return render_template('index.html', post=post)


@routes.route('/project/create')
def create_project():
    return render_template('index.html')


@routes.route('/contest/create')
def create_contest():
    return render_template('index.html')
