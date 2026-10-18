import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import Base, get_db
from api import app
from models import Building, Room, Teacher, Department, Level, Group, Course, TimeSlot, Session

from sqlalchemy.pool import StaticPool

# --- SETUP IN-MEMORY DB FOR TESTING ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_db():
    pass

# Helper: unwrap standard API envelope
def data(response):
    return response.json()["data"]

# --- TESTS ---

def test_create_building():
    payload = {"name": "Building 1", "location": "Main Campus", "number_of_rooms": 10}
    response = client.post("/buildings", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert data(response)["name"] == "Building 1"
    # Store generated id for later tests
    pytest.building_id = data(response)["id"]

def test_update_building():
    bid = pytest.building_id
    payload = {"name": "Updated Building 1", "location": "North Campus", "number_of_rooms": 15}
    response = client.put(f"/buildings/{bid}", json=payload)
    assert response.status_code == 200
    assert data(response)["name"] == "Updated Building 1"

    # Negative test
    response_404 = client.put("/buildings/invalid", json=payload)
    assert response_404.status_code == 404
    assert response_404.json()["success"] is False

def test_get_buildings():
    response = client.get("/buildings")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(data(response)) >= 1

def test_create_department():
    payload = {"name": "Computer Science", "code": "CS"}
    response = client.post("/departments", json=payload)
    assert response.status_code == 200
    assert data(response)["code"] == "CS"
    pytest.dept_id = data(response)["id"]

def test_update_department():
    payload = {"name": "Information Technology", "code": "IT"}
    response = client.put(f"/departments/{pytest.dept_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["name"] == "Information Technology"

def test_create_level():
    payload = {"name": "L1", "department_id": pytest.dept_id}
    response = client.post("/levels", json=payload)
    assert response.status_code == 200
    assert data(response)["name"] == "L1"
    pytest.level_id = data(response)["id"]

def test_update_level():
    payload = {"name": "Year 2", "department_id": pytest.dept_id}
    response = client.put(f"/levels/{pytest.level_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["name"] == "Year 2"

def test_create_room():
    payload = {
        "code": "R101", "name": "Room 101",
        "building_id": pytest.building_id, "type": "Classroom", "capacity": 30
    }
    response = client.post("/rooms", json=payload)
    assert response.status_code == 200
    assert data(response)["code"] == "R101"
    pytest.room_id = data(response)["id"]

def test_update_room():
    payload = {"code": "R102", "name": "Room 102", "building_id": pytest.building_id, "type": "Lab", "capacity": 40}
    response = client.put(f"/rooms/{pytest.room_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["type"] == "Lab"

def test_create_teacher():
    payload = {
        "name": "John Doe", "email": "john@univ.edu",
        "max_hours": 9.0, "specializations": ["CS", "AI"]
    }
    response = client.post("/teachers", json=payload)
    assert response.status_code == 200
    assert data(response)["name"] == "John Doe"
    pytest.teacher_id = data(response)["id"]

def test_update_teacher():
    payload = {
        "name": "Jane Doe", "email": "jane@univ.edu",
        "max_hours": 12.0, "specializations": ["Networking"],
        "unavailable_slots": ["MON-1"]
    }
    response = client.put(f"/teachers/{pytest.teacher_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["name"] == "Jane Doe"

def test_create_group():
    payload = {"name": "Group A", "level_id": pytest.level_id, "headcount": 60}
    response = client.post("/groups", json=payload)
    assert response.status_code == 200
    assert data(response)["headcount"] == 60
    pytest.group_id = data(response)["id"]

def test_update_group():
    payload = {"name": "Class B", "level_id": pytest.level_id, "headcount": 45}
    response = client.put(f"/groups/{pytest.group_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["headcount"] == 45

def test_create_course():
    payload = {
        "name": "Python 101", "code": "PY101",
        "level_id": pytest.level_id, "num_lectures": 2, "num_td": 1
    }
    response = client.post("/courses", json=payload)
    assert response.status_code == 200
    assert data(response)["code"] == "PY101"
    pytest.course_id = data(response)["id"]

def test_update_course():
    payload = {
        "name": "Advanced Python", "code": "PY201",
        "level_id": pytest.level_id, "num_lectures": 1, "num_td": 2, "num_tp": 1
    }
    response = client.put(f"/courses/{pytest.course_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["num_tp"] == 1

def test_create_timeslot():
    payload = {"day": "MON", "start_time": "08:00", "end_time": "09:30", "slot_index": 0}
    response = client.post("/timeslots", json=payload)
    assert response.status_code == 200
    assert data(response)["day"] == "MON"
    pytest.ts_id = data(response)["id"]

def test_update_timeslot():
    payload = {"day": "TUE", "start_time": "10:00", "end_time": "11:30", "slot_index": 1}
    response = client.put(f"/timeslots/{pytest.ts_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["day"] == "TUE"

def test_create_session():
    payload = {
        "course_id": pytest.course_id, "type": "Lecture",
        "teacher_id": pytest.teacher_id, "group_id": pytest.group_id
    }
    response = client.post("/sessions", json=payload)
    assert response.status_code == 200
    assert data(response)["type"] == "Lecture"
    pytest.session_id = data(response)["id"]

def test_update_session():
    payload = {
        "course_id": pytest.course_id, "type": "TD", "teacher_id": pytest.teacher_id,
        "group_id": pytest.group_id, "room_id": pytest.room_id, "timeslot_id": pytest.ts_id
    }
    response = client.put(f"/sessions/{pytest.session_id}", json=payload)
    assert response.status_code == 200
    assert data(response)["type"] == "TD"
    assert data(response)["room_id"] == pytest.room_id

# --- LIST GET TESTS ---

def test_get_departments():
    response = client.get("/departments")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert len(data(response)) >= 1
    assert "code" in data(response)[0]

def test_get_levels():
    response = client.get("/levels")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert len(data(response)) >= 1

def test_get_rooms():
    response = client.get("/rooms")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert any(r["id"] == pytest.room_id for r in data(response))

def test_get_teachers():
    response = client.get("/teachers")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert any(t["id"] == pytest.teacher_id for t in data(response))

def test_get_groups():
    response = client.get("/groups")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert any(g["id"] == pytest.group_id for g in data(response))

def test_get_courses():
    response = client.get("/courses")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert any(c["id"] == pytest.course_id for c in data(response))

def test_get_timeslots():
    response = client.get("/timeslots")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert any(t["id"] == pytest.ts_id for t in data(response))

def test_get_sessions():
    response = client.get("/sessions")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(data(response), list)
    assert any(s["id"] == pytest.session_id for s in data(response))

def test_count_field_on_list_endpoints():
    """Verify the count field matches the actual number of items returned."""
    for endpoint in ["/buildings", "/departments", "/levels", "/rooms",
                     "/teachers", "/groups", "/courses", "/timeslots", "/sessions"]:
        resp = client.get(endpoint)
        assert resp.status_code == 200
        body = resp.json()
        assert body["count"] == len(body["data"])

def test_get_timetable():
    """
    Timetable should return 200 with the correct hierarchical structure.
    With a scheduled session in DB, at least one department should appear.
    """
    response = client.get("/timetable")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "departments" in body["data"]
    assert "meta" in body["data"]
    meta = body["data"]["meta"]
    assert "total_sessions" in meta
    assert "scheduled" in meta
    assert "unscheduled" in meta
    assert meta["total_sessions"] == meta["scheduled"] + meta["unscheduled"]

def test_get_timetable_regenerate():
    """regenerate=true should still return a valid 200 response."""
    response = client.get("/timetable?regenerate=true")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "departments" in body["data"]

def test_timetable_schedule_structure():
    """
    Any group in the timetable with a scheduled session should have
    the correct slot structure (slot_index, start_time, end_time, session).
    """
    response = client.get("/timetable")
    assert response.status_code == 200
    timetable = response.json()["data"]

    for dept in timetable["departments"]:
        for level in dept["levels"]:
            for group in level["groups"]:
                for day, slots in group["schedule"].items():
                    assert day in ["MON", "TUE", "WED", "THU", "FRI"]
                    for slot in slots:
                        assert "slot_index" in slot
                        assert "start_time" in slot
                        assert "end_time" in slot
                        session = slot["session"]
                        assert "id" in session
                        assert "type" in session
                        assert "start_time" in session
                        assert "end_time" in session
                        assert "course" in session
                        assert "teacher" in session
                        assert "room" in session
                        # Verify nested fields
                        assert "name" in session["course"]
                        assert "name" in session["teacher"]
                        assert "code" in session["room"]

def test_delete_session():
    response = client.delete(f"/sessions/{pytest.session_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_delete_timeslot():
    response = client.delete(f"/timeslots/{pytest.ts_id}")
    assert response.status_code == 200

def test_delete_course():
    response = client.delete(f"/courses/{pytest.course_id}")
    assert response.status_code == 200

def test_delete_group():
    response = client.delete(f"/groups/{pytest.group_id}")
    assert response.status_code == 200

def test_delete_teacher():
    response = client.delete(f"/teachers/{pytest.teacher_id}")
    assert response.status_code == 200

def test_delete_room():
    response = client.delete(f"/rooms/{pytest.room_id}")
    assert response.status_code == 200

def test_delete_level():
    response = client.delete(f"/levels/{pytest.level_id}")
    assert response.status_code == 200

def test_delete_department():
    response = client.delete(f"/departments/{pytest.dept_id}")
    assert response.status_code == 200

def test_delete_building():
    response = client.delete(f"/buildings/{pytest.building_id}")
    assert response.status_code == 200
    # Negative test: second delete should be 404
    resp_404 = client.delete(f"/buildings/{pytest.building_id}")
    assert resp_404.status_code == 404
    assert resp_404.json()["success"] is False
