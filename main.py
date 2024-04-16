from random import randint

from flask import Flask, render_template, make_response, jsonify, request, url_for, flash
from werkzeug.utils import redirect, secure_filename
from data import db_session
from data.posts import Post
from data.users import User
from forms.gamefirst import GameFirst
from forms.login import LoginForm
from forms.register import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from api import users_api
import os
from time import sleep

from forms.second_game import StartMenuSecondGame, SecondGame
from forms.third_game import ThirdGame, StartThirdGame

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'  # секртный ключ
CLICK_COUNT = 0  # счётчик кликов
attempt1, attempt2, attempt3, attempt4, attempt5 = '', '', '', '', ''  # попытки в первой игре
RANDOM_NUM = randint(1, 100)  # рандомайзер от 1 до 100
it = ''
User_summ, User_stavka = 0, 0  # Ставки в первой и во второй игре соответсвтенно

UPLOAD_FOLDER = 'static/uploads/'  # путь загрузки фото
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # фотка
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # размер загруженной картинки

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])  # допутимые форматы изображений


# функция проверки провельности формата загруженной картинки в профиль
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


login_manager = LoginManager()
login_manager.init_app(app)


# подключение базы данных
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')  # путь к начальному файлу
def index():
    if current_user.is_authenticated:  # проверка на то, что пользователь авторизирован
        return render_template('index_auth.html', title='Moonstruck',
                               specific_page=True)  # обращение к html файлу с авторизацией
    else:
        return render_template('index.html', title='Moonstruck',
                               specific_page=True)  # обращение к html файлу, который отвечает за начальную страницу


@app.route('/logout')  # путь к функции
@login_required  # проверка, что пользователь зашёл в свой аккаунт
def logout():  # функция logout
    logout_user()  # функция, которая выходит из авторизации
    return redirect("/")  # путь, перенаправляющий на главную страницу


@app.route('/login', methods=['GET', 'POST'])  # путь функции
def login():  # функция логина пользователя, который уже зареган в базе данных
    form = LoginForm()
    if form.validate_on_submit():  # проверка на то, что кнопка нажата пользователем
        db_sess = db_session.create_session()  # подключение к базе данных
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()  # проверка на то, что совпадает почта при ригестрации и авторизации у пользователя
        if user and user.check_password(form.password.data):  # проверка на правильность введённого пароля
            login_user(user, remember=form.remember_me.data)  # запоминания пользователя
            return redirect("/")  # путь, перенаправляющий на главную страницу
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)  # обращение к html файлу, который отвечает за страницу с логином и направление смс, если не соблюдено условие
    return render_template('login.html', title='Авторизация',
                           form=form)  # обращение к html файлу, который отвечает за страницу с логином


@app.route('/register', methods=['GET', 'POST'])  # путь функции
def register():  # функция, которая вывдит форму регистрации нового пользователя
    form = RegisterForm()
    if form.validate_on_submit():  # проверка того, что пользоветель нажал кнопку
        if form.password.data != form.password_again.data:  # проверка на того, что пользователь правильно ввёл пароль в ячейке повтора пароля
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(
                User.email == form.email.data).first():  # проверка на то, что пользователь уже зареган
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.balance = 100  # присваивание начального баланса новенькому
        user.set_password(form.password.data)  # установление пароля
        db_sess.add(user)  # добавление пользователя
        db_sess.commit()  # сохранение изменений в базе данных
        return redirect('/login')  # перенаправление на страницу авторизаиии
    return render_template('register.html', title='Регистрация',
                           form=form)  # # обращение к html файлу, который отвечает за страницу с регистрацией пользователя


# проверка в базе данных на то, что у пользователя достаточно денег на балансе
def proverka():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email).first()
    if user.balance < 10:
        return False
    return True


@app.route('/game 1', methods=['GET', 'POST'])
def game_1():
    global CLICK_COUNT
    global RANDOM_NUM, it
    form = GameFirst()
    global attempt1, attempt2, attempt3, attempt4, attempt5
    if proverka():
        if form.validate_on_submit():
            CLICK_COUNT += 1
            num = int(form.number.data)
            form.number.data = ''
            if CLICK_COUNT < 6:
                if num > RANDOM_NUM: a = 'Загаданное число меньше'
                if num < RANDOM_NUM: a = 'Загаданное число больше'
                if num == RANDOM_NUM:
                    db_sess = db_session.create_session()
                    user = db_sess.query(User).filter(User.email).first()
                    user.balance = user.balance + 10
                    db_sess.commit()
                    it = f'Вы выиграли, +10 к балансу. Загаданное число {RANDOM_NUM}'
                    CLICK_COUNT = 0
                    attempt1, attempt2, attempt3, attempt4, attempt5, attempt6 = '', '', '', '', '', ''
                    db_sess = db_session.create_session()
                    user = db_sess.query(User).filter(User.email).first()
                    user.balance = user.balance + 10
                    db_sess.commit()
                    RANDOM_NUM = randint(1, 100)
                if CLICK_COUNT == 1: attempt1 = a
                if CLICK_COUNT == 2: attempt2 = a
                if CLICK_COUNT == 3: attempt3 = a
                if CLICK_COUNT == 4: attempt4 = a
                if CLICK_COUNT == 5: attempt5 = a
            else:
                it = f'Вы проиграли, -10 к балансу. Загаданное число {RANDOM_NUM}'
                CLICK_COUNT = 0
                attempt1, attempt2, attempt3, attempt4, attempt5, attempt6 = '', '', '', '', '', ''
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.email).first()
                user.balance = user.balance - 10
                db_sess.commit()
            print(CLICK_COUNT)
    else:
        return render_template("Game_1.html", form=form, attempt1=attempt1, attempt2=attempt2, attempt3=attempt3,
                               attempt4=attempt4, attempt5=attempt5, it='Недостаточно средств для продолжения игры')
    return render_template("Game_1.html", form=form, attempt1=attempt1, attempt2=attempt2, attempt3=attempt3,
                           attempt4=attempt4, attempt5=attempt5, it=it)


