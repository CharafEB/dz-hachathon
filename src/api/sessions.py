from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", response_model=ApiResponse[List[schemas.Session]])
def get_sessions(db: Session = Depends(get_db)):
    items = db.query(models.Session).all()
    return ok([schemas.Session.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Session])
def create_session(s: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_s = models.Session(id=str(uuid.uuid4()), **s.model_dump())
    db.add(db_s)
    db.commit()
    db.refresh(db_s)
    return ok(schemas.Session.model_validate(db_s).model_dump(), message="Session created")


@router.put("/{id}", response_model=ApiResponse[schemas.Session])
def update_session(id: str, s: schemas.SessionBase, db: Session = Depends(get_db)):
    db_s = db.query(models.Session).filter(models.Session.id == id).first()
    if not db_s:
        err("Session not found", status_code=404)
    for key, value in s.model_dump(exclude_unset=True).items():
        setattr(db_s, key, value)
    db.commit()
    db.refresh(db_s)
    return ok(schemas.Session.model_validate(db_s).model_dump(), message="Session updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_session(id: str, db: Session = Depends(get_db)):
    db_s = db.query(models.Session).filter(models.Session.id == id).first()
    if not db_s:
        err("Session not found", status_code=404)
    db.delete(db_s)
    db.commit()
    return ok(None, message="Session deleted")
