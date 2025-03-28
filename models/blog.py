from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, LargeBinary
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase
from datetime import datetime


class Poster(SqlAlchemyBase):
    __tablename__ = 'poster'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False, default='title')
    description = Column(Text, nullable=True, default='description')
    tags = Column(String(255), nullable=True, default='tags')
    category = Column(Enum('news', 'article', 'event', name='poster_category'), nullable=False, default='news')
    date_posted = Column(DateTime, default=datetime.now())
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    # Внешние ключи
    user = relationship("User", back_populates="posters")
    comments = relationship("CommentPoster", back_populates="post")
    images = relationship("ImagePoster", back_populates="post")


class ImagePoster(SqlAlchemyBase):
    __tablename__ = 'image_poster'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(LargeBinary, nullable=True)
    post_id = Column(Integer, ForeignKey('poster.id'), nullable=False)
    post = relationship("Poster", back_populates="images")

class CommentPoster(SqlAlchemyBase):
    __tablename__ = 'comments_poster'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('poster.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    text = Column(Text, nullable=False, default='text')

    # Relationships
    post = relationship("Poster", back_populates="comments")
    user = relationship("User", back_populates="comments")
