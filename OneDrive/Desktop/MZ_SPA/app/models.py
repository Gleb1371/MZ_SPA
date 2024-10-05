from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    heading = Column(Text)
    task_text = Column(Text)
    user = relationship("User", back_populates="tasks")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    tasks = relationship("Task", back_populates="user")
