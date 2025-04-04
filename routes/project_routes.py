import os
import base64

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from werkzeug.utils import secure_filename
import pickle

from db_session import create_session
from models.users import User
from models.projects import Project

from forms.projects import Project_create_form

SYMBOL_PATH = "|"

project_bp = Blueprint('project', __name__, url_prefix='/project')

# def create_folder_tree(root_dir):
#     file_tree = []
#     for entry in os.scandir(root_dir):
#         if entry.is_dir():
#             file_tree.append({
#                 'name': entry.name,
#                 'type': 'folder',
#                 'children': create_folder_tree(entry.path)
#             })
#         else:
#             file_tree.append({
#                 'name': entry.name,
#                 'type': 'file'
#             })
#     return file_tree


def create_folder_tree_reverse(path, list_name):
    file_tree = []
    # print("-"*100)
    if path.split("/")[-1] == "":
        content_dir = list(filter(lambda x: path == "/".join(x.split("/")[:-2]) + "/" and x.split("/")[-2] != "" and x.split("/")[-1] == "", list_name))
        content_file = list(filter(lambda x: path == "/".join(x.split("/")[:-1]) + "/" and x.split("/")[-1] != "", list_name))
    else:
        content_dir = []
        content_file = [path]
    # print(path, content_dir, content_file)
    # print(list_name)
    # print()
    for path_content in content_dir:
        file_tree.append({
            'name': path_content.split("/")[-2],
            'type': 'folder',
            'children': create_folder_tree_reverse(path_content, list_name[1:])
        })
    for path_content in content_file:
        # print(path_content)
        file_tree.append({
            'name': path_content.split("/")[-1],
            'type': 'file',
            'path': path_content.replace("/", SYMBOL_PATH)
        })
    return file_tree

def create_folder_tree(byte_code):
    with ZipFile(byte_code) as zip_file:
        # file_tree = [{'name': 'files', 'type': 'folder', 'children': [{'name': '1', 'type': 'folder', 'children': []}, {'name': '2', 'type': 'folder', 'children': []}, {'name': '3', 'type': 'folder', 'children': [{'name': 'csvs', 'type': 'folder', 'children': [{'name': 'данные.csv', 'type': 'file'}]}, {'name': 'files', 'type': 'folder', 'children': []}, {'name': 'Описание.txt', 'type': 'file'}]}]}]
        # file_tree = create_folder_tree("DEMO-13/", zip_file.namelist())
        file_tree = []
        for name in zip_file.namelist():
            if name.split("/")[-1] == "" and len(name.split("/")) == 2:
                file_tree.append({
                    'name': name.split("/")[-2],
                    'type': 'folder',
                    "children": create_folder_tree_reverse(name, zip_file.namelist())
                })
            elif name.split("/")[-1] != "" and len(name.split("/")) == 1:
                file_tree.append({
                    'name': name.split("/")[-1],
                    'type': 'file',
                    'path': name.replace("/", SYMBOL_PATH)
                })
    return file_tree


