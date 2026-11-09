
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Blog, User

router = APIRouter(prefix="/api/blogs", tags=["Blog History"])


class BlogCreateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=300)
    content: str = Field(min_length=1, max_length=100000)
    title: str | None = Field(default=None, max_length=300)
    tone: str = Field(default="Professional", max_length=50)
    audience: str | None = Field(default=None, max_length=200)
    length: str = Field(default="Medium", max_length=30)
    language: str = Field(default="English", max_length=50)


class BlogUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    content: str | None = Field(default=None, min_length=1, max_length=100000)


def serialize_blog(blog: Blog) -> dict:
    return {
        "id": blog.id,
        "user_id": blog.user_id,
        "topic": blog.topic,
        "title": blog.title,
        "content": blog.content,
        "tone": blog.tone,
        "audience": blog.audience,
        "length": blog.length,
        "language": blog.language,
        "created_at": blog.created_at.isoformat() if blog.created_at else None,
        "updated_at": blog.updated_at.isoformat() if blog.updated_at else None,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def save_blog(
    request: BlogCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = Blog(
        user_id=current_user.id,
        topic=request.topic.strip(),
        title=request.title.strip() if request.title else None,
        content=request.content,
        tone=request.tone,
        audience=request.audience,
        length=request.length,
        language=request.language,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return {
        "message": "Blog saved successfully.",
        "blog": serialize_blog(blog),
    }


@router.get("")
def list_blogs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Blog)
        .where(Blog.user_id == current_user.id)
        .order_by(Blog.created_at.desc(), Blog.id.desc())
        .offset(offset)
        .limit(limit)
    )

    blogs = db.scalars(statement).all()

    return {
        "items": [serialize_blog(blog) for blog in blogs],
        "limit": limit,
        "offset": offset,
    }


@router.get("/{blog_id}")
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.scalar(
        select(Blog).where(
            Blog.id == blog_id,
            Blog.user_id == current_user.id,
        )
    )

    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found.",
        )

    return serialize_blog(blog)


@router.patch("/{blog_id}")
def update_blog(
    blog_id: int,
    request: BlogUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    changes = request.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide a title or content to update.",
        )

    blog = db.scalar(
        select(Blog).where(
            Blog.id == blog_id,
            Blog.user_id == current_user.id,
        )
    )

    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found.",
        )

    if "title" in changes and changes["title"] is not None:
        blog.title = changes["title"].strip() or None

    if "content" in changes and changes["content"] is not None:
        blog.content = changes["content"]

    db.commit()
    db.refresh(blog)

    return {
        "message": "Blog updated successfully.",
        "blog": serialize_blog(blog),
    }


@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.scalar(
        select(Blog).where(
            Blog.id == blog_id,
            Blog.user_id == current_user.id,
        )
    )

    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found.",
        )

    db.delete(blog)
    db.commit()

    return {"message": "Blog deleted successfully.", "id": blog_id}
