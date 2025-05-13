from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    send_file,
)
from flask_login import login_required, current_user

import pandas as pd
from io import BytesIO, StringIO
import rarfile
from rarfile import RarFile
from zipfile import ZipFile, ZIP_DEFLATED
from werkzeug.utils import secure_filename
import pickle

from db_session import create_session
from models.users import User
from models.projects import Project

from forms.projects import (
    Project_create_form,
    Project_set_archive_form,
    Project_set_description_form,
)

SYMBOL_PATH = "|"
rarfile.UNRAR_TOOL = r"static/UnRAR.exe"

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
        content_dir = list(
            filter(
                lambda x: path == "/".join(x.split("/")[:-2]) + "/"
                and x.split("/")[-2] != ""
                and x.split("/")[-1] == "",
                list_name,
            )
        )
        content_file = list(
            filter(
                lambda x: path == "/".join(x.split("/")[:-1]) + "/"
                and x.split("/")[-1] != "",
                list_name,
            )
        )
    else:
        content_dir = []
        content_file = [path]
    # print(path, content_dir, content_file)
    # print(list_name)
    # print()
    for path_content in content_dir:
        file_tree.append(
            {
                'name': path_content.split("/")[-2],
                'type': 'folder',
                'children': create_folder_tree_reverse(
                    path_content, list_name[1:]
                ),
            }
        )
    for path_content in content_file:
        # print(path_content)
        file_tree.append(
            {
                'name': path_content.split("/")[-1],
                'type': 'file',
                'path': path_content.replace("/", SYMBOL_PATH),
            }
        )
    return file_tree


def create_folder_tree(arg, type_arg="byte_code"):
    if type_arg == "byte_code":
        with ZipFile(arg, "r") as zip_file:
            name_list = zip_file.namelist()
    elif type_arg == "name_list":
        name_list = arg

    file_tree = []
    name_list = sorted(
        name_list, key=lambda x: x.split("/")[-1] == "", reverse=True
    )
    for name in name_list:
        if name.split("/")[-1] == "" and len(name.split("/")) == 2:
            file_tree.append(
                {
                    'name': name.split("/")[-2],
                    'type': 'folder',
                    "children": create_folder_tree_reverse(name, name_list),
                }
            )
        elif name.split("/")[-1] != "" and len(name.split("/")) == 1:
            file_tree.append(
                {
                    'name': name.split("/")[-1],
                    'type': 'file',
                    'path': name.replace("/", SYMBOL_PATH),
                }
            )
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
        file_tree = None
    else:
        file_data = "*Ссылка на скачивание архив*"
        file_tree = pickle.loads(project.file_tree)

    flash(f'Вы вошли в проект {project.title}', 'info')
    print(file_tree)
    return render_template(
        'project/view.html',
        name=project.title,
        id=id,
        description=project.description,
        file_data=file_data,
        file_tree=file_tree,
    )


