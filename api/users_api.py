import flask
from flask import redirect, render_template, request
from flask_login import login_required, current_user

from data import db_session
from data.users import User
from forms.admin import Admin
from forms.redact import Admin_redact

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)
ID = 0


@blueprint.route('/users', methods=['GET', 'POST'])
@login_required
def get_users():
    # если пользователь имееет id = 1
    if current_user.post_id == 1:
        # подключение к форме
        form = Admin()
        global ID
        # открытие сессии базы данных
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        if form.validate_on_submit():  # проверка отправки формы/нажатия кнопки
            ID = int(form.number.data)
            print(ID)
            if db_sess.query(User).filter(User.id == ID).first():
                return redirect(f'/users_red/{ID}')
            return render_template('admin_panel.html', form=form, users=users, it='Такого пользователя нет')
        return render_template('admin_panel.html', form=form, users=users)
    else:  # если пользователь не админ, то перенос на общую страницу
        return redirect('/')


# путь к опред пользователю через id
@blueprint.route('/users_red/<int:id>', methods=['GET', 'POST'])
@login_required
def users(id):
    ID = id
    # елси пользователь админ(id = 1)
    if current_user.post_id == 1:
        # открытие сессии базы данных
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id == ID).first()
        form = Admin_redact()
        # проверка отправки формы/нажатия кнопки
        if form.validate_on_submit():
            # изменения данных пользователя
            user = db_sess.query(User).filter(User.id == ID).first()
            user.balance = int(form.balance.data)
            users.name = form.name.data
            users.email = form.email.data
            print(form.balance)
            db_sess.commit()
            return redirect('/users')

        form.email.data = users.email
        form.name.data = users.name
        form.balance.data = users.balance
        print(id, form.validate_on_submit())
    # отображение страницы
        return render_template('redact.html', action_str=f'/users_red/{ID}', id=ID, form=form)
    else:
        return redirect('/')
