import json
from datetime import datetime

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_TO_INDEX = {d: i for i, d in enumerate(DAYS)}
timetable = []

def parse_time(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def validate_time(t):
    try:
        if ":" not in t:
            return False
        h, m = map(int, t.split(":"))
        return 0 <= h <= 23 and 0 <= m <= 59
    except:
        return False

def sort_timetable():
    timetable.sort(key=lambda x: (DAY_TO_INDEX[x["day"]], parse_time(x["start"])))

def conflicts(day, start, end, ignore_index=None):
    s, e = parse_time(start), parse_time(end)
    for idx, cls in enumerate(timetable):
        if ignore_index is not None and idx == ignore_index:
            continue
        if cls["day"] == day:
            cs, ce = parse_time(cls["start"]), parse_time(cls["end"])
            if not (e <= cs or ce <= s):
                return True
    return False

def find_class_index(name, day, start):
    for i, cls in enumerate(timetable):
        if cls["name"] == name and cls["day"] == day and cls["start"] == start:
            return i
    return None

def add_class():
    name = input("Enter class name: ")
    day = input("Enter day (e.g. Monday): ")
    start = input("Enter start time in 24-hour format (HH:MM, e.g. 14:30): ")
    if not validate_time(start):
        print("Invalid time format. Please use HH:MM in 24-hour format (00:00-23:59).")
        return
    end = input("Enter end time in 24-hour format (HH:MM, e.g. 16:00): ")
    if not validate_time(end):
        print("Invalid time format. Please use HH:MM in 24-hour format (00:00-23:59).")
        return
    if conflicts(day, start, end):
        print("Conflict detected! Cannot add.")
    else:
        timetable.append({"name": name, "day": day, "start": start, "end": end})
        sort_timetable()
        print("Class added.")

def update_class():
    old_name = input("Enter old class name: ")
    old_day = input("Enter old day: ")
    old_start = input("Enter old start time (HH:MM): ")
    idx = find_class_index(old_name, old_day, old_start)
    if idx is None:
        print("Class not found.")
        return
    new_name = input("Enter new class name: ")
    new_day = input("Enter new day: ")
    new_start = input("Enter new start time in 24-hour format (HH:MM, e.g. 14:30): ")
    if not validate_time(new_start):
        print("Invalid time format. Please use HH:MM in 24-hour format (00:00-23:59).")
        return
    new_end = input("Enter new end time in 24-hour format (HH:MM, e.g. 16:00): ")
    if not validate_time(new_end):
        print("Invalid time format. Please use HH:MM in 24-hour format (00:00-23:59).")
        return
    if conflicts(new_day, new_start, new_end, ignore_index=idx):
        print("Conflict detected! Cannot update.")
    else:
        timetable[idx] = {"name": new_name, "day": new_day, "start": new_start, "end": new_end}
        sort_timetable()
        print("Class updated.")

def delete_class():
    name = input("Enter class name to delete: ")
    day = input("Enter day: ")
    start = input("Enter start time (HH:MM): ")
    idx = find_class_index(name, day, start)
    if idx is None:
        print("Class not found.")
    else:
        timetable.pop(idx)
        print("Class deleted.")

def show_day(day):
    print(f"--- {day} ---")
    for cls in timetable:
        if cls["day"] == day:
            print(f"{cls['start']} - {cls['end']} | {cls['name']}")

def show_today_and_tomorrow():
    today_idx = datetime.now().weekday()
    today = DAYS[today_idx]
    tomorrow = DAYS[(today_idx + 1) % 7]
    show_day(today)
    show_day(tomorrow)

def weekly_summary():
    totals = {}
    for cls in timetable:
        duration = parse_time(cls["end"]) - parse_time(cls["start"])
        totals[cls["name"]] = totals.get(cls["name"], 0) + duration
    print("--- Weekly Summary ---")
    for name, mins in totals.items():
        print(f"{name}: {mins//60}h {mins%60}m")

def save_json():
    path = input("Enter filename to save (e.g. timetable.json): ")
    with open(path, "w") as f:
        json.dump(timetable, f, indent=2)
    print("Saved.")

def load_json():
    path = input("Enter filename to load (e.g. timetable.json): ")
    with open(path, "r") as f:
        data = json.load(f)
        timetable.clear()
        timetable.extend(data)
    sort_timetable()
    print("Loaded.")

def menu():
    while True:
        print("\n1. Add class")
        print("2. Update class")
        print("3. Delete class")
        print("4. Show today's and tomorrow's timetable")
        print("5. Weekly summary")
        print("6. Save timetable (JSON)")
        print("7. Load timetable (JSON)")
        print("0. Exit")
        choice = input("Choose: ")
        if choice == "1":
            add_class()
        elif choice == "2":
            update_class()
        elif choice == "3":
            delete_class()
        elif choice == "4":
            show_today_and_tomorrow()
        elif choice == "5":
            weekly_summary()
        elif choice == "6":
            save_json()
        elif choice == "7":
            load_json()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    menu()