@app.route('/Start_game_2', methods=['GET', 'POST'])
def start_game_2():
    global User_stavka
    form = StartMenuSecondGame()
    db_sess = db_session.create_session()
    user_game_2 = db_sess.query(User).filter(User.email).first()

    if form.validate_on_submit():
        User_stavka = form.Second_stavka.data
        if user_game_2.balance >= int(User_stavka):
            if 50 >= int(User_stavka) >= 10:
                return redirect('/game 2')
            else:
                return render_template("Start_game_2.html", form=form, message='Введите конкретное число от 10 до 50')
        else:
            return render_template("Start_game_2.html", form=form, message='У вас недостаточно денег на балансе')
    return render_template("Start_game_2.html", form=form)


@app.route('/game 2', methods=['GET', 'POST'])
def game_2():
    global User_stavka
    form = SecondGame()
    RED = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
    BLACK = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
    F_st_12 = [i for i in range(1, 13)]
    S_st_12 = [i for i in range(12, 25)]
    T_st_12 = [i for i in range(24, 37)]
    F_2to1 = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
    S_2to1 = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
    T_2to1 = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
    First_to_18 = [i for i in range(1, 19)]
    TN_to_36 = [i for i in range(19, 37)]
    Zero = 0
    CHISLO = randint(0, 36)
    db_sess = db_session.create_session()
    user_game_2 = db_sess.query(User).filter(User.email).first()
    win_text = "Недостаточно средств для продолжения игры"
    if form.validate_on_submit():
        if user_game_2.balance >= int(User_stavka):
            if not (form.Red.data or form.Black.data or form.Even.data or form.Odd.data \
                    or form.Fst_12.data or form.Snd_12.data or form.Trd_12.data \
                    or form.F2to1.data or form.S2to1.data or form.T2to1.data or form.Zero.data \
                    or form.First_to_18.data or form.TN_to_36.data):
                win_text = "Пожалуйста выберите, на что будете ставить"
                return render_template("Game_2.html", form=form, win_text=win_text, bal=User_stavka)
            else:
                if form.Red.data:
                    user_game_2.balance -= int(User_stavka)
                if form.Black.data:
                    user_game_2.balance -= int(User_stavka)
                if form.Odd.data:
                    user_game_2.balance -= int(User_stavka)
                if form.Even.data:
                    user_game_2.balance -= int(User_stavka)
                if form.Fst_12.data:
                    user_game_2.balance -= int(User_stavka)
                if form.Snd_12.data:
                    user_game_2.balance -= int(User_stavka)
                if form.Trd_12.data:
                    user_game_2.balance -= int(User_stavka)
                if form.F2to1.data:
                    user_game_2.balance -= int(User_stavka)
                if form.S2to1.data:
                    user_game_2.balance -= int(User_stavka)
                if form.T2to1.data:
                    user_game_2.balance -= int(User_stavka)
                if form.Zero.data:
                    user_game_2.balance -= int(User_stavka)
                db_sess.commit()
                if CHISLO == Zero and form.Zero.data:
                    win_text = f'+ {int(User_stavka) * 5} к балансу'
                    User_stavka += int(User_stavka) * 5
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in RED and form.Red.data:
                    win_text = f"+ {int(User_stavka) * 2} к балансу"
                    user_game_2.balance += int(User_summ) * 2
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in BLACK and form.Black.data:
                    win_text = f"+ {int(User_stavka) * 2} к балансу"
                    user_game_2.balance += int(User_summ) * 2
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO % 2 == 0 and form.Odd.data:
                    win_text = f"+ {int(User_stavka) * 2} к балансу"
                    user_game_2.balance += int(User_summ) * 2
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO % 2 != 0 and form.Even.data:
                    win_text = f"+ {int(User_stavka) * 2} к балансу"
                    user_game_2.balance += int(User_summ) * 2
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in F_st_12 and form.Fst_12.data:
                    win_text = f"+ {int(User_stavka) + 15} к балансу"
                    user_game_2.balance += int(User_summ)
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in S_st_12 and form.Snd_12.data:
                    win_text = f"+ {int(User_stavka) + 15} к балансу"
                    user_game_2.balance += int(User_summ)
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in T_st_12 and form.Trd_12.data:
                    win_text = f"+ {int(User_stavka) + 15} к балансу"
                    user_game_2.balance += int(User_summ)
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in S_2to1 and form.S2to1.data:
                    win_text = f'+ {int(User_stavka) + 8} к балансу'
                    user_game_2.balance += int(User_stavka) + 8
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in T_2to1 and form.T2to1.data:
                    win_text = f'+ {int(User_stavka) + 8} к балансу'
                    user_game_2.balance += int(User_stavka) + 8
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in F_2to1 and form.F2to1.data:
                    win_text = f'+ {int(User_stavka) + 8} к балансу'
                    user_game_2.balance += int(User_stavka) + 8
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in First_to_18 and form.First_to_18.data:
                    win_text = f'+ {int(User_stavka) + 5} к балансу'
                    user_game_2.balance += int(User_stavka) + 5
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                if CHISLO in TN_to_36 and form.TN_to_36.data:
                    win_text = f'+ {int(User_stavka) + 5} к балансу'
                    user_game_2.balance += int(User_stavka) + 5
                    db_sess.commit()
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
                else:
                    win_text = f'- {int(User_stavka)} к балансу из-за того, что вы выбрали нечего не выпало'
                    return render_template("Game_2.html", form=form, bal=User_stavka, chi=f'Выпало число: {CHISLO}',
                                           win_text=win_text)
        else:
            return render_template("Game_2.html", form=form, win_text=win_text, bal=User_stavka)
    return render_template("Game_2.html", form=form, bal=User_stavka)


