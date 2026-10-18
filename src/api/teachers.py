from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("", response_model=ApiResponse[List[schemas.Teacher]])
def get_teachers(db: Session = Depends(get_db)):
    items = db.query(models.Teacher).all()
    return ok([schemas.Teacher.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Teacher])
def create_teacher(t: schemas.TeacherCreate, db: Session = Depends(get_db)):
    db_t = models.Teacher(id=str(uuid.uuid4()), **t.model_dump())
    db.add(db_t)
    db.commit()
    db.refresh(db_t)
    return ok(schemas.Teacher.model_validate(db_t).model_dump(), message="Teacher created")


@router.put("/{id}", response_model=ApiResponse[schemas.Teacher])
def update_teacher(id: str, t: schemas.TeacherBase, db: Session = Depends(get_db)):
    db_t = db.query(models.Teacher).filter(models.Teacher.id == id).first()
    if not db_t:
        err("Teacher not found", status_code=404)
    for key, value in t.model_dump(exclude_unset=True).items():
        setattr(db_t, key, value)
    db.commit()
    db.refresh(db_t)
    return ok(schemas.Teacher.model_validate(db_t).model_dump(), message="Teacher updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_teacher(id: str, db: Session = Depends(get_db)):
    db_t = db.query(models.Teacher).filter(models.Teacher.id == id).first()
    if not db_t:
        err("Teacher not found", status_code=404)
    db.delete(db_t)
    db.commit()
    return ok(None, message="Teacher deleted")
