from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from db_session import create_session
from models.users import User
from werkzeug.security import check_password_hash, generate_password_hash

rating_bp = Blueprint('rating', __name__, url_prefix='/rating')

@rating_bp.route('/')
@rating_bp.route('/index')
def index():
    flash('Рейтинг участников', 'info')
    return render_template('rating.html')