from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase
from datetime import datetime


class BlogPost(SqlAlchemyBase):
    __tablename__ = 'blog_posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    date_posted = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey('users.id'))

    author = relationship("User", back_populates="blog_posts")

    def __repr__(self):
        return f'<BlogPost {self.title}>'