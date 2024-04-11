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
    if current_user.post_id == 1:
        form = Admin()
        global ID
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        if form.validate_on_submit():
            ID = int(form.number.data)
            print(ID)
            if db_sess.query(User).filter(User.id == ID):
                return redirect('/users_red')
            return render_template('admin_panel.html', form=form, users=users, it='Такого пользователя нет')
        return render_template('admin_panel.html', form=form, users=users)
    else:
        return redirect('/')


@blueprint.route('/users_red', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def users():
    global ID
    if current_user.post_id == 1:
        form = Admin_redact()
        ID = 5
        print(ID)
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id == ID).first()
        form.email.data = users.email
        form.name.data = users.name
        form.balance.data = users.balance
        if form.validate_on_submit():
            user = db_sess.query(User).filter(User.id == ID).first()
            user.balance = form.balance.data
            users.name = form.name.data
            users.email = int(form.email.data)
            db_sess.commit()
            return redirect('/users')
        return render_template('redact.html', form=form)
    else:
        return redirect('/')


# @blueprint.route('/users/delete', methods=['DELETE'])
# @login_required
# def delete_user(id):
#     if current_user.post_id == 1:
#         return "Обработчик в news_api, delete"
#     else:
#         return redirect('/')
#
#
# @blueprint.route('/users/<int:id>', methods=['GET'])
# @login_required
# def get_user(id):
#     if current_user.post_id == 1:
#         return "Обработчик в news_api, get"
#     else:
#         return redirect('/')
#
#
# @blueprint.route('/users', methods=['POST'])
# @login_required
# def create_user():
#     if current_user.post_id == 1:
#         return "Обработчик в news_api, post"
#     else:
#         return redirect('/')
#
#
# @blueprint.route('/users/<int:id>', methods=['PUT'])
# @login_required
# def update_user(id):
#     if current_user.post_id == 1:
#         return "Обработчик в news_api, put"
#     else:
#         return redirect('/')
