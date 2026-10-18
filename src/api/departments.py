from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
import schemas
from api.core import ok, err, ApiResponse
from typing import List

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=ApiResponse[List[schemas.Department]])
def get_departments(db: Session = Depends(get_db)):
    items = db.query(models.Department).all()
    return ok([schemas.Department.model_validate(i).model_dump() for i in items], count=len(items))


@router.post("", response_model=ApiResponse[schemas.Department])
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    db_dept = models.Department(id=str(uuid.uuid4()), **dept.model_dump())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return ok(schemas.Department.model_validate(db_dept).model_dump(), message="Department created")


@router.put("/{id}", response_model=ApiResponse[schemas.Department])
def update_department(id: str, dept: schemas.DepartmentBase, db: Session = Depends(get_db)):
    db_dept = db.query(models.Department).filter(models.Department.id == id).first()
    if not db_dept:
        err("Department not found", status_code=404)
    for key, value in dept.model_dump(exclude_unset=True).items():
        setattr(db_dept, key, value)
    db.commit()
    db.refresh(db_dept)
    return ok(schemas.Department.model_validate(db_dept).model_dump(), message="Department updated")


@router.delete("/{id}", response_model=ApiResponse[None])
def delete_department(id: str, db: Session = Depends(get_db)):
    db_dept = db.query(models.Department).filter(models.Department.id == id).first()
    if not db_dept:
        err("Department not found", status_code=404)
    db.delete(db_dept)
    db.commit()
    return ok(None, message="Department deleted")
