from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("", response_model=ApiResponse[List[schemas.Room]])
def get_rooms(db: Session = Depends(get_db)):
    items = db.query(models.Room).all()
    return ok([schemas.Room.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Room])
def create_room(r: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_r = models.Room(id=str(uuid.uuid4()), **r.model_dump())
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return ok(schemas.Room.model_validate(db_r).model_dump(), message="Room created")


@router.put("/{id}", response_model=ApiResponse[schemas.Room])
def update_room(id: str, r: schemas.RoomBase, db: Session = Depends(get_db)):
    db_r = db.query(models.Room).filter(models.Room.id == id).first()
    if not db_r:
        err("Room not found", status_code=404)
    for key, value in r.model_dump(exclude_unset=True).items():
        setattr(db_r, key, value)
    db.commit()
    db.refresh(db_r)
    return ok(schemas.Room.model_validate(db_r).model_dump(), message="Room updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_room(id: str, db: Session = Depends(get_db)):
    db_r = db.query(models.Room).filter(models.Room.id == id).first()
    if not db_r:
        err("Room not found", status_code=404)
    db.delete(db_r)
    db.commit()
    return ok(None, message="Room deleted")
