from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.sqlite_database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


# 这里就是先创建数据库连接，然后把 db 扔出去。
# yield 是生成器，用于 FastAPI Depends 生命周期管理。
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
