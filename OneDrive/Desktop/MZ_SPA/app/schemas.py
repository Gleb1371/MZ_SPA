from pydantic import BaseModel
from typing import Optional

# Модель для создания задачи 
class TaskCreate(BaseModel):
    heading: str
    task_text: str

# Модель для обновления задачи 
class TaskUpdate(BaseModel):
    heading: Optional[str] = None
    task_text: Optional[str] = None

# Модель ответа для задачи
class TaskResponse(BaseModel):
    task_id: int
    heading: str
    task_text: str
    user_id: int

    class Config:
        orm_mode = True

# Модель для создания пользователя (регистрация)
class UserCreate(BaseModel):
    login: str
    password: str

# Модель ответа для пользователя
class UserResponse(BaseModel):
    user_id: int
    login: str

    class Config:
        orm_mode = True
