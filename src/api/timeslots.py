from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/timeslots", tags=["TimeSlots"])


@router.get("", response_model=ApiResponse[List[schemas.TimeSlot]])
def get_timeslots(db: Session = Depends(get_db)):
    items = db.query(models.TimeSlot).all()
    return ok([schemas.TimeSlot.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.TimeSlot])
def create_timeslot(ts: schemas.TimeSlotCreate, db: Session = Depends(get_db)):
    db_ts = models.TimeSlot(id=str(uuid.uuid4()), **ts.model_dump())
    db.add(db_ts)
    db.commit()
    db.refresh(db_ts)
    return ok(schemas.TimeSlot.model_validate(db_ts).model_dump(), message="TimeSlot created")


@router.put("/{id}", response_model=ApiResponse[schemas.TimeSlot])
def update_timeslot(id: str, ts: schemas.TimeSlotBase, db: Session = Depends(get_db)):
    db_ts = db.query(models.TimeSlot).filter(models.TimeSlot.id == id).first()
    if not db_ts:
        err("TimeSlot not found", status_code=404)
    for key, value in ts.model_dump(exclude_unset=True).items():
        setattr(db_ts, key, value)
    db.commit()
    db.refresh(db_ts)
    return ok(schemas.TimeSlot.model_validate(db_ts).model_dump(), message="TimeSlot updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_timeslot(id: str, db: Session = Depends(get_db)):
    db_ts = db.query(models.TimeSlot).filter(models.TimeSlot.id == id).first()
    if not db_ts:
        err("TimeSlot not found", status_code=404)
    db.delete(db_ts)
    db.commit()
    return ok(None, message="TimeSlot deleted")
