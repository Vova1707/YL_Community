from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from db_session import create_session
from models.users import User
from werkzeug.security import check_password_hash, generate_password_hash

project_bp = Blueprint('project', __name__, url_prefix='/project')

@project_bp.route('/<id>')
def open_project(id):
    # Достаём из бд по id нужные данные прооекта в обработчик
    data = {
        "id": id,
        "name": " Имя проекта 1"
    }
    flash(f'Вы вошли в проект.{data["name"]}', 'info')
    return render_template('project.html', **data)