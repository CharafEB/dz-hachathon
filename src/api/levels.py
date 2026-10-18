from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/levels", tags=["Levels"])


@router.get("", response_model=ApiResponse[List[schemas.Level]])
def get_levels(db: Session = Depends(get_db)):
    items = db.query(models.Level).all()
    return ok([schemas.Level.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Level])
def create_level(level: schemas.LevelCreate, db: Session = Depends(get_db)):
    db_lvl = models.Level(id=str(uuid.uuid4()), **level.model_dump())
    db.add(db_lvl)
    db.commit()
    db.refresh(db_lvl)
    return ok(schemas.Level.model_validate(db_lvl).model_dump(), message="Level created")


@router.put("/{id}", response_model=ApiResponse[schemas.Level])
def update_level(id: str, level: schemas.LevelBase, db: Session = Depends(get_db)):
    db_lvl = db.query(models.Level).filter(models.Level.id == id).first()
    if not db_lvl:
        err("Level not found", status_code=404)
    for key, value in level.model_dump(exclude_unset=True).items():
        setattr(db_lvl, key, value)
    db.commit()
    db.refresh(db_lvl)
    return ok(schemas.Level.model_validate(db_lvl).model_dump(), message="Level updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_level(id: str, db: Session = Depends(get_db)):
    db_lvl = db.query(models.Level).filter(models.Level.id == id).first()
    if not db_lvl:
        err("Level not found", status_code=404)
    db.delete(db_lvl)
    db.commit()
    return ok(None, message="Level deleted")
