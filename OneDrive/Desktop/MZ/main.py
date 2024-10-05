from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from app.views import (
    homepage, lk_page, auth_page, regis_page, registration, auth, delete_task, 
    get_task_by_id, get_now_tasks, get_completed_tasks, 
    create_task, update_task, complete_task, resume_task
)
from app.auth import JWTAuthanticationBackend

routes = [
    Route("/", homepage),
    Route("/index.html", homepage),
    Route("/LK.html", lk_page),
    Route("/auth.html", auth_page),
    Route("/regis.html", regis_page),
    Mount("/static", StaticFiles(directory="static"), name="static"),
    Route("/registration", registration, methods=["POST"]),
    Route("/auth", auth, methods=["POST"]),
    Route("/create_task", create_task, methods=["POST"]),
    Route("/tasks", get_now_tasks, methods=["GET"]),
    Route("/tasks_completed", endpoint=get_completed_tasks, methods=["GET"]),
    Route("/tasks/{task_id:int}", get_task_by_id, methods=["GET"]),
    Route("/tasks/{task_id:int}", endpoint=update_task, methods=["PUT"]),
    Route("/tasks/{task_id}", endpoint=delete_task, methods=["DELETE"]),
    Route("/tasks/{task_id}/complete", complete_task, methods=["PATCH"]),
    Route("/tasks/{task_id}/resume", resume_task, methods=["PATCH"]),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthanticationBackend())
