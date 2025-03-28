from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from db_session import create_session
from models.blog import Poster, ImagePoster
from models.users import User
from forms.blog import BlogForms

blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_blog_post():
    form = BlogForms()
    if request.method == 'POST':
        title = form.title.data
        description = form.description.data
        session = create_session()
        blog_post = Poster(title=title, description=description, user_id=current_user.id)
        session.add(blog_post)
        session.commit()
        images = form.images.data
        session = create_session()
        for image in images:
            blog_post = max(session.query(Poster).all(), key=lambda s: s.id)
            if image:
                if image.filename != '':
                    image_data = image.read()
                    image = ImagePoster(image=image_data, post_id=blog_post.id)
                    image.post_id = blog_post.id
                    session.add(image)
        session.commit()
        # print(session.query(ImagePoster).filter(ImagePoster.post_id == blog_post.id).first())
        return redirect(url_for('profile.index'))

    return render_template('blog/create.html', form=form)

@blog_bp.route('/<int:post_id>')
@login_required
def view_blog_post(post_id):
    session = create_session()
    post = session.query(Poster).get(post_id)
    if not post:
        flash('Запись не найдена.', 'danger')
        return redirect(url_for('profile.index'))

    return render_template('blog/view.html', post=post)

@blog_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog_post(post_id):
    session = create_session()
    post = session.query(Poster).get(post_id)
    if not post:
        flash('Запись не найдена.', 'danger')
        return redirect(url_for('profile.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if title and content:
            post.title = title
            post.content = content
            session.commit()
            flash('Запись успешно обновлена!', 'success')
            return redirect(url_for('profile.index'))
        else:
            flash('Заголовок и содержимое обязательны.', 'danger')

    return render_template('blog/edit.html', post=post)

@blog_bp.route('/<int:post_id>/delete')
@login_required
def delete(post_id):
    session = create_session()
    post = session.query(Poster).get(post_id)
    for image in session.query(ImagePoster).filter(ImagePoster.post_id == post.id):
        session.delete(image)
    if not post:
        flash('Запись не найдена.', 'danger')
        return redirect(url_for('profile.index'))
    session.delete(post)
    session.commit()
    return redirect(url_for('profile.index'))


@blog_bp.route('/all')
@login_required
def all_blogs():
    session = create_session()
    posts = session.query(Poster).all()

    return render_template('blog/all.html', posts=posts)