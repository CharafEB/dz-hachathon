from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("", response_model=ApiResponse[List[schemas.Group]])
def get_groups(db: Session = Depends(get_db)):
    items = db.query(models.Group).all()
    return ok([schemas.Group.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Group])
def create_group(g: schemas.GroupCreate, db: Session = Depends(get_db)):
    db_g = models.Group(id=str(uuid.uuid4()), **g.model_dump())
    db.add(db_g)
    db.commit()
    db.refresh(db_g)
    return ok(schemas.Group.model_validate(db_g).model_dump(), message="Group created")


@router.put("/{id}", response_model=ApiResponse[schemas.Group])
def update_group(id: str, g: schemas.GroupBase, db: Session = Depends(get_db)):
    db_g = db.query(models.Group).filter(models.Group.id == id).first()
    if not db_g:
        err("Group not found", status_code=404)
    for key, value in g.model_dump(exclude_unset=True).items():
        setattr(db_g, key, value)
    db.commit()
    db.refresh(db_g)
    return ok(schemas.Group.model_validate(db_g).model_dump(), message="Group updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_group(id: str, db: Session = Depends(get_db)):
    db_g = db.query(models.Group).filter(models.Group.id == id).first()
    if not db_g:
        err("Group not found", status_code=404)
    db.delete(db_g)
    db.commit()
    return ok(None, message="Group deleted")
