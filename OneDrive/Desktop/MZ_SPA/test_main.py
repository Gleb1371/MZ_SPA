import pytest
from httpx import AsyncClient
from main import app
from app.database import engine
from app.models import Base

# Настройка тестовой базы данных
@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Фикстура для клиента
@pytest.fixture(scope="function")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Тест регистрации пользователя
@pytest.mark.asyncio
async def test_registration(client):
    response = await client.post("/api/registration", json={
        "login": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["login"] == "testuser"
    assert "user_id" in data

# Тест авторизации пользователя
@pytest.mark.asyncio
async def test_auth(client):
    # Сначала регистрируем пользователя
    await client.post("/api/registration", json={
        "login": "testuser",
        "password": "testpassword"
    })

    # Теперь авторизуемся
    response = await client.post("/api/auth", json={
        "login": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "testuser"
    assert "user_id" in data

# Тест выхода из системы
@pytest.mark.asyncio
async def test_logout(client):
    response = await client.post("/api/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}

# Тест создания задачи
@pytest.mark.asyncio
async def test_create_task(client):
    # Сначала регистрируем пользователя
    registration_response = await client.post("/api/registration", json={
        "login": "testuser",
        "password": "testpassword"
    })
    user_id = registration_response.json()["user_id"]

    # Создаем задачу
    response = await client.post(f"/api/tasks?user_id={user_id}", json={
        "heading": "Test Task",
        "task_text": "This is a test task"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["heading"] == "Test Task"
    assert data["task_text"] == "This is a test task"
    assert "task_id" in data
    assert data["user_id"] == user_id

# Тест получения всех задач пользователя
@pytest.mark.asyncio
async def test_get_tasks(client):
    # Сначала регистрируем пользователя
    registration_response = await client.post("/api/registration", json={
        "login": "testuser",
        "password": "testpassword"
    })
    user_id = registration_response.json()["user_id"]

    # Создаем задачу
    await client.post(f"/api/tasks?user_id={user_id}", json={
        "heading": "Test Task",
        "task_text": "This is a test task"
    })

    # Получаем задачи
    response = await client.get(f"/api/tasks?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["heading"] == "Test Task"
    assert data[0]["task_text"] == "This is a test task"
    assert data[0]["user_id"] == user_id

# Тест получения конкретной задачи
@pytest.mark.asyncio
async def test_get_task(client):
    # Сначала регистрируем пользователя
    registration_response = await client.post("/api/registration", json={
        "login": "testuser",
        "password": "testpassword"
    })
    user_id = registration_response.json()["user_id"]

    # Создаем задачу
    create_response = await client.post(f"/api/tasks?user_id={user_id}", json={
        "heading": "Test Task",
        "task_text": "This is a test task"
    })
    task_id = create_response.json()["task_id"]

    # Получаем конкретную задачу
    response = await client.get(f"/api/tasks/{task_id}?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["heading"] == "Test Task"
    assert data["task_text"] == "This is a test task"
    assert data["user_id"] == user_id

# Тест обновления задачи
@pytest.mark.asyncio
async def test_update_task(client):
    # Сначала регистрируем пользователя
    registration_response = await client.post("/api/registration", json={
        "login": "testuser",
        "password": "testpassword"
    })
    user_id = registration_response.json()["user_id"]

    # Создаем задачу
    create_response = await client.post(f"/api/tasks?user_id={user_id}", json={
        "heading": "Test Task",
        "task_text": "This is a test task"
    })
    task_id = create_response.json()["task_id"]

    # Обновляем задачу
    update_response = await client.put(f"/api/tasks/{task_id}?user_id={user_id}", json={
        "heading": "Updated Task",
        "task_text": "This is an updated test task"
    })
    assert update_response.status_code == 200
    assert update_response.json() == {"message": "Task updated successfully"}

    # Проверяем, что задача обновлена
    response = await client.get(f"/api/tasks/{task_id}?user_id={user_id}")
    task = response.json()
    assert task["heading"] == "Updated Task"
    assert task["task_text"] == "This is an updated test task"

# Тест удаления задачи
@pytest.mark.asyncio
async def test_delete_task(client):
    # Сначала регистрируем пользователя
    registration_response = await client.post("/api/registration", json={
        "login": "testuser",
        "password": "testpassword"
    })
    user_id = registration_response.json()["user_id"]

    # Создаем задачу
    create_response = await client.post(f"/api/tasks?user_id={user_id}", json={
        "heading": "Test Task",
        "task_text": "This is a test task"
    })
    task_id = create_response.json()["task_id"]

    # Удаляем задачу
    delete_response = await client.delete(f"/api/tasks/{task_id}?user_id={user_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Task deleted successfully"}

    # Проверяем, что задача удалена
    response = await client.get(f"/api/tasks?user_id={user_id}")
    tasks = response.json()
    assert len(tasks) == 0
