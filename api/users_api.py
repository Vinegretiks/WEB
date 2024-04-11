import flask
from flask import redirect
from flask_login import login_required, current_user

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/users', methods=['GET'])
@login_required
def get_users():
    if current_user.post_id == 1:
        return "Обработчик в news_api"
    else:
        return redirect('/')


@blueprint.route('/users/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    if current_user.post_id == 1:
        return "Обработчик в news_api"
    else:
        return redirect('/')


@blueprint.route('/users', methods=['POST'])
@login_required
def create_user():
    if current_user.post_id == 1:
        return "Обработчик в news_api"
    else:
        return redirect('/')


@blueprint.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    if current_user.post_id == 1:
        return "Обработчик в news_api"
    else:
        return redirect('/')


@blueprint.route('/users/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    if current_user.post_id == 1:
        return "Обработчик в news_api"
    else:
        return redirect('/')