@project_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = Project_create_form()
    if request.method == "POST":
        title = form.title.data
        description = form.description.data
        file = form.file.data
        name = secure_filename(file.filename)
        if name != "":
            if not (
                name
                and name.split(".")[-1] in form.file_extension
                and len(name) > 5
            ):
                flash(
                    f'Недопустимый формат расширения. {form.file_extension_str}',
                    'danger',
                )
                return render_template('project/create.html', form=form)
            type_file = name.split(".")[-1]
            file_read = file.read()
        session = create_session()
        user = session.query(User).get(current_user.id)
        project = Project(
            title=title, description=description, user_id=current_user.id
        )
        if name != "":
            if type_file == "rar":
                res_zip = BytesIO()
                with RarFile(BytesIO(file_read), "r") as rar_file, ZipFile(
                    res_zip, 'w'
                ) as zip_file:
                    name_list = rar_file.namelist()
                    print("BASE 1", name_list)
                    for rar_info in rar_file.infolist():
                        # print(rar_info.filename, end=" ")
                        # print(rar_info.filename.split("/"))
                        if rar_info.filename.split("/")[-1] != "":
                            with rar_file.open(rar_info.filename) as f:
                                zip_file.writestr(rar_info.filename, f.read())
                file_read = res_zip.getvalue()
                file_tree = pickle.dumps(
                    create_folder_tree(name_list, type_arg="name_list")
                )
            elif type_file == "zip":
                file_tree = pickle.dumps(
                    create_folder_tree(BytesIO(file_read))
                )
            project.file = file_read
            project.file_tree = file_tree
            # project.type_file = type_file
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

        file = form.file.data
        name = secure_filename(file.filename)
        if name != "":
            file_read = file.read()
            if file_read not in [None, "", b""]:
                name = secure_filename(name)
                if not (
                    name
                    and name.split(".")[-1] in form.file_extension
                    and len(name) > 5
                ):
                    flash(
                        f'Недопустимый формат расширения. {form.file_extension_str}',
                        'danger',
                    )
                    return render_template(
                        'project/edit.html',
                        form=form,
                        text_load_file=text_load_file,
                    )
                project.file = file_read
            project.file_tree = pickle.dumps(
                create_folder_tree(BytesIO(file_read))
            )

        session.commit()
        return redirect(url_for('project.open_project', id=project.id))
    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        return render_template(
            'project/edit.html', form=form, text_load_file=text_load_file
        )


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


