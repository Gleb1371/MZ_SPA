from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    completed = Column(Boolean, default=False)
    heading = Column(Text)
    task_text = Column(Text)
    user = relationship("User", back_populates="tasks")

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    tasks = relationship("Task", back_populates="user")
