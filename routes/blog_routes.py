from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from db_session import create_session
from models.blog import Poster, ImagePoster, CommentPoster, LikePoster
from forms.blog import BlogForms, CommentForm
from models.users import User

blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_blog_post():
    form = BlogForms()
    if request.method == 'POST':
        description = form.description.data
        session = create_session()
        blog_post = Poster(description=description, user_id=current_user.id)
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

    form.description.data = post.description
    return render_template('blog/edit.html', form=form)




@blog_bp.route('/<int:post_id>/delete')
@login_required
def delete(post_id):
    session = create_session()
    post = session.query(Poster).get(post_id)
    for image in session.query(ImagePoster).filter(ImagePoster.post_id == post.id):
        session.delete(image)
    for comment in session.query(CommentPoster).filter(CommentPoster.post_id == post.id):
        session.delete(comment)
    for like in session.query(LikePoster).filter(LikePoster.post_id == post.id):
        session.delete(like)
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
    images = [image.image for image in session.query(ImagePoster).filter(ImagePoster.post_id == post_id)]
    comments = list(session.query(CommentPoster).filter(CommentPoster.post_id == post_id))
    user_comments = list(map(lambda comment: session.query(User).filter(User.id == comment.user_id)[0], comments))
    comments = [{"comment":comments[i], "user":user_comments[i]} for i in range(len(comments))]
    if form.validate_on_submit():
        new_comment = CommentPoster(
            text=form.text.data,
            post_id=poster.id,
            user_id=current_user.id,
        )
        session.add(new_comment)
        session.commit()
    return render_template('blog/poster_detail.html', poster=poster, form=form, images=images, comments=comments)



@blog_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_poster(post_id):
    db_session = create_session()
    try:
        like_user = db_session.query(LikePoster).filter(
            LikePoster.post_id == post_id,
            LikePoster.user_id == current_user.id
        ).first()

        poster = db_session.query(Poster).get(post_id)

        if not poster:
            return jsonify({'error': 'Poster not found'}), 404

        if like_user:
            if like_user.likes == -1:
                poster.dislikes -= 1
                poster.dislikes = max(0, poster.dislikes)
                poster.likes += 1
                like_user.likes = 1
        else:
            likes = LikePoster(post_id=post_id, user_id=current_user.id, likes=1)
            db_session.add(likes)
            poster.likes += 1

        db_session.commit()
        return jsonify({'likes': poster.likes, 'dislikes': poster.dislikes})

    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        db_session.close()


@blog_bp.route('/dislike/<int:post_id>', methods=['POST'])
@login_required
def dislike_poster(post_id):
    db_session = create_session()
    try:
        like_user = db_session.query(LikePoster).filter(
            LikePoster.post_id == post_id,
            LikePoster.user_id == current_user.id
        ).first()

        poster = db_session.query(Poster).get(post_id)

        if not poster:
            return jsonify({'error': 'Poster not found'}), 404

        if like_user:
            if like_user.likes == 1:
                poster.likes -= 1
                poster.likes = max(0, poster.likes)
                poster.dislikes += 1
                like_user.likes = -1
        else:
            likes = LikePoster(post_id=post_id, user_id=current_user.id, likes=-1)
            db_session.add(likes)
            poster.dislikes += 1

        db_session.commit()
        return jsonify({'likes': poster.likes, 'dislikes': poster.dislikes})

    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        db_session.close()


@blog_bp.route('/all', methods=['GET', 'POST'])
def all_blogs():
    session = create_session()
    images = {}
    search_query = request.args.get('search')
    search_type = request.args.get('search_type', 'author')
    posts = []

    if search_query:
        if search_type == 'content':
            posts = session.query(Poster).filter(Poster.description.like(f'%{search_query}%')).all()
        else:
            users = session.query(User).filter(User.name.like(f'%{search_query}%')).all()
            for user in users:
                posts = session.query(Poster).filter(Poster.user_id == user.id)

    for post in posts:
        images[post.id] = []
        for image in session.query(ImagePoster).filter(ImagePoster.post_id == post.id):
            images[post.id].append(image.image)

    return render_template('blog/all.html',
                           posts=posts,
                           images=images,
                           search_query=search_query,
                           search_type=search_type)