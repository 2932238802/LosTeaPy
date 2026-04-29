from app.db.session import Base, engine
from app.models import User


def init_db() -> None:
    # 本地开发阶段直接自动建表；后续正式环境建议换 Alembic。
    Base.metadata.create_all(bind=engine)
