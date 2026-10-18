from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from models import RoomType, SessionType

class BuildingBase(BaseModel):
    name: str
    location: Optional[str] = None
    number_of_rooms: int = 0

class BuildingCreate(BuildingBase):
    pass  # id is auto-generated

class Building(BuildingBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class RoomBase(BaseModel):
    code: str
    name: Optional[str] = None
    building_id: Optional[str] = None
    type: RoomType
    capacity: int

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: str
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class DepartmentBase(BaseModel):
    name: str
    code: str

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class LevelBase(BaseModel):
    name: str
    department_id: str

class LevelCreate(LevelBase):
    pass

class Level(LevelBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class GroupBase(BaseModel):
    name: str
    level_id: str
    headcount: int

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class TeacherBase(BaseModel):
    name: str
    email: str
    max_hours: float = 9.0
    specializations: List[str] = []
    unavailable_slots: List[str] = []

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class CourseBase(BaseModel):
    name: str
    code: str
    level_id: str
    num_lectures: int = 1
    num_td: int = 1
    num_tp: int = 0

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class TimeSlotBase(BaseModel):
    day: str
    start_time: str
    end_time: str
    slot_index: int

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlot(TimeSlotBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class SessionBase(BaseModel):
    course_id: str
    type: SessionType
    teacher_id: str
    group_id: str
    room_id: Optional[str] = None
    timeslot_id: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: str
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class SessionDetailed(SessionBase):
    id: str
    course: Course
    teacher: Teacher
    room: Optional[Room] = None
    timeslot: Optional[TimeSlot] = None

    model_config = ConfigDict(from_attributes=True)
