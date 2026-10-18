from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("", response_model=ApiResponse[List[schemas.Building]])
def get_buildings(db: Session = Depends(get_db)):
    items = db.query(models.Building).all()
    return ok([schemas.Building.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Building])
def create_building(b: schemas.BuildingCreate, db: Session = Depends(get_db)):
    db_b = models.Building(id=str(uuid.uuid4()), **b.model_dump())
    db.add(db_b)
    db.commit()
    db.refresh(db_b)
    return ok(schemas.Building.model_validate(db_b).model_dump(), message="Building created")


@router.put("/{id}", response_model=ApiResponse[schemas.Building])
def update_building(id: str, b: schemas.BuildingBase, db: Session = Depends(get_db)):
    db_b = db.query(models.Building).filter(models.Building.id == id).first()
    if not db_b:
        err("Building not found", status_code=404)
    for key, value in b.model_dump(exclude_unset=True).items():
        setattr(db_b, key, value)
    db.commit()
    db.refresh(db_b)
    return ok(schemas.Building.model_validate(db_b).model_dump(), message="Building updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_building(id: str, db: Session = Depends(get_db)):
    db_b = db.query(models.Building).filter(models.Building.id == id).first()
    if not db_b:
        err("Building not found", status_code=404)
    db.delete(db_b)
    db.commit()
    return ok(None, message="Building deleted")
