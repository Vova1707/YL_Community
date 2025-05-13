from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase


class Program(SqlAlchemyBase):
    __tablename__ = 'programs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Float, nullable=True, default=0)
    user = relationship("User", back_populates="programs")

    def __repr__(self):
        return f"<Program(rating={self.rating})>"
