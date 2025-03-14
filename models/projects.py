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
    category = Column(Enum('web', 'mobile', 'data_science', name='project_category'), nullable=False)
    rar = Column(LargeBinary, nullable=True, default=None) # полюшко для хравения rar

    # Внешние ключи
    user = relationship("User", back_populates="projects")