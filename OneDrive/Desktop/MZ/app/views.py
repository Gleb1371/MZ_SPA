from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.authentication import requires
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from .models import Task, User
from .auth import verify_password, get_password_hash, create_access_token
from .database import SessionLocal

templates = Jinja2Templates(directory="app/templates")

async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def lk_page(request: Request):
    return templates.TemplateResponse("LK.html", {"request": request})

async def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

async def regis_page(request: Request):
    return templates.TemplateResponse("regis.html", {"request": request})

async def registration(request: Request):
    data = await request.json()
    async with SessionLocal() as session:
        async with session.begin():
            try:
                existing_user = await session.execute(
                    select(User).filter(User.login == data["login"])
                )
                if existing_user.scalar_one_or_none():
                    return JSONResponse({"error": "Пользователь с таким логином уже зарегистрирован!"}, status_code=400)

                user = User(
                    login=data["login"], password=get_password_hash(data["password"])
                )
                session.add(user)
                await session.commit()
                return JSONResponse({"message": "Регистрация прошла успешно."})
            except IntegrityError:
                await session.rollback()
                return JSONResponse({"error": "Ошибка."}, status_code=400)
            except Exception as e:
                await session.rollback()
                return JSONResponse({"error": str(e)}, status_code=400)

async def auth(request: Request):
    data = await request.json()
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User).filter(User.login == data["login"])
            )
            user = result.scalar_one_or_none()
    if user and verify_password(data["password"], user.password):
        token = create_access_token(data={"sub": user.user_id})
        return JSONResponse({"access_token": token}, status_code=200)
    return JSONResponse({"error": "Неверный логин или пароль"}, status_code=401)

@requires("authenticated")
async def delete_task(request: Request):
    task_id = int(request.path_params["task_id"]) 
    user_id = int(request.user.username)

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()
            
            if task is None:
                return JSONResponse({"error": "Задача не найдена"}, status_code=404)

            await session.delete(task)
            await session.commit()

    return JSONResponse({"message": f"Задача с айди={task_id} была удалена"})

@requires("authenticated")
async def get_task_by_id(request: Request):
    task_id = int(request.path_params["task_id"])
    user_id = int(request.user.username)

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()

    if task:
        task_dict = {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "completed": task.completed,
            "heading": task.heading,
            "task_text": task.task_text,
        }
        return JSONResponse(task_dict)
    else:
        return JSONResponse({"error": "Task not found"}, status_code=404)

@requires("authenticated")
async def get_now_tasks(request: Request):
    user_id = int(request.user.username)
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id, Task.completed == False)
            )
            tasks = results.scalars().all()

    tasks_list = []
    for task in tasks:
        task_dict = {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "completed": task.completed,
            "heading": task.heading,
            "task_text": task.task_text,
        }
        tasks_list.append(task_dict)

    return JSONResponse(tasks_list)

@requires("authenticated")
async def get_completed_tasks(request: Request):
    user_id = int(request.user.username)
    async with SessionLocal() as session:
        async with session.begin():
            results = await session.execute(
                select(Task).filter(Task.user_id == user_id, Task.completed == True)
            )
            tasks = results.scalars().all()

    tasks_list = []
    for task in tasks:
        task_dict = {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "completed": task.completed,
            "heading": task.heading,
            "task_text": task.task_text,
        }
        tasks_list.append(task_dict)

    return JSONResponse(tasks_list)

@requires("authenticated")
async def create_task(request: Request):
    data = await request.json()
    user_id = int(request.user.username)
    heading = data.get("heading")
    task_text = data.get("task_text")
    completed = data.get("completed", False)

    async with SessionLocal() as session:
        async with session.begin():
            task = Task(
                user_id=user_id,
                heading=heading,
                task_text=task_text,
                completed=completed,
            )
            session.add(task)
            await session.commit()
            
            response_data = {
                "task_id": task.task_id,
                "user_id": task.user_id,
                "heading": task.heading,
                "task_text": task.task_text,
                "completed": task.completed,
            }
            
            return JSONResponse(response_data, status_code=201)

@requires("authenticated")
async def update_task(request: Request):
    data = await request.json()
    user_id = int(request.user.username)
    task_id = int(request.path_params["task_id"])
    heading = data.get("heading")
    task_text = data.get("task_text")
    completed = data.get("completed", False)

    async with SessionLocal() as session:
        async with session.begin():
            task = await session.get(Task, task_id)
            if task and task.user_id == user_id:
                task.heading = heading
                task.task_text = task_text
                task.completed = completed
                await session.commit()

                response_data = {
                    "task_id": task.task_id,
                    "user_id": user_id,
                    "heading": heading,
                    "task_text": task.task_text,
                    "completed": task.completed,
                }
                return JSONResponse(response_data, status_code=200)
            else:
                return JSONResponse({"error": "Задача не найдена или не принадлежит пользователю"}, status_code=404)

@requires("authenticated")
async def complete_task(request: Request):
    task_id = int(request.path_params["task_id"])
    user_id = int(request.user.username)

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()

            if task is None:
                return JSONResponse({"error": "Задача не найдена"}, status_code=404)

            task.completed = True
            await session.commit()

    return JSONResponse({"message": "Задача завершена"})

@requires("authenticated")
async def resume_task(request: Request):
    task_id = int(request.path_params["task_id"])
    user_id = int(request.user.username)

    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Task).filter(Task.task_id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()

            if task is None:
                return JSONResponse({"error": "Задача не найдена"}, status_code=404)

            task.completed = False
            await session.commit()

    return JSONResponse({"message": "Задача возобновлена"})