@project_bp.route('/<id>')
@login_required
def open_project(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден.', 'danger')
        return redirect(url_for('index'))

    file_tree = pickle.loads(project.file_tree)
    if project.file in [None, "", b""]:
        file_data = None
    else:
        file_data = "*Ссылка на скачивание архив*"

    flash(f'Вы вошли в проект {project.title}', 'info')
    return render_template('project/view.html', name=project.title, id=id, description=project.description, file_data=file_data, file_tree=file_tree)

@project_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = Project_create_form()
    if request.method == "POST":
        title = form.title.data
        description = form.description.data
        file = form.file.data
        name = secure_filename(file.filename)
        if not(name and name.split(".")[-1] in form.file_extension and len(name) > 5):
            flash(f'Недопустимый формат расширения. {form.file_extension_str}', 'danger')
            return render_template('project/create.html', form=form)
        file_read = file.read()
        file_tree = pickle.dumps(create_folder_tree(BytesIO(file_read)))
        session = create_session()
        user = session.query(User).get(current_user.id)
        project = Project(title=title, description=description, user_id=current_user.id, file=file_read, file_tree=file_tree)
        project.author = user
        session.add(project)
        session.commit()

        return redirect(url_for('project.open_project', id=project.id))
    elif request.method == "GET":
        return render_template('project/create.html', form=form)

@project_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден', 'danger')
        return redirect(url_for('index'))

    if project.file:
        text_load_file = "Архив загружался ранее"
    else:
        text_load_file = "Архив не загружался ранее"
    form = Project_create_form()
    if request.method == 'POST':
        project.title = form.title.data
        project.description = form.description.data
        file_data = form.file.data
        file_read = file_data.read()
        if file_read not in [None, "", b""]:
            name = secure_filename(file_data.filename)
            if not (name and name.split(".")[-1] in form.file_extension and len(name) > 5):
                flash(f'Недопустимый формат расширения. {form.file_extension_str}', 'danger')
                return render_template('project/edit.html', form=form, text_load_file=text_load_file)
            project.file = file_read
        project.file_tree = pickle.dumps(create_folder_tree(BytesIO(file_read)))
        session.commit()
        return redirect(url_for('project.open_project', id=project.id))
    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        return render_template('project/edit.html', form=form, text_load_file=text_load_file)

@project_bp.route('/<int:id>/delete')
@login_required
def delete_project(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден.', 'danger')
        return redirect(url_for('profile.index'))
    session.delete(project)
    session.commit()
    return redirect(url_for('profile.index'))

@project_bp.route('<int:id_project>/file/<string:path>')
@login_required
def open_file(id_project, path):
    session = create_session()
    project = session.query(Project).get(id_project)
    if not project:
        flash('Проект не найден.', 'danger')
        return redirect(url_for('profile.index'))

    path = path.replace(SYMBOL_PATH, '/')

    with ZipFile(BytesIO(project.file)) as zip_file:
        with zip_file.open(path, 'r') as file:
            file_data = file.read() # base64.b64encode(file.read()).decode('utf-8')
            if path.split(".")[-1] in ["png", "jpg", "jpeg", "bmp", "gif", "tif", "tiff", "webp", "heic", "heif", "ico", "dds", "raw", "exr", "svg", "eps", "ai"]:
                file_type = "img"
            else:
                try:
                    file_data = file.read().decode("utf-8")
                    file_type = "code"
                except UnicodeDecodeError:
                    file_type = None
    return render_template('project/file_view.html',
                           name_project=project.title, file_tree=pickle.loads(project.file_tree), id=id_project,
                           path=path.replace('/', SYMBOL_PATH), orig_path=path, file_data=file_data, file_type=file_type)

@project_bp.route('<int:id_project>/file/delete/<string:path>')
@login_required
def delete_file(id_project, path):
    session = create_session()
    project = session.query(Project).get(id_project)
    if not project:
        flash('Проект не найден.', 'danger')
        return redirect(url_for('profile.index'))
    path = path.replace(SYMBOL_PATH, '/')

    res_zip = BytesIO()
    # print(path)
    with ZipFile(BytesIO(project.file), 'r') as start_zip_file:
        # print("start:", start_zip_file.namelist())
        with ZipFile(res_zip, 'w', ZIP_DEFLATED) as res_zip_file:
            for item in start_zip_file.infolist():
                # print(item.filename)
                with start_zip_file.open(item.filename, 'r') as file:
                    if item.filename != path:
                        res_zip_file.writestr(item, file.read())
            # print("- " * 50)

    project.file = res_zip.getvalue()
    project.file_tree = pickle.dumps(create_folder_tree(BytesIO(project.file)))
    session.commit()

    return redirect(url_for('project.open_project', id=id_project))

@project_bp.route('<int:id_project>/file/save/<string:path>')
@login_required
def save_file(id_project, path):
    print("SAVE FILE")
    new_data = request.args.get("new_data", "")
    session = create_session()
    project = session.query(Project).get(id_project)
    if not project:
        flash('Проект не найден.', 'danger')
        return redirect(url_for('profile.index'))
    path = path.replace(SYMBOL_PATH, '/')

    res_zip = BytesIO()
    with ZipFile(BytesIO(project.file), 'r') as start_zip_file:
        with ZipFile(res_zip, 'w', ZIP_DEFLATED) as res_zip_file:
            for item in start_zip_file.infolist():
                with start_zip_file.open(item.filename, 'r') as file:
                    if item.filename == path:
                        res_zip_file.writestr(path, new_data)
                    else:
                        res_zip_file.writestr(item, file.read())

    with ZipFile(res_zip, 'r') as check_file:
        with check_file.open(path, 'r') as file:
            print(file.read())

    project.file = res_zip.getvalue()
    project.file_tree = pickle.dumps(create_folder_tree(BytesIO(project.file)))
    session.commit()

    return redirect(url_for('project.open_file', id_project=id_project, path=path.replace("/", SYMBOL_PATH)))