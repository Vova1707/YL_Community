from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from db_session import create_session
from models.blog import Poster, ImagePoster, CommentPoster, LikePoster
from forms.blog import BlogForms, CommentForm

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
    form = BlogForms()
    session = create_session()
    post = session.query(Poster).get(post_id)

    if not post:
        flash('Запись не найдена.', 'danger')
        return redirect(url_for('profile.index'))

    list_of_image = [0] * 3
    for index, image in enumerate(session.query(ImagePoster).filter(ImagePoster.post_id == post_id)):
        list_of_image[index] = image

    if request.method == 'POST':

        post.title = form.title.data
        post.description = form.description.data
        images = form.images.data

        for index, image_form in enumerate(images):
            if image_form:
                image_data = image_form.read()
                if list_of_image[index] != 0:
                    list_of_image[index].image = image_data
                else:
                    image = ImagePoster(image=image_data, post_id=post_id)
                    image.post_id = post_id
                    session.add(image)
            else:
                if list_of_image[index] != 0:
                    session.delete(list_of_image[index])
        session.commit()
        return redirect(url_for('profile.index'))

    form.title.data = post.title
    form.description.data = post.description
    return render_template('blog/edit.html', form=form)




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


@blog_bp.route('/post_detail/<int:post_id>', methods=['GET', 'POST'])
def poster_detail(post_id):
    form = CommentForm()
    session = create_session()
    poster = session.query(Poster).get(post_id)
    images = session.query(ImagePoster).filter(ImagePoster.post_id == post_id)
    comments = session.query(CommentPoster).filter(CommentPoster.post_id == post_id)
    if form.validate_on_submit():
        new_comment = CommentPoster(
            text=form.text.data,
            post_id=poster.id,
            user_id=current_user.id,
        )
        session.add(new_comment)
        session.commit()
    return render_template('blog/poster_detail.html', poster=poster, form=form, images=images, comments=comments)



@blog_bp.route('like/<int:post_id>', methods=['POST'])
@login_required
def like_poster(post_id):
    session = create_session()
    like_user = session.query(LikePoster).filter(LikePoster.post_id == post_id, LikePoster.user_id==current_user.id).first()
    poster = session.query(Poster).get(post_id)
    if like_user:
        print('Лайк', like_user.likes)
        if like_user.likes == -1:
            poster.dislikes -= 1
            poster.likes += 1
            like_user.likes = 1
    else:
        likes = LikePoster(post_id=post_id, user_id=current_user.id, likes=1)
        session.add(likes)
        poster.likes += 1
    session.commit()
    print('Лайки поста:', poster.likes, 'Дизлайки поста', poster.dislikes)
    return redirect(url_for('blog.poster_detail', post_id=post_id))


@blog_bp.route('dislike/<int:post_id>', methods=['POST'])
@login_required
def dislike_poster(post_id):
    session = create_session()
    like_user = session.query(LikePoster).filter(LikePoster.post_id == post_id, LikePoster.user_id==current_user.id).first()
    poster = session.query(Poster).get(post_id)
    if like_user:
        print('Лайк', like_user.likes)
        if like_user.likes == 1:
            poster.likes -= 1
            poster.dislikes += 1
            like_user.likes = -1
    else:
        likes = LikePoster(post_id=post_id, user_id=current_user.id, likes=-1)
        session.add(likes)
        poster.dislikes += 1
    session.commit()
    print('Лайки поста:', poster.likes, 'Дизлайки поста', poster.dislikes)
    return redirect(url_for('blog.poster_detail', post_id=post_id))


@login_required
def all_blogs():
    session = create_session()
    posts = session.query(Poster).all()

    return render_template('blog/all.html', posts=posts)