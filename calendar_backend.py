# calendar_backend.py
import json
from datetime import date, datetime
from collections import defaultdict

from timetable_backend import (
    conflicts,
    timetable,
    sort_timetable,
    find_class_index,
    validate_time
)


from todo_backend import TaskManager

CATEGORY_COLORS_FILE = "category_colors.json"
OVERRIDES_FILE = "timetable_overrides.json"
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIMETABLE_FILE = os.path.join(BASE_DIR, "timetable.json")


class CalendarManager:
    def __init__(self, task_manager: TaskManager):
        self.tm = task_manager
        self.category_colors = self._load_category_colors()
        self.overrides = self._load_overrides()

    # -----------------------------
    # Category Colors
    # -----------------------------
    def _load_category_colors(self):
        try:
            with open(CATEGORY_COLORS_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_category_color(self, category, color_hex):
        self.category_colors[category] = color_hex
        json.dump(self.category_colors,
                  open(CATEGORY_COLORS_FILE, "w"),
                  indent=2)

    def get_category_color(self, category):
        return self.category_colors.get(category, "#00E5FF")

    # -----------------------------
    # Timetable Overrides (NEW)
    # -----------------------------
    def _load_overrides(self):
        try:
            with open(OVERRIDES_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_overrides(self):
        json.dump(self.overrides,
                  open(OVERRIDES_FILE, "w"),
                  indent=2)

    def override_event_for_date(
        self,
        yyyy_mm_dd,
        event_name,
        new_start,
        new_end
    ):
        """
        Override a weekly event for a specific date
        """
        if yyyy_mm_dd not in self.overrides:
            self.overrides[yyyy_mm_dd] = {
                "cancel": [],
                "add": []
            }

        # cancel original
        if event_name not in self.overrides[yyyy_mm_dd]["cancel"]:
            self.overrides[yyyy_mm_dd]["cancel"].append(event_name)

        # add modified event
        self.overrides[yyyy_mm_dd]["add"].append({
            "name": event_name,
            "start": new_start,
            "end": new_end
        })

        self._save_overrides()

    # -----------------------------
    # Tasks by Date
    # -----------------------------
    def tasks_for_date(self, yyyy_mm_dd):
        return [
            t for t in self.tm.tasks
            if t.deadline == yyyy_mm_dd and not t.done
        ]

    # -----------------------------
    # Scheduling Tasks (weekly)
    # -----------------------------
    def schedule_task(
        self,
        task_title,
        day_name,
        start,
        end
    ):
        """
        Assign a task to the weekly timetable
        """
        if conflicts(day_name, start, end):
            raise ValueError("Time conflict detected")

        timetable.append({
            "name": f"Task: {task_title}",
            "day": day_name,
            "start": start,
            "end": end
        })
        sort_timetable()

    # -----------------------------
    # Timetable for Specific Date (NEW)
    # -----------------------------
    def timetable_for_date(self, yyyy_mm_dd):
        day_name = datetime.strptime(
            yyyy_mm_dd, "%Y-%m-%d"
        ).strftime("%A")

        base_events = [
            e for e in timetable
            if e["day"] == day_name
        ]

        final = []
        for e in base_events:
            final.append({
                "date": yyyy_mm_dd,
                "name": e["name"],
                "start": e["start"],
                "end": e["end"],
                "category": e.get("category", "General")
            })

        return final


    # -----------------------------
    # Daily Overview
    # -----------------------------
    def daily_overview(self, yyyy_mm_dd):
        return {
            "tasks": self.tasks_for_date(yyyy_mm_dd),
            "events": self.timetable_for_date(yyyy_mm_dd)
        }

    # -----------------------------
    # Upcoming Items
    # -----------------------------
    def upcoming_items(self, days=7):
        today = date.today()
        upcoming_tasks = []
        upcoming_events = []

        for t in self.tm.tasks:
            if t.deadline:
                d = datetime.strptime(t.deadline, "%Y-%m-%d").date()
                if 0 <= (d - today).days <= days and not t.done:
                    upcoming_tasks.append(t)

        # upcoming events = weekly + overrides
        for e in timetable:
            upcoming_events.append(e)

        for day, data in self.overrides.items():
            for ev in data.get("add", []):
                upcoming_events.append(ev)

        return upcoming_tasks, upcoming_events
        # =============================
    # TIMETABLE ADAPTER (GUI SAFE)
    # =============================

    def add_timetable_event(self, date, name, start, end, category):
        from timetable_backend import timetable, conflicts, sort_timetable, validate_time
        from datetime import datetime

        day = datetime.strptime(date, "%Y-%m-%d").strftime("%A")

        if not validate_time(start) or not validate_time(end):
            raise ValueError("Invalid time format (HH:MM)")

        if conflicts(day, start, end):
            raise ValueError("Timetable conflict detected")

        timetable.append({
            "name": name,
            "day": day,
            "start": start,
            "end": end,
            "category": category
        })

        sort_timetable()

    

    def delete_timetable_event(self, event):
        day = datetime.strptime(event["date"], "%Y-%m-%d").strftime("%A")

        idx = find_class_index(event["name"], day, event["start"])
        if idx is not None:
            timetable.pop(idx)

    def update_timetable_event(self, old_event, new_event):
        old_day = datetime.strptime(
            old_event["date"], "%Y-%m-%d"
        ).strftime("%A")

        idx = find_class_index(
            old_event["name"],
            old_day,
            old_event["start"]
        )

        if idx is None:
            return

        new_day = datetime.strptime(
            new_event["date"], "%Y-%m-%d"
        ).strftime("%A")

        if conflicts(
            new_day,
            new_event["start"],
            new_event["end"],
            ignore_index=idx
        ):
            raise ValueError("Timetable conflict detected")

        timetable[idx] = {
            "name": new_event["name"],
            "day": new_day,
            "start": new_event["start"],
            "end": new_event["end"],
            "category": new_event["category"]
        }

        sort_timetable()

    # -----------------------------
    # SAVE / LOAD (reuse backend)
    # -----------------------------
    def save_timetable(self):
        with open(TIMETABLE_FILE, "w") as f:
            json.dump(timetable, f, indent=2)

    def load_timetable(self):
        try:
            with open(TIMETABLE_FILE, "r") as f:
                data = json.load(f)
                timetable.clear()
                timetable.extend(data)
                sort_timetable()
        except FileNotFoundError:
            pass
