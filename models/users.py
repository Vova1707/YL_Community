from sqlalchemy import Column, Integer, String, Text, Enum, LargeBinary
from sqlalchemy.orm import relationship

from db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, default='name')
    surname = Column(String(50), nullable=False, default='surname')
    about = Column(Text, nullable=True, default='about')
    age = Column(Integer, nullable=True, default=52)
    email = Column(String(120), unique=True, nullable=False, default='teach@mail.ru')
    image_profile = Column(LargeBinary, nullable=True, default=None)
    type = Column(Enum('teacher', 'student', 'admin', name='user_type'),
                 nullable=False, default='student')
    password_hash = Column(String(128), nullable=False)

    # Связи с другими моделями
    posters = relationship("Poster", back_populates="user")
    comments = relationship("CommentPoster", back_populates="user")
    projects = relationship("Project", back_populates="user")
    programs = relationship("Program", back_populates="user")
    like = relationship("LikePoster", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name} {self.surname}, {self.email}>'