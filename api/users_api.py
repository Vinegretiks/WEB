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
            if db_sess.query(User).filter(User.id == ID).first():
                return redirect(f'/users_red/{ID}')
            return render_template('admin_panel.html', form=form, users=users, it='Такого пользователя нет')
        return render_template('admin_panel.html', form=form, users=users)
    else:
        return redirect('/')


@blueprint.route('/users_red/<int:id>', methods=['GET', 'POST'])
@login_required
def users(id):
    ID = id
    if current_user.post_id == 1:
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id == ID).first()
        form = Admin_redact()
        if form.validate_on_submit():
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

        return render_template('redact.html', action_str=f'/users_red/{ID}', id=ID, form=form)
    else:
        return redirect('/')
