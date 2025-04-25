import os
from datetime import timedelta
from authx import AuthXConfig, AuthX
from fastapi import FastAPI

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

security = AuthX(config=config)


@app.post("/auth/register", response_model=UserRead)
async def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.password_hasher.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
