from fastapi import FastAPI
from app.views import router as task_router
from app.auth import router as auth_router


app = FastAPI(
    title="Task Management API",
    description="API для управления задачами и пользователями",
    version="1.0.0",  # Версия API
    openapi_url="/api/openapi.json",  # URL для файла OpenAPI
    docs_url="/api/docs",  # Путь к документации Swagger
    redoc_url="/api/redoc"  # Путь к документации ReDoc
)


app.include_router(auth_router, prefix="/api")
app.include_router(task_router, prefix="/api")
