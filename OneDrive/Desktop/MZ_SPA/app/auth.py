from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException, Depends, Response
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .database import SessionLocal
from .schemas import UserCreate, UserResponse
from fastapi import Depends

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Регистрация пользователя
@router.post(
    "/registration", 
    response_model=UserResponse, 
    status_code=201, 
    summary="Регистрация нового пользователя", 
    responses={
        201: {"description": "Пользователь успешно зарегистрирован"},
        409: {"description": "Пользователь с таким логином уже существует"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def registration(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.login == user_data.login))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=409, detail="User with this login already exists")

    user = User(login=user_data.login, password=get_password_hash(user_data.password))
    db.add(user)
    await db.commit()
    return UserResponse(user_id=user.user_id, login=user.login)

# Авторизация пользователя
@router.post(
    "/auth", 
    response_model=UserResponse, 
    summary="Авторизация пользователя", 
    responses={
        200: {"description": "Пользователь успешно авторизован"},
        401: {"description": "Неверные учетные данные"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def auth(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.login == user_data.login))
    user = result.scalars().first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return UserResponse(user_id=user.user_id, login=user.login)

# Выход из системы
@router.post(
    "/logout", 
    summary="Выход из аккаунта пользователя", 
    status_code=204, 
    response_class=Response,
    responses={
        204: {"description": "Пользователь успешно вышел из системы"},
        422: {"description": "Некорректный формат запроса"}
    }
)
async def logout():
    return Response(status_code=204)
