import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash

# создание таблицы пользователей в базе данных
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"))
    post = orm.relationship('Post')
    balance = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password): # шифрование сгенерированного пароля
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password): # проверка правильности шифрование пароля
        return check_password_hash(self.hashed_password, password)
