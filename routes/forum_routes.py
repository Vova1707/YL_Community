from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from db_session import create_session
from models.blog import Poster, ImagePoster, CommentPoster, LikePoster
from forms.blog import BlogForms, CommentForm
from models.users import User

forum_bp = Blueprint('forum', __name__, url_prefix='/blog')

@forum_bp.route('/forum')
@login_required
def forum_view():
    return render_template('forum/forum_view.html')