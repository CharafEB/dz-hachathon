from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Any
import uuid

from database import get_db
import models
from auth import hash_password, verify_password, create_access_token, get_current_user, decode_token
from api.core import ok, err, ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "teacher"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool


class LoginResponse(BaseModel):
    token: str
    user: UserOut


@router.post(
    "/register",
    response_model=ApiResponse[LoginResponse],
    summary="Register a new user",
    description="Creates a new user account and returns an authentication token upon success."
)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.
    
    - **email**: Valid email address
    - **password**: Strong password
    - **role**: Either 'admin' or 'teacher' (defaults to 'teacher')
    
    Automatically logs in the user after registration by returning a JWT token.
    """
    if db.query(models.User).filter(models.User.email == req.email).first():
        err("Email already registered", status_code=400)
    
    try:
        role = models.UserRole(req.role)
    except ValueError:
        err(f"Invalid role '{req.role}'. Must be 'admin' or 'teacher'.", status_code=400)
    
    user = models.User(
        id=str(uuid.uuid4()),
        email=req.email,
        hashed_password=hash_password(req.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token immediately for the new user
    token = create_access_token({"sub": user.id, "role": user.role.value})
    
    return ok(
        LoginResponse(
            token=token,
            user=UserOut(id=user.id, email=user.email, role=user.role.value, is_active=user.is_active)
        ),
        message="User registered and logged in successfully",
    )


@router.post(
    "/login",
    response_model=ApiResponse[LoginResponse],
    summary="User Login",
    description="Authenticates a user and returns a JWT access token."
)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user using email and password.
    
    Returns a Bearer token that must be included in the Authorization header 
    for protected endpoints.
    """
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        err("Invalid email or password", status_code=401)
    
    if not user.is_active:
        err("Account is disabled", status_code=403)
    
    token = create_access_token({"sub": user.id, "role": user.role.value})
    
    return ok(
        LoginResponse(
            token=token,
            user=UserOut(id=user.id, email=user.email, role=user.role.value, is_active=user.is_active)
        ),
        message="Login successful",
    )


@router.get(
    "/me",
    response_model=ApiResponse[dict],
    summary="Get Token Details",
    description="Decodes the provided JWT token and returns the payload (claims)."
)
def me(authorization: str = Header(...)):
    """
    Decodes the Bearer token provided in the Authorization header.
    
    Returns the raw JWT payload (claims) such as user ID (`sub`), role, and expiration.
    """
    if not authorization.startswith("Bearer "):
        err("Invalid authorization header format", status_code=401)
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    
    return ok(
        payload,
        message="Token decoded successfully",
    )
