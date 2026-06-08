from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
from dotenv import load_dotenv
import os
import shutil
import uuid

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError('SECRET_KEY environment variable is required.')

database_path = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'database.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + database_path
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024 * 1024))
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=int(os.environ.get('REMEMBER_COOKIE_DAYS', 30)))

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))

class UploadTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class FileVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('upload_task.id'))
    version_name = db.Column(db.String(100))
    changelog = db.Column(db.Text)
    filename = db.Column(db.String(255))
    stored_filename = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())



def save_task_files(task_id, version_names, changelogs, files):
    task_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'task_{task_id}')
    os.makedirs(task_folder, exist_ok=True)

    saved_count = 0
    for idx, uploaded_file in enumerate(files):
        if not uploaded_file or not uploaded_file.filename:
            continue

        original_filename = secure_filename(uploaded_file.filename)
        unique_name = str(uuid.uuid4()) + "_" + original_filename
        save_path = os.path.join(task_folder, unique_name)
        uploaded_file.save(save_path)

        version = FileVersion(
            task_id=task_id,
            version_name=version_names[idx] if idx < len(version_names) else '',
            changelog=changelogs[idx] if idx < len(changelogs) else '',
            filename=original_filename,
            stored_filename=unique_name
        )
        db.session.add(version)
        saved_count += 1

    return saved_count

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/init')
def init():
    db.create_all()

    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_username or not admin_password:
        return '请先设置 ADMIN_USERNAME 和 ADMIN_PASSWORD 环境变量。', 500

    if not User.query.filter_by(username=admin_username).first():
        user = User(
            username=admin_username,
            password_hash=generate_password_hash(admin_password)
        )
        db.session.add(user)
        db.session.commit()

    return '初始化完成。'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for('index'))

        flash('用户名或密码错误')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    tasks = UploadTask.query.order_by(UploadTask.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/task/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        task = UploadTask(
            title=title,
            description=description
        )

        db.session.add(task)
        db.session.commit()

        version_names = request.form.getlist('version_name')
        changelogs = request.form.getlist('changelog')
        files = request.files.getlist('file')

        save_task_files(task.id, version_names, changelogs, files)
        db.session.commit()

        return redirect(url_for('task_detail', task_id=task.id))

    return render_template('create_task.html')

@app.route('/task/<int:task_id>')
@login_required
def task_detail(task_id):
    task = UploadTask.query.get_or_404(task_id)
    versions = FileVersion.query.filter_by(task_id=task.id).order_by(FileVersion.uploaded_at.desc()).all()

    return render_template(
        'task_detail.html',
        task=task,
        versions=versions
    )


@app.route('/task/<int:task_id>/files', methods=['POST'])
@login_required
def add_task_files(task_id):
    task = UploadTask.query.get_or_404(task_id)
    version_names = request.form.getlist('version_name')
    changelogs = request.form.getlist('changelog')
    files = request.files.getlist('file')

    saved_count = save_task_files(task.id, version_names, changelogs, files)
    if saved_count == 0:
        flash('请选择至少一个文件')
    else:
        db.session.commit()
        flash(f'已上传 {saved_count} 个文件')

    return redirect(url_for('task_detail', task_id=task.id))

@app.route('/task/<int:task_id>/description', methods=['POST'])
@login_required
def add_task_description(task_id):
    task = UploadTask.query.get_or_404(task_id)
    extra_description = request.form.get('extra_description', '').strip()

    if not extra_description:
        flash('请填写要补充的说明')
        return redirect(url_for('task_detail', task_id=task.id))

    if task.description:
        task.description = task.description.rstrip() + '\n\n' + extra_description
    else:
        task.description = extra_description

    db.session.commit()
    flash('说明已更新')
    return redirect(url_for('task_detail', task_id=task.id))

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = UploadTask.query.get_or_404(task_id)
    task_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'task_{task.id}')

    FileVersion.query.filter_by(task_id=task.id).delete()
    db.session.delete(task)
    if os.path.isdir(task_folder):
        shutil.rmtree(task_folder)

    db.session.commit()
    flash('任务已删除')
    return redirect(url_for('index'))

@app.route('/download/<int:version_id>')
@login_required
def download(version_id):
    version = FileVersion.query.get_or_404(version_id)

    folder = os.path.join(app.config['UPLOAD_FOLDER'], f'task_{version.task_id}')
    filepath = os.path.join(folder, version.stored_filename)

    return send_file(
        filepath,
        as_attachment=True,
        download_name=version.filename
    )

if __name__ == '__main__':
    app.run(
        host=os.environ.get('HOST', '127.0.0.1'),
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    )