@project_bp.route('/<int:id>/delete_archive')
@login_required
def delete_archive(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден.', 'danger')
        return redirect(url_for('profile.index'))
    project.file = None
    session.commit()
    return redirect(url_for('project.open_project', id=id))


@project_bp.route('/<int:id>/set_archive', methods=['GET', 'POST'])
@login_required
def set_archive(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден', 'danger')
        return redirect(url_for('index'))

    if project.file:
        text_load_file = "Архив загружался ранее"
    else:
        text_load_file = "Архив не загружался ранее"
    form = Project_set_archive_form()
    if request.method == 'POST':
        file = form.file.data
        name = secure_filename(file.filename)
        if name != "":
            file_read = file.read()
            if file_read not in [None, "", b""]:
                name = secure_filename(name)
                if not (
                    name
                    and name.split(".")[-1] in form.file_extension
                    and len(name) > 5
                ):
                    flash(
                        f'Недопустимый формат расширения. {form.file_extension_str}',
                        'danger',
                    )
                    return render_template(
                        'project/edit.html',
                        form=form,
                        text_load_file=text_load_file,
                    )
                project.file = file_read
            project.file_tree = pickle.dumps(
                create_folder_tree(BytesIO(file_read))
            )
        session.commit()
        return redirect(url_for('project.open_project', id=id))
    elif request.method == 'GET':
        return render_template(
            'project/set_archive.html',
            form=form,
            text_load_file=text_load_file,
            project_title=project.title,
            project_id=id,
        )


@project_bp.route('/<int:id>/download_archive')
def download_archive(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден', 'danger')
        return redirect(url_for('index'))

    replace_elements = {" ": "_"}
    for k in ["\\", "/", ":", "*", "?", '"', ">", "<", "|"]:
        replace_elements[k] = "#"
    file_name = project.title
    for k, v in replace_elements.items():
        file_name = file_name.replace(k, v)
    file_name = file_name.strip().lower() + ".zip"

    return send_file(
        BytesIO(project.file),
        as_attachment=True,
        download_name=file_name,
        mimetype='application/octet-stream',
    )


@project_bp.route('/<int:id>/set_description', methods=['GET', 'POST'])
@login_required
def set_description(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден', 'danger')
        return redirect(url_for('index'))

    form = Project_set_description_form()
    if request.method == 'POST':
        project.description = form.description.data
        session.commit()
        return redirect(url_for('project.open_project', id=id))
    elif request.method == 'GET':
        form.description.data = project.description
        return render_template(
            'project/set_description.html',
            form=form,
            project_title=project.title,
            project_id=id,
        )


@project_bp.route('/<int:id>/delete_description')
@login_required
def delete_description(id):
    session = create_session()
    project = session.query(Project).get(id)
    if not project:
        flash('Проект не найден', 'danger')
        return redirect(url_for('index'))

    project.description = ""
    session.commit()
    return redirect(url_for('project.open_project', id=id))


def get_csv_data(data, delimiter):
    table_data = pd.read_csv(data, sep=delimiter)
    header = [table_data.index.name or "№"] + table_data.columns.tolist()
    table_data = table_data.values.tolist()
    table_data = [[i] + table_data[i] for i in range(len(table_data))]
    table_data = [header] + table_data
    return table_data


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
        with zip_file.open(path, "r") as file:
            file_data = file.read()
    if path.split(".")[-1] in [
        "png",
        "jpg",
        "jpeg",
        "bmp",
        "gif",
        "tif",
        "tiff",
        "webp",
        "heic",
        "heif",
        "ico",
        "dds",
        "raw",
        "exr",
        "svg",
        "eps",
        "ai",
    ]:
        file_type = "img"
    elif path.split(".")[-1] in ["csv"]:
        file_type = "csv"
        file_data = [
            request.args.get("delimiter", ";"),
            StringIO(file_data.decode("utf-8")),
        ]
        file_data[1] = get_csv_data(file_data[1], file_data[0])
    else:
        try:
            file_data = file_data.decode("utf-8")
            file_type = "code"
        except UnicodeDecodeError:
            file_type = None
    return render_template(
        'project/file_view.html',
        name_project=project.title,
        file_tree=pickle.loads(project.file_tree),
        id=id_project,
        path=path.replace('/', SYMBOL_PATH),
        orig_path=path,
        file_data=file_data,
        file_type=file_type,
        name_file=path.split("/")[-1],
    )


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

    project.file = res_zip.getvalue()
    project.file_tree = pickle.dumps(
        create_folder_tree(BytesIO(project.file))
    )
    session.commit()

    return redirect(url_for('project.open_project', id=id_project))


@project_bp.route('<int:id_project>/file/save/<string:path>')
@login_required
def save_file(id_project, path):
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

    project.file = res_zip.getvalue()
    with ZipFile(BytesIO(project.file), 'r') as zip_file:
        print("BASE 2", zip_file.namelist())

    project.file_tree = pickle.dumps(
        create_folder_tree(BytesIO(project.file))
    )
    session.commit()

    return redirect(
        url_for(
            'project.open_file',
            id_project=id_project,
            path=path.replace("/", SYMBOL_PATH),
        )
    )


@project_bp.route('<int:id_project>/file/rename/<string:path>')
@login_required
def rename_file(id_project, path):
    session = create_session()
    project = session.query(Project).get(id_project)
    if not project:
        flash('Проект не найден.', 'danger')
        return redirect(url_for('profile.index'))
    path = path.replace(SYMBOL_PATH, '/')

    new_name = request.args.get('new_name')
    new_name = path.split("/")[-1] if new_name == "" else new_name
    new_name += (
        "." + path.split("/")[-1].split(".")[-1]
        if "." not in new_name
        else ""
    )
    res_zip = BytesIO()
    new_path = None
    with ZipFile(BytesIO(project.file), 'r') as start_zip_file:
        # print("start:", start_zip_file.namelist())
        with ZipFile(res_zip, 'w', ZIP_DEFLATED) as res_zip_file:
            for item in start_zip_file.infolist():
                # print(item.filename)
                with start_zip_file.open(item.filename, 'r') as file:
                    if item.filename == path:
                        new_path = "/".join(
                            item.filename.split("/")[:-1] + [new_name]
                        )
                        res_zip_file.writestr(new_path, file.read())
                    else:
                        res_zip_file.writestr(item, file.read())
            # print("- " * 50)
    new_path = path if new_path is None else new_path

    project.file = res_zip.getvalue()
    project.file_tree = pickle.dumps(
        create_folder_tree(BytesIO(project.file))
    )
    session.commit()

    return redirect(
        url_for(
            'project.open_file',
            id_project=id_project,
            path=new_path.replace("/", SYMBOL_PATH),
        )
    )
