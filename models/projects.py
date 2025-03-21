from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, LargeBinary
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase
from datetime import datetime


class Project(SqlAlchemyBase):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False, default='title')
    description = Column(Text, nullable=True, default='description')
    # category = Column(Enum('web', 'mobile', 'data_science', name='project_category'), nullable=False)
    category = Column(Enum('web', 'mobile', 'data_science', 'no_category', name='project_category'), default='no_category', nullable=True)
    file = Column(LargeBinary, nullable=True, default=None)
    file_tree = Column(LargeBinary, nullable=True, default=None)

    # Внешние ключи
    user = relationship("User", back_populates="projects")