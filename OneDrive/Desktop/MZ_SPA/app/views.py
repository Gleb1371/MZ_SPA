from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Task
from .database import SessionLocal
from .schemas import TaskCreate, TaskResponse, TaskUpdate   

router = APIRouter()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Получить все задачи пользователя
@router.get(
    "/tasks", 
    response_model=list[TaskResponse], 
    summary="Получение всех задач пользователя",
    responses={
        200: {"description": "Список задач успешно получен"},
        404: {"description": "Задачи пользователя не найдены"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def get_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.user_id == user_id))
    tasks = result.scalars().all()

    return tasks

# Получить конкретную задачу пользователя
@router.get(
    "/tasks/{task_id}", 
    response_model=TaskResponse, 
    summary="Получение задачи по ID",
    responses={
        200: {"description": "Задача успешно получена"},
        404: {"description": "Задача не найдена или нет доступа"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def get_task(task_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found or you don't have access")

    return task

# Создать новую задачу
@router.post(
    "/tasks", 
    response_model=TaskResponse, 
    status_code=201, 
    summary="Создание новой задачи",
    responses={
        201: {"description": "Задача успешно создана"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def create_task(task_data: TaskCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    task = Task(user_id=user_id, heading=task_data.heading, task_text=task_data.task_text)
    db.add(task)
    await db.commit()

    return task

# Обновить задачу
@router.put(
    "/tasks/{task_id}", 
    status_code=200, 
    summary="Обновление задачи",
    responses={
        200: {"description": "Задача успешно обновлена"},
        404: {"description": "Задача не найдена или нет доступа"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def update_task(task_id: int, task_data: TaskUpdate, user_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found or you don't have access")

    if task_data.heading is not None:
        task.heading = task_data.heading
    if task_data.task_text is not None:
        task.task_text = task_data.task_text

    await db.commit()
    return {"message": "Task updated successfully"}

# Удалить задачу
@router.delete(
    "/tasks/{task_id}", 
    status_code=200, 
    summary="Удаление задачи",
    responses={
        200: {"description": "Задача успешно удалена"},
        404: {"description": "Задача не найдена или нет доступа"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def delete_task(task_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if task is None or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found or you don't have access")

    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}
