import json
import os
import sys

# Define base path to ensure we can run from anywhere
sys.path.append(os.path.join(os.path.dirname(__file__)))

from database import engine, SessionLocal, Base
from models import Department, Level, Building, Room, Teacher, Group, Course, TimeSlot, Session, RoomType, SessionType

def migrate_data():
    print("Initializing Database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    filepath = os.path.join(os.path.dirname(__file__), "data.json")
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return

    print("Loading data from JSON...")
    with open(filepath, "r") as f:
        data = json.load(f)

    # 1. Departments and Levels
    print("Migrating Departments and Levels...")
    for dep_data in data.get("departments", []):
        dep = db.query(Department).filter(Department.id == dep_data["id"]).first()
        if not dep:
            dep = Department(id=dep_data["id"], name=dep_data["name"], code=dep_data["id"].replace("DEP-", ""))
            db.add(dep)
        
        for lvl_name in dep_data.get("levels", []):
            lvl_id = f"{dep_data['id']}-{lvl_name}"
            lvl = db.query(Level).filter(Level.id == lvl_id).first()
            if not lvl:
                lvl = Level(id=lvl_id, name=lvl_name, department_id=dep_data["id"])
                db.add(lvl)
    
    db.commit()

    # 2. Buildings and Rooms
    print("Migrating Buildings and Rooms...")
    for b_data in data.get("buildings", []):
        b = db.query(Building).filter(Building.id == b_data["id"]).first()
        if not b:
            b = Building(id=b_data["id"], name=b_data["name"], location=b_data.get("location", ""), number_of_rooms=0)
            db.add(b)
    db.commit()

    for r_data in data.get("rooms", []):
        r = db.query(Room).filter(Room.id == r_data["id"]).first()
        if not r:
            rtype = RoomType.CLASSROOM
            if "Amphi" in r_data.get("room_type", ""): rtype = RoomType.AMPHITHEATRE
            if "Lab" in r_data.get("room_type", ""): rtype = RoomType.LAB

            r = Room(
                id=r_data["id"],
                code=r_data["code"],
                name=r_data["name"],
                building_id=r_data["building_id"],
                capacity=r_data["capacity"],
                type=rtype
            )
            db.add(r)
    db.commit()

    # 3. Teachers
    print("Migrating Teachers...")
    for t_data in data.get("teachers", []):
        t = db.query(Teacher).filter(Teacher.id == t_data["id"]).first()
        if not t:
            t = Teacher(
                id=t_data["id"],
                name=t_data["name"],
                email=f"{t_data['id'].lower()}@univ.edu",
                max_hours=t_data.get("max_hours", 9.0),
                specializations=t_data.get("specializations", []),
                unavailable_slots=t_data.get("unavailable_slots", [])
            )
            db.add(t)
    db.commit()

    # 4. Groups
    print("Migrating Groups...")
    for g_data in data.get("groups", []):
        g = db.query(Group).filter(Group.id == g_data["id"]).first()
        if not g:
            # Reconstruct level_id from group id or from data mapping
            # Group ID is DEP-CS-L1-G1 typically, so DEP-CS-L1 is the level ID
            level_id = "-".join(g_data["id"].split("-")[:3])
            
            # Since subgroups aren't a distinct model mapped to DB, we skip them.
            # Subgroups are targeted in sessions via a generic string target.
            
            # Approximate headcount or calculate
            headcount = sum(sg["size"] for sg in g_data.get("sub_groups", [])) if "sub_groups" in g_data else 100

            g = Group(
                id=g_data["id"],
                name=g_data["name"],
                level_id=level_id,
                headcount=headcount
            )
            db.add(g)
    db.commit()

    # 5. Courses
    print("Migrating Courses...")
    for c_data in data.get("courses", []):
        c = db.query(Course).filter(Course.id == c_data["id"]).first()
        if not c:
            level_id = f"{c_data['department_id']}-{c_data['level']}"
            c = Course(
                id=c_data["id"],
                name=c_data["name"],
                code=c_data["code"],
                level_id=level_id,
                num_lectures=c_data.get("lectures_per_week", 1),
                num_td=c_data.get("tds_per_week", 0),
                num_tp=c_data.get("tps_per_week", 0)
            )
            db.add(c)
    db.commit()

    # 6. Sessions (Session Requirements from JSON)
    print("Migrating Sessions...")
    for req_data in data.get("session_requirements", []):
        s = db.query(Session).filter(Session.id == req_data["id"]).first()
        if not s:
            stype = SessionType.LECTURE
            if req_data.get("session_type") == "TD": stype = SessionType.TD
            if req_data.get("session_type") == "TP": stype = SessionType.TP
            
            s = Session(
                id=req_data["id"],
                course_id=req_data["course_id"],
                type=stype,
                teacher_id=req_data["teacher_id"],
                group_id=req_data["target_id"],
                room_id=None,
                timeslot_id=None
            )
            db.add(s)
    db.commit()

    # 7. Add default timeslots if none exist
    print("Migrating TimeSlots...")
    for day in ["MON", "TUE", "WED", "THU", "FRI"]:
        for slot in range(5):
            ts_id = f"{day}-{slot}"
            ts = db.query(TimeSlot).filter(TimeSlot.id == ts_id).first()
            if not ts:
                ts = TimeSlot(
                    id=ts_id,
                    day=day,
                    start_time=f"{8 + slot * 2}:00",
                    end_time=f"{9 + slot * 2}:30",
                    slot_index=slot
                )
                db.add(ts)
    db.commit()

    print("Data Migration Complete! All items from JSON are now in SQLite.")

if __name__ == "__main__":
    migrate_data()
