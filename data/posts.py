import sqlalchemy
from .db_session import SqlAlchemyBase


# Модель должностей пользователей, создание таблицы для пользователя и админа
class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
