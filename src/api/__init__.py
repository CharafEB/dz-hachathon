from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from api.core import http_exception_handler, validation_exception_handler
from api import buildings, departments, levels, rooms, teachers, groups, courses, timeslots, sessions, timetable, auth_routes

app = FastAPI(
    title="Timetable Scheduling API",
    description="RESTful API for managing university timetable entities and generating schedules.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(buildings.router)
app.include_router(departments.router)
app.include_router(levels.router)
app.include_router(rooms.router)
app.include_router(teachers.router)
app.include_router(groups.router)
app.include_router(courses.router)
app.include_router(timeslots.router)
app.include_router(sessions.router)
app.include_router(timetable.router)
app.include_router(auth_routes.router)
