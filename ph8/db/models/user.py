from datetime import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import mapped_column, Mapped
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = mapped_column(String, primary_key=True, autoincrement=False)
    create_at: Mapped[datetime] = mapped_column(insert_default=func.now())
