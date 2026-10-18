from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=ApiResponse[List[schemas.Course]])
def get_courses(db: Session = Depends(get_db)):
    items = db.query(models.Course).all()
    return ok([schemas.Course.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Course])
def create_course(c: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_c = models.Course(id=str(uuid.uuid4()), **c.model_dump())
    db.add(db_c)
    db.commit()
    db.refresh(db_c)
    return ok(schemas.Course.model_validate(db_c).model_dump(), message="Course created")


@router.put("/{id}", response_model=ApiResponse[schemas.Course])
def update_course(id: str, c: schemas.CourseBase, db: Session = Depends(get_db)):
    db_c = db.query(models.Course).filter(models.Course.id == id).first()
    if not db_c:
        err("Course not found", status_code=404)
    for key, value in c.model_dump(exclude_unset=True).items():
        setattr(db_c, key, value)
    db.commit()
    db.refresh(db_c)
    return ok(schemas.Course.model_validate(db_c).model_dump(), message="Course updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_course(id: str, db: Session = Depends(get_db)):
    db_c = db.query(models.Course).filter(models.Course.id == id).first()
    if not db_c:
        err("Course not found", status_code=404)
    db.delete(db_c)
    db.commit()
    return ok(None, message="Course deleted")
