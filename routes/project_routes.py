import os

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from io import BytesIO
from zipfile import ZipFile
from werkzeug.utils import secure_filename

from db_session import create_session
from models.users import User
from models.projects import Project

from forms.projects import Project_create_form

project_bp = Blueprint('project', __name__, url_prefix='/project')

# def recursive_create_folder_tree(path, flag_folder, file_tree):
#     name, next_path = path.split("/")[0], "/".join(path.split("/")[1:])
#     print(name, next_path, file_tree)
#     if file_tree and name in list(map(lambda x: x["name"], file_tree)):
#         return recursive_create_folder_tree(next_path, flag_folder, list(filter(lambda x: x["name"] == name, file_tree))[0]["children"])
#     else:
#         if flag_folder:
#             file_tree.append({
#                 'name': name,
#                 'type': 'folder',
#                 'children': []
#             })
#         else:
#             file_tree.append({
#                 'name': name,
#                 'type': 'file'
#             })
#         return file_tree
#
# def create_folder_tree(infolist):
#     file_tree = []
#     for info in infolist:
#         path = info.filename
#         print("-" * 20)
#         print("start:", path, file_tree)
#         file_tree = recursive_create_folder_tree("/".join(path.split("/")[:-1]), True if path.split("/")[-1] == "" else True, file_tree)
#         print("end:", path, file_tree)
#         print("-" * 20)
#     return file_tree


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


def create_folder_tree(path, list_name):
    file_tree = []
    print("-"*100)
    if path.split("/")[-1] == "":
        content_dir = list(filter(lambda x: path == "/".join(x.split("/")[:-2]) + "/" and x.split("/")[-2] != "" and x.split("/")[-1] == "", list_name))
        content_file = list(filter(lambda x: path == "/".join(x.split("/")[:-1]) + "/" and x.split("/")[-1] != "", list_name))
    else:
        content_dir = []
        content_file = [path]
    print(path, content_dir, content_file)
    print(list_name)
    print()
    for path_content in content_dir:
        file_tree.append({
            'name': path_content.split("/")[-2],
            'type': 'folder',
            'children': create_folder_tree(path_content, list_name[1:])
        })
    # print("FILE:")
    for path_content in content_file:
        print(path_content)
        file_tree.append({
            'name': path_content.split("/")[-1],
            'type': 'file'
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

    if project.file in [None, "", b""]:
        file_data = None
    else:
        file_data = "*Ссылка на скачивание архив*"
        with ZipFile(BytesIO(project.file)) as zip_file:
            # file_tree = [{'name': 'files', 'type': 'folder', 'children': [{'name': '1', 'type': 'folder', 'children': []}, {'name': '2', 'type': 'folder', 'children': []}, {'name': '3', 'type': 'folder', 'children': [{'name': 'csvs', 'type': 'folder', 'children': [{'name': 'данные.csv', 'type': 'file'}]}, {'name': 'files', 'type': 'folder', 'children': []}, {'name': 'Описание.txt', 'type': 'file'}]}]}]
            # file_tree = create_folder_tree("DEMO-13/", zip_file.namelist())
            file_tree = []
            for name in zip_file.namelist():
                if name.split("/")[-1] == "" and len(name.split("/")) == 2:
                    file_tree.append({
                        'name': name.split("/")[-2],
                        'type': 'folder',
                        "children": create_folder_tree(name, zip_file.namelist())
                    })
                elif name.split("/")[-1] != "" and len(name.split("/")) == 1:
                    file_tree.append({
                        'name': name.split("/")[-1],
                        'type': 'file'
                    })



            # infolists = zip_file.infolist()
            # folder_name = infolists[0].filename.split("/")[-1]
            # for infolist in infolists:
            #     path = infolist.filename
            #     file_name = infolist.filename.split("/")[-1]
            #     if file_name == "": # Папка
            #         file_name = infolist.filename.split("/")[-2]
            #         folder_content = list(filter(lambda x: x.split("/")[-2] == file_name, infolist.filename))
            #     else:
            #         folder_content = []
            #     file_tree.append((infolist.filename))
            #     print(infolist.filename)
                # print((infolist.filename, ))
            # files ['1', '2', '3'] ['1.txt', 'Icon\r']
            # files/1 [] ['Icon\r']
            # files/2 [] ['Icon\r']
            # files/3 ['files'] ['Icon\r', 'Описание.txt']
            # files/3/files ['csvs'] []
            # files/3/files/csvs [] ['Icon\r', 'данные.csv']

            # for root, dirs, files in os.walk(root_dir):
            #     relative_path = os.path.relpath(root, root_dir)
            #     file_tree.append((relative_path, dirs, files))
            # file_tree = {}
            # for path in zip_file.namelist():
            #     names, count_indent = path.split('/')

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
        session = create_session()
        user = session.query(User).get(current_user.id)
        project = Project(title=title, description=description, user_id=current_user.id, file=file.read())
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
        print(form.title.data, project.title)
        print(form.description.data, project.description)
        session.commit()
        return redirect(url_for('project.open_project', id=project.id))
    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        return render_template('project/edit.html', form=form, text_load_file=text_load_file)