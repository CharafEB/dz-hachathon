import random
from typing import List, Dict, Optional, Set
from sqlalchemy.orm import Session
from models import Building, Room, Teacher, Department, Level, Group, Course, TimeSlot, Session as SessionModel, RoomType, SessionType

class TimetableScheduler:
    def __init__(self, db: Session):
        self.db = db
        
        # Load all data into memory for the scheduling run
        self.rooms = {r.id: r for r in db.query(Room).all()}
        self.teachers = {t.id: t for t in db.query(Teacher).all()}
        self.groups = {g.id: g for g in db.query(Group).all()}
        self.levels = {l.id: l for l in db.query(Level).all()}
        self.courses = {c.id: c for c in db.query(Course).all()}
        self.timeslots = db.query(TimeSlot).all()
        
        # Map levels to groups for convenience
        self.level_groups = {}
        for g in self.groups.values():
            if g.level_id not in self.level_groups:
                self.level_groups[g.level_id] = []
            self.level_groups[g.level_id].append(g)

    def solve(self, max_iterations=100):
        """Simple Randomized Greedy Solver updated for DB models"""
        
        # In this version, we find all sessions that haven't been assigned a room/timeslot yet
        unscheduled = self.db.query(SessionModel).filter(
            (SessionModel.room_id == None) | (SessionModel.timeslot_id == None)
        ).all()
        
        if not unscheduled:
            print("All sessions are already scheduled.")
            return []

        # State tracking
        days = sorted(list(set(ts.day for ts in self.timeslots)))
        slots = sorted(list(set(ts.slot_index for ts in self.timeslots)))
        
        # teacher_busy[day][slot] = set of teacher IDs
        teacher_busy = {d: {s: set() for s in slots} for d in days}
        room_busy = {d: {s: set() for s in slots} for d in days}
        group_busy = {d: {s: set() for s in slots} for d in days}
        
        # Load existing schedule to avoid conflicts
        scheduled = self.db.query(SessionModel).filter(
            (SessionModel.room_id != None) & (SessionModel.timeslot_id != None)
        ).all()
        
        for s in scheduled:
            ts = next((t for t in self.timeslots if t.id == s.timeslot_id), None)
            if ts:
                teacher_busy[ts.day][ts.slot_index].add(s.teacher_id)
                room_busy[ts.day][ts.slot_index].add(s.room_id)
                group_busy[ts.day][ts.slot_index].add(s.group_id)

        # Shuffle and try to place
        random.shuffle(unscheduled)
        
        scheduled_count = 0
        for sess in unscheduled:
            placed = False
            
            # Find eligible rooms
            course = self.courses.get(sess.course_id)
            if not course: continue
            
            target_type = RoomType.CLASSROOM
            if sess.type == SessionType.LECTURE:
                target_type = RoomType.AMPHITHEATRE
            elif sess.type == SessionType.TP:
                target_type = RoomType.LAB
                
            eligible_rooms = [r for r in self.rooms.values() if r.type == target_type]
            random.shuffle(eligible_rooms)
            
            # Find eligible timeslots
            eligible_ts = list(self.timeslots)
            random.shuffle(eligible_ts)
            
            for ts in eligible_ts:
                # Check teacher
                if sess.teacher_id in teacher_busy[ts.day][ts.slot_index]:
                    continue
                # Check group
                if sess.group_id in group_busy[ts.day][ts.slot_index]:
                    continue
                
                # Check room
                found_room = None
                for r in eligible_rooms:
                    if r.id not in room_busy[ts.day][ts.slot_index]:
                        found_room = r
                        break
                
                if not found_room:
                    continue
                
                # Update DB and memory
                sess.room_id = found_room.id
                sess.timeslot_id = ts.id
                
                teacher_busy[ts.day][ts.slot_index].add(sess.teacher_id)
                room_busy[ts.day][ts.slot_index].add(found_room.id)
                group_busy[ts.day][ts.slot_index].add(sess.group_id)
                
                placed = True
                scheduled_count += 1
                break
        
        self.db.commit()
        return scheduled_count