@app.route('/Start_game_3', methods=['GET', 'POST'])
def start_game_3():
    global User_summ
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email).first()
    bal = user.balance
    form = StartThirdGame()
    if form.validate_on_submit():
        User_summ = form.Third_game_sum.data
        if int(bal) >= int(User_summ):
            if 100 >= int(User_summ) >= 10:
                return redirect('/game 3')
            else:
                return render_template("Start_game_3.html", form=form, message="Введите корректное число")
        else:
            return render_template("Start_game_3.html", form=form, message="У вас недостаточно денег на балансе")
    return render_template("Start_game_3.html", form=form)


@app.route('/game 3', methods=['GET', 'POST'])
def game_3():
    global User_summ
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email).first()
    form = ThirdGame()
    first = randint(1, 50)
    second = randint(1, 50)
    third = randint(1, 50)
    win = "Вы проиграли"
    if form.validate_on_submit():
        if user.balance >= int(User_summ):
            if first == second == third:
                win = "Джекпот"
                user.balance += int(User_summ) * 5
                db_sess.commit()
            elif first == second or second == third or first == third:
                win = "Вы выиграли, у вас совпало два числа!"
                user.balance += int(User_summ) * 3
                db_sess.commit()
            else:
                user.balance -= int(User_summ)
                db_sess.commit()
            return render_template("Game_3.html", form=form, User_summ=User_summ, first=first, second=second,
                                   third=third, win=win)
        else:
            win = "У вас недостаточно средств"
            return render_template("Game_3.html", form=form, User_summ=User_summ, win=win)
    return render_template("Game_3.html", form=form, User_summ=User_summ)


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
    # print(1212)
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
def balance():  # показ баланса пользователя
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email).first()
    a = user.balance
    return render_template('balance.html', bal=a)


@app.errorhandler(404)  # сервер не может найти нужные страницы
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@app.errorhandler(401)  # проблема с авторизацией, человек не авторизован
def bad_request(_):
    return make_response(jsonify({'error': 'Not access'}), 401)


@app.errorhandler(400)  # отправка некорректных запросов
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':  # если название файла совпадает с условием, то есть 'main'
    db_session.global_init("blogs.db")  # подключение базы данных
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == 1).first()
    if not post:  # если нет администратора, то он создаётся
        post = Post()
        post.id = 1
        post.name = 'Администратор'
        db_sess.add(post)
        db_sess.commit()

    post = db_sess.query(Post).filter(Post.id == 3).first()
    # if not post:  # создание строки пользователя в таблице, где пользователь сможет заполнить данные
    #     post = Post()
    #     post.id = 3
    #     post.name = 'Пользователь'
    #     db_sess.add(post)
    #     db_sess.commit()

    user = db_sess.query(User).filter(User.email == 'admin@mail.ru').first()
    if not user:  # создание администратора в базе данных
        user = User()
        user.email = 'admin@mail.ru'
        user.name = 'admin'
        user.post_id = 1
        user.set_password('admin')
        db_sess.add(user)
        db_sess.commit()

    app.register_blueprint(users_api.blueprint)  # создание API
    app.run(port=8080, host='127.0.0.1')  # порт подключения
