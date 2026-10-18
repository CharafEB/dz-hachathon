from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload, subqueryload

from database import get_db
import models
from api.core import ok, err

router = APIRouter(prefix="/timetable", tags=["Schedule"])

DAYS_ORDER = ["MON", "TUE", "WED", "THU", "FRI"]


@router.get("")
def get_timetable(regenerate: bool = False, db: Session = Depends(get_db)):
    try:
        if regenerate:
            db.query(models.Session).update({"room_id": None, "timeslot_id": None})
            db.commit()

        from scheduler import TimetableScheduler
        TimetableScheduler(db).solve()

        # Scheduled sessions
        scheduled = db.query(models.Session).options(
            joinedload(models.Session.course),
            joinedload(models.Session.teacher),
            joinedload(models.Session.room),
            joinedload(models.Session.timeslot),
        ).filter(
            models.Session.timeslot_id.isnot(None),
            models.Session.room_id.isnot(None),
        ).all()

        # Unscheduled sessions (conflict list)
        unscheduled = db.query(models.Session).options(
            joinedload(models.Session.course),
            joinedload(models.Session.teacher),
        ).filter(
            (models.Session.timeslot_id == None) | (models.Session.room_id == None)
        ).all()

        conflicts = [
            {
                "session_id": s.id,
                "type": s.type.value,
                "course": s.course.name if s.course else None,
                "teacher": s.teacher.name if s.teacher else None,
                "reason": "No available timeslot or room found that satisfies all constraints",
            }
            for s in unscheduled
        ]

        total = len(scheduled) + len(unscheduled)
        scheduled_count = len(scheduled)
        unscheduled_count = len(unscheduled)

        sessions_by_group: dict = {}
        for s in scheduled:
            sessions_by_group.setdefault(s.group_id, []).append(s)

        departments = db.query(models.Department).options(
            subqueryload(models.Department.levels).subqueryload(models.Level.groups),
            subqueryload(models.Department.levels).subqueryload(models.Level.courses),
        ).all()

        result_departments = []
        for dept in departments:
            dept_data = {"id": dept.id, "name": dept.name, "code": dept.code, "levels": []}

            for level in sorted(dept.levels, key=lambda l: l.name):
                level_data = {
                    "id": level.id,
                    "name": level.name,
                    "courses": [
                        {"id": c.id, "name": c.name, "code": c.code,
                         "num_lectures": c.num_lectures, "num_td": c.num_td, "num_tp": c.num_tp}
                        for c in level.courses
                    ],
                    "groups": [],
                }

                for group in sorted(level.groups, key=lambda g: g.name):
                    schedule: dict = {day: [] for day in DAYS_ORDER}

                    for s in sessions_by_group.get(group.id, []):
                        ts = s.timeslot
                        if ts and ts.day in schedule:
                            schedule[ts.day].append({
                                "slot_index": ts.slot_index,
                                "start_time": ts.start_time,
                                "end_time": ts.end_time,
                                "session": {
                                    "id": s.id,
                                    "type": s.type.value,
                                    "start_time": ts.start_time,
                                    "end_time": ts.end_time,
                                    "course": {"id": s.course.id, "name": s.course.name, "code": s.course.code},
                                    "teacher": {"id": s.teacher.id, "name": s.teacher.name, "email": s.teacher.email},
                                    "room": {
                                        "id": s.room.id, "code": s.room.code, "name": s.room.name,
                                        "type": s.room.type.value, "capacity": s.room.capacity,
                                    },
                                },
                            })

                    for day in DAYS_ORDER:
                        schedule[day].sort(key=lambda x: x["slot_index"])

                    level_data["groups"].append({
                        "id": group.id, "name": group.name,
                        "headcount": group.headcount, "schedule": schedule,
                    })

                dept_data["levels"].append(level_data)
            result_departments.append(dept_data)

        if unscheduled_count == total:
            msg = "Timetable could not be generated: no sessions could be scheduled due to constraint conflicts"
        elif unscheduled_count > 0:
            msg = f"Timetable partially generated: {unscheduled_count} session(s) could not be scheduled"
        else:
            msg = "Timetable generated successfully"

        return ok(
            {
                "departments": result_departments,
                "conflicts": conflicts,
                "meta": {
                    "total_sessions": total,
                    "scheduled": scheduled_count,
                    "unscheduled": unscheduled_count,
                },
            },
            message=msg,
            count=scheduled_count,
        )

    except Exception as e:
        err(f"Scheduler error: {str(e)}", status_code=500)
