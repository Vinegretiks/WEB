from flask import Flask, render_template, make_response, jsonify
from werkzeug.utils import redirect
from data import db_session
from data.posts import Post
from data.users import User
from forms.login import LoginForm
from forms.register import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from api import users_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

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
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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

    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == 1).first()
    if not post:
        post = Post()
        post.id = 1
        post.name = 'Администратор'
        db_sess.add(post)
        db_sess.commit()

    post = db_sess.query(Post).filter(Post.id == 2).first()
    if not post:
        post = Post()
        post.id = 2
        post.name = 'Модератор'
        db_sess.add(post)
        db_sess.commit()

    post = db_sess.query(Post).filter(Post.id == 3).first()
    if not post:
        post = Post()
        post.id = 3
        post.name = 'Пользователь'
        db_sess.add(post)
        db_sess.commit()

    user = db_sess.query(User).filter(User.email == 'admin@mail.ru').first()
    if not user:
        user = User()
        user.email = 'admin@mail.ru'
        user.name = 'admin'
        user.post_id = 1
        user.set_password('admin')
        db_sess.add(user)
        db_sess.commit()

    app.register_blueprint(users_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
