from flask import Flask, render_template, make_response, jsonify, request, url_for, flash
from werkzeug.utils import redirect, secure_filename
from data import db_session
from data.posts import Post
from data.users import User
from forms.login import LoginForm
from forms.register import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from api import users_api
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index_auth.html', title='Казино')
    else:
        return render_template('index.html', title='Казино')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.balance(100)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/game 1', methods=['GET', 'POST'])
def game_1():
    return render_template("Game 1.html")


@app.route('/game 2', methods=['GET', 'POST'])
def game_2():
    return render_template("Game 2.html")


@app.route('/game 3', methods=['GET', 'POST'])
def game_3():
    return render_template("Game 3.html")


@app.route('/user_profil', methods=['GET', 'POST'])
def user_profile():
    if request.method == 'POST':
        if 'profile_picture' not in request.files:
            return redirect(request.url)

        uploaded_file = request.files['profile_picture']
        if uploaded_file.filename != '':
            filename = 'avatar.' + ".".join(uploaded_file.filename.split('.')[1:])
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            return redirect('/user_profil')
    if os.path.exists(url_for('static', filename='uploads/avatar.png')[1:]):
        filename = 'uploads/avatar.png'
        return render_template('profil.html', filename=filename)
    else:
        return render_template('profil.html')


@app.route('/upload_image', methods=['POST'])
def upload_image():
    print(1212)
    if 'file' not in request.files:
        flash('Нету картинки')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Картинка не выбрана')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('upload_image filename: ' + filename)
        flash('Картинка успешно загруженна на сервер')
        return render_template('profil.html', filename=filename)
    else:
        flash('Нужно загрузить картинку в формотах - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>', methods=['POST'])
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


# profile_picture_url = request.args.get('profile_picture_url')
# return render_template('profil.html', profile_picture_url=profile_picture_url)
@app.route('/upload-my-image', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(ABSOLUTE_PATH_TO_YOUR_FOLDER, filename))
        new_image = Image(
            path=PATH_TO_YOUR_FOLDER,
            filename=filename,
            ext=filename.rsplit('.', 1)[1].lower()
        )


@app.route('/balance', methods=['GET', 'POST'])
def balance():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email).first()
    a = user.balance
    return render_template('balance.html', bal=a)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@app.errorhandler(401)
def bad_request(_):
    return make_response(jsonify({'error': 'Not access'}), 401)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    db_session.global_init("blogs.db")
    #
    # db_sess = db_session.create_session()
    # post = db_sess.query(Post).filter(Post.id == 1).first()
    # if not post:
    #     post = Post()
    #     post.id = 1
    #     post.name = 'Администратор'
    #     db_sess.add(post)
    #     db_sess.commit()
    #
    # post = db_sess.query(Post).filter(Post.id == 2).first()
    # if not post:
    #     post = Post()
    #     post.id = 2
    #     post.name = 'Модератор'
    #     db_sess.add(post)
    #     db_sess.commit()
    #
    # post = db_sess.query(Post).filter(Post.id == 3).first()
    # if not post:
    #     post = Post()
    #     post.id = 3
    #     post.name = 'Пользователь'
    #     db_sess.add(post)
    #     db_sess.commit()
    #
    # user = db_sess.query(User).filter(User.email == 'admin@mail.ru').first()
    # if not user:
    #     user = User()
    #     user.email = 'admin@mail.ru'
    #     user.name = 'admin'
    #     user.post_id = 1
    #     user.set_password('admin')
    #     db_sess.add(user)
    #     db_sess.commit()
    #
    # app.register_blueprint(users_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
