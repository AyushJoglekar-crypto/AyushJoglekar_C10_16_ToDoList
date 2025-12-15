import json
from datetime import datetime, date

# --------------------------
# Task Class
# --------------------------
class Task:
    def __init__(self, title, deadline=None, priority="Medium",
                 category="General", done=False):
        self.title = title
        self.deadline = deadline  # "YYYY-MM-DD"
        self.priority = priority  # High, Medium, Low
        self.category = category
        self.done = done
        self.created_at = datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "title": self.title,
            "deadline": self.deadline,
            "priority": self.priority,
            "category": self.category,
            "done": self.done,
            "created_at": self.created_at
        }

# --------------------------
# Task Manager
# --------------------------
class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = []
        self.streak = 0
        self.last_done_date = None
        self.load()

    # Add new task
    def add_task(self, title, deadline=None, priority="Medium", category="General"):
        task = Task(title, deadline, priority, category)
        self.tasks.append(task)
        self.save()

    # Delete task
    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save()

    # Edit task
    def edit_task(self, index, **updates):
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.save()

    # Mark as done / not done
    def mark_task(self, index, done=True):
        if 0 <= index < len(self.tasks):
            self.tasks[index].done = done
            self._update_streak(done)
            self.save()

    # Track daily streak
    def _update_streak(self, done):
        if not done:
            return

        today = date.today()
        if self.last_done_date is None:
            self.streak = 1
        else:
            last_date = datetime.strptime(self.last_done_date, "%Y-%m-%d").date()
            if (today - last_date).days == 1:
                self.streak += 1
            elif (today - last_date).days > 1:
                self.streak = 1

        self.last_done_date = today.strftime("%Y-%m-%d")

    # Show all tasks
    def show_tasks(self):
        print("\n===== ALL TASKS =====")
        for i, task in enumerate(self.tasks):
            print(f"{i}. {task.title} | Done: {task.done} | "
                  f"Priority: {task.priority} | Category: {task.category} | "
                  f"Deadline: {task.deadline}")
        print("=====================")

    # Filter tasks
    def filter_tasks(self, **filters):
        results = self.tasks
        for key, value in filters.items():
            results = [t for t in results if getattr(t, key) == value]
        return results

    # Sort tasks
    def sort_tasks(self, key="deadline"):
        try:
            self.tasks.sort(key=lambda t: getattr(t, key) or "")
        except Exception:
            print("Unable to sort by", key)

    # Save to JSON
    def save(self):
        data = {
            "tasks": [t.to_dict() for t in self.tasks],
            "streak": self.streak,
            "last_done_date": self.last_done_date
        }
        json.dump(data, open(self.filename, "w"), indent=4)

    # Load from JSON
    def load(self):
        try:
            data = json.load(open(self.filename))
            self.streak = data.get("streak", 0)
            self.last_done_date = data.get("last_done_date", None)

            self.tasks = []
            for t in data.get("tasks", []):
                task = Task(
                    t["title"],
                    t["deadline"],
                    t["priority"],
                    t["category"],
                    t["done"]
                )
                task.created_at = t["created_at"]
                self.tasks.append(task)

        except FileNotFoundError:
            self.save()

tm = TaskManager()

def show_menu():
    print("\n===== TO-DO LIST MENU =====")
    print("1. Add Task")
    print("2. Delete Task")
    print("3. Edit Task")
    print("4. Mark Task as Done")
    print("5. Mark Task as Not Done")
    print("6. Show All Tasks")
    print("7. Filter Tasks")
    print("8. Sort Tasks")
    print("9. Show Streak")
    print("0. Exit")
    print("===========================")

def get_index():
    tm.show_tasks()
    try:
        return int(input("\nEnter task number: "))
    except:
        print("Invalid input.")
        return None

def add_task():
    title = input("Enter task title: ")
    deadline = input("Enter deadline (YYYY-MM-DD or blank): ")
    deadline = deadline if deadline else None
    priority = input("Priority (High/Medium/Low): ") or "Medium"
    category = input("Category (Study, Work, Personal, etc.): ") or "General"

    tm.add_task(title, deadline, priority, category)
    print("Task added!")

def delete_task():
    idx = get_index()
    if idx is not None:
        tm.delete_task(idx)
        print("Task deleted!")

def edit_task():
    idx = get_index()
    if idx is None:
        return

    print("\nLeave empty to keep old value.")
    title = input("New title: ")
    deadline = input("New deadline (YYYY-MM-DD): ")
    priority = input("New priority (High/Medium/Low): ")
    category = input("New category: ")

    updates = {}
    if title: updates["title"] = title
    if deadline: updates["deadline"] = deadline
    if priority: updates["priority"] = priority
    if category: updates["category"] = category

    tm.edit_task(idx, **updates)
    print("Task updated!")

def mark_done():
    idx = get_index()
    if idx is not None:
        tm.mark_task(idx, True)
        print("Marked as done!")

def mark_not_done():
    idx = get_index()
    if idx is not None:
        tm.mark_task(idx, False)
        print("Marked as NOT done!")

def filter_tasks():
    print("\nFilter by:")
    print("1. Category")
    print("2. Priority")
    print("3. Done / Not Done")
    choice = input("Enter choice: ")

    if choice == "1":
        cat = input("Enter category: ")
        results = tm.filter_tasks(category=cat)
    elif choice == "2":
        pr = input("Enter priority (High/Medium/Low): ")
        results = tm.filter_tasks(priority=pr)
    elif choice == "3":
        dn = input("Done? (yes/no): ")
        status = True if dn.lower() == "yes" else False
        results = tm.filter_tasks(done=status)
    else:
        print("Invalid!")
        return

    print("\nFiltered Results:")
    for t in results:
        print(f"- {t.title} ({t.category}, {t.priority})")

def sort_tasks():
    print("\nSort by:")
    print("1. Deadline")
    print("2. Priority")
    print("3. Category")
    choice = input("Enter choice: ")

    if choice == "1":
        tm.sort_tasks("deadline")
    elif choice == "2":
        tm.sort_tasks("priority")
    elif choice == "3":
        tm.sort_tasks("category")
    else:
        print("Invalid!")
        return

    print("Tasks sorted!")

def show_streak():
    print(f"\n🔥 Current Productivity Streak: {tm.streak} days")

def main():
    while True:
        show_menu()
        choice = input("Enter choice: ")

        if choice == "1":
            add_task()
        elif choice == "2":
            delete_task()
        elif choice == "3":
            edit_task()
        elif choice == "4":
            mark_done()
        elif choice == "5":
            mark_not_done()
        elif choice == "6":
            tm.show_tasks()
        elif choice == "7":
            filter_tasks()
        elif choice == "8":
            sort_tasks()
        elif choice == "9":
            show_streak()
        elif choice == "0":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice! Try again.")

if __name__ == "__main__":
    main()
