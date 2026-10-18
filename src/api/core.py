from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    count: Optional[int] = None
    totalPages: Optional[int] = None
    error: Optional[str] = None


def ok(data: Any, message: str = "Success", count: Optional[int] = None) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
        "count": count,
    }


def err(message: str, error: str = None, status_code: int = 400):
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "message": message,
            "error": error or message,
            "data": None,
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={
        "success": False,
        "message": exc.detail,
        "error": exc.detail,
        "data": None,
    })


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={
        "success": False,
        "message": "Validation error",
        "error": str(exc.errors()),
        "data": None,
    })
