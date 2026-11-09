
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    blogs: Mapped[list["Blog"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic: Mapped[str] = mapped_column(
        String(300), nullable=False
    )
    title: Mapped[str | None] = mapped_column(
        String(300), nullable=True
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, default=""
    )
    tone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Professional"
    )
    audience: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    length: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Medium"
    )
    language: Mapped[str] = mapped_column(
        String(50), nullable=False, default="English"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        back_populates="blogs"
    )
