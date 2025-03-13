from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase
from datetime import datetime


class Projects(SqlAlchemyBase):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Text, nullable=False) # категория проекта(связь один с одним)
    tags = Column(Text, nullable=False) # теги (связь один со многим)
    files = Column(Text, nullable=False) # файлы(думаю просто rar архив достаточно)
    links = Column(Text, nullable=False) # список ссылок
    created_at = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'<Project {self.title} for user for id={self.user_id}>'

'''Здесь ещё модели: category, tags пока'''