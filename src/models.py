import json
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, Enum, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base

class RoomType(str, PyEnum):
    AMPHITHEATRE = "Amphitheatre"
    CLASSROOM = "Classroom"
    LAB = "Lab"

class SessionType(str, PyEnum):
    LECTURE = "Lecture"
    TD = "TD"
    TP = "TP"

class UserRole(str, PyEnum):
    ADMIN = "admin"
    TEACHER = "teacher"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.TEACHER, nullable=False)
    is_active = Column(Boolean, default=True)

class Building(Base):
    __tablename__ = "buildings"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    number_of_rooms = Column(Integer, default=0)
    
    rooms = relationship("Room", back_populates="building")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(String, primary_key=True, index=True)
    code = Column(String, nullable=False)
    name = Column(String)
    building_id = Column(String, ForeignKey("buildings.id"))
    type = Column(Enum(RoomType))
    capacity = Column(Integer)

    building = relationship("Building", back_populates="rooms")

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True)
    
    levels = relationship("Level", back_populates="department")

class Level(Base):
    __tablename__ = "levels"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False) # e.g. L1, L2, etc.
    department_id = Column(String, ForeignKey("departments.id"))
    
    department = relationship("Department", back_populates="levels")
    groups = relationship("Group", back_populates="level")
    courses = relationship("Course", back_populates="level")

class Group(Base):
    __tablename__ = "groups"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    level_id = Column(String, ForeignKey("levels.id"))
    headcount = Column(Integer)
    
    level = relationship("Level", back_populates="groups")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    max_hours = Column(Float, default=9.0)
    specializations = Column(JSON) # Stores list of strings
    unavailable_slots = Column(JSON) # e.g. ["MON-0"]

class Course(Base):
    __tablename__ = "courses"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True)
    level_id = Column(String, ForeignKey("levels.id"))
    num_lectures = Column(Integer, default=1)
    num_td = Column(Integer, default=1)
    num_tp = Column(Integer, default=0)
    
    level = relationship("Level", back_populates="courses")

class TimeSlot(Base):
    __tablename__ = "timeslots"
    id = Column(String, primary_key=True, index=True)
    day = Column(String) # MON, TUE...
    start_time = Column(String)
    end_time = Column(String)
    slot_index = Column(Integer)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True)
    course_id = Column(String, ForeignKey("courses.id"))
    type = Column(Enum(SessionType))
    teacher_id = Column(String, ForeignKey("teachers.id"))
    group_id = Column(String) # Can be Group ID or Subgroup ID (stored as string for flexibility)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=True)
    timeslot_id = Column(String, ForeignKey("timeslots.id"), nullable=True)
    
    course = relationship("Course")
    teacher = relationship("Teacher")
    room = relationship("Room")
    timeslot = relationship("TimeSlot")

