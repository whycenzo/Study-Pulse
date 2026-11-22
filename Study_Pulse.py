import csv
from datetime import datetime

# Local file where tasks will be saved automatically
FILENAME = "study_pulse_tasks.csv"
FIELDNAMES = ["title", "due_date", "importance", "completed"]


def calculate_days_left(due_date_str):
    """Calculates days remaining from today to the due date."""
    today = datetime.now().date()
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    return (due_date - today).days


def calculate_priority_score(days_left, importance):
    """
    Computes priority score based on urgency and importance.
    Formula: (Importance * 20) / (Days Left + 1)
    """
    if days_left < 0:
        return 100.0

    score = (importance * 20) / (days_left + 1)
    return round(min(score, 100.0), 2)


def load_tasks():
    """Reads saved tasks from the CSV file."""
    tasks = []
    try:
        with open(FILENAME, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                tasks.append({
                    "title": row["title"],
                    "due_date": row["due_date"],
                    "importance": int(row["importance"]),
                    "completed": str(row["completed"]).strip().lower() == "true"
                })
    except FileNotFoundError:
        pass

    return tasks


def save_tasks(tasks):
    """Saves the tasks list to the CSV file."""
    try:
        with open(FILENAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            for task in tasks:
                writer.writerow(task)
    except Exception as e:
        print(f"Error saving data to CSV: {e}")


def prompt_due_date(current_date=None):
    """Prompts for a YYYY-MM-DD due date, optionally keeping current_date on blank input."""
    while True:
        prompt_text = (
            f"Enter Due Date (YYYY-MM-DD) [current: {current_date}, Enter to keep]: "
            if current_date
            else "Enter Due Date (YYYY-MM-DD): "
        )
        date_str = input(prompt_text).strip()
        if not date_str and current_date:
            return current_date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format! Use YYYY-MM-DD (e.g., 2026-11-20).")


def prompt_importance(current_importance=None):
    """Prompts for an importance level (1-5), optionally keeping current_importance on blank input."""
    while True:
        prompt_text = (
            f"Enter Priority/Importance Level (1 = Low, 5 = High) [current: {current_importance}, Enter to keep]: "
            if current_importance is not None
            else "Enter Importance Level (1 = Low, 5 = High): "
        )
        raw = input(prompt_text).strip()
        if not raw and current_importance is not None:
            return current_importance
        try:
            importance = int(raw)
            if 1 <= importance <= 5:
                return importance
            print("Please enter a whole number between 1 and 5.")
        except ValueError:
            print("Invalid input! Please enter a valid integer.")


def prompt_status(current_completed):
    """Prompts for task completion status (Pending or Completed)."""
    current_label = "Completed" if current_completed else "Pending"
    while True:
        print(f"Current Status: {current_label}")
        print("  1. Pending")
        print("  2. Completed")
        choice = input("Select status (1-2, or Enter to keep): ").strip()

        if not choice:
            return current_completed
        if choice == "1":
            return False
        if choice == "2":
            return True
        print("Invalid choice! Enter 1, 2, or press Enter.")


def select_task_index(tasks, action_label):
    """Displays a clean numbered task list and returns a valid 0-based index, or None if cancelled."""
    print("-" * 72)
    for idx, task in enumerate(tasks, 1):
        status = "[DONE]   " if task["completed"] else "[PENDING]"
        print(
            f"  {idx:<2}. {status} {task['title'][:26]:<26} | "
            f"Due: {task['due_date']} | Lvl: {task['importance']}/5"
        )
    print("-" * 72)

    while True:
        raw_idx = input(
            f"Select task number to {action_label} (1-{len(tasks)}, or 0 to cancel): "
        ).strip()
        if raw_idx == "0":
            return None
        try:
            task_idx = int(raw_idx) - 1
            if 0 <= task_idx < len(tasks):
                return task_idx
            print(f"Please enter a number between 1 and {len(tasks)}.")
        except ValueError:
            print("Invalid input! Please enter a valid task number.")


def enrich_tasks(task_list):
    """Attaches days_left and priority_score to copies of the given tasks."""
    enriched = []
    for task in task_list:
        days = calculate_days_left(task["due_date"])
        item = task.copy()
        item["days_left"] = days
        item["priority_score"] = calculate_priority_score(days, task["importance"])
        enriched.append(item)
    return enriched


def print_tasks_table(header_title, rows):
    """Renders a neatly aligned table with a compact summary bar."""
    pending_count = sum(1 for t in rows if not t["completed"])
    overdue_count = sum(1 for t in rows if not t["completed"] and t["days_left"] < 0)
    due_soon_count = sum(1 for t in rows if not t["completed"] and 0 <= t["days_left"] <= 2)

    print(f"\n=== {header_title} ===")
    print(
        f"Summary: {len(rows)} shown | {pending_count} pending | "
        f"{overdue_count} overdue | {due_soon_count} due in <=2 days"
    )
    print("=" * 80)
    print(
        f"{'No.':<4} {'Status':<10} {'Level':<7} {'Title':<22} "
        f"{'Due Date':<12} {'Days Left':<10} {'Score':<7}"
    )
    print("-" * 80)

    for idx, task in enumerate(rows, 1):
        status = "[DONE]" if task["completed"] else "[PENDING]"
        level_str = f"{task['importance']}/5"
        days_str = "OVERDUE" if task["days_left"] < 0 else str(task["days_left"])

        print(
            f"{idx:<4} {status:<10} {level_str:<7} {task['title'][:20]:<22} "
            f"{task['due_date']:<12} {days_str:<10} "
            f"{task['priority_score']:<7}"
        )

    print("=" * 80)


def add_task(tasks):
    """Adds a new task with basic input validation."""
    print("\n--- ADD NEW TASK ---")

    title = input("Enter Task Title: ").strip()
    if not title:
        print("Error: Task title cannot be empty.")
        return

    date_str = prompt_due_date()
    importance = prompt_importance()

    new_task = {
        "title": title,
        "due_date": date_str,
        "importance": importance,
        "completed": False
    }

    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Task '{title}' saved successfully (Status: Pending)!")


def toggle_task_status(tasks):
    """Quickly flips a task between Pending and Completed."""
    if not tasks:
        print("\nNo tasks available.")
        return

    print("\n--- QUICK TOGGLE STATUS ---")
    task_idx = select_task_index(tasks, "toggle status for")
    if task_idx is None:
        print("Cancelled.")
        return

    task = tasks[task_idx]
    task["completed"] = not task["completed"]
    save_tasks(tasks)

    state = "Completed" if task["completed"] else "Pending"
    print(f"Updated: '{task['title']}' is now [{state}].")


def edit_task(tasks):
    """Allows editing a task's title, completion status, priority level, or due date."""
    if not tasks:
        print("\nNo tasks available to edit. Choose Option 1 to add a task first!")
        return

    print("\n--- EDIT EXISTING TASK ---")
    task_idx = select_task_index(tasks, "edit")
    if task_idx is None:
        print("Edit cancelled.")
        return

    task = tasks[task_idx]

    while True:
        current_status_str = "Completed" if task["completed"] else "Pending"
        print(f"\nEditing: '{task['title']}' [{current_status_str} | Level: {task['importance']}/5]")
        print("  1. Rename Task")
        print("  2. Change Status (Pending / Completed)")
        print("  3. Change Priority Level (1-5)")
        print("  4. Change Due Date")
        print("  5. Edit All Fields")
        print("  6. Done Editing")

        field_choice = input("Select what to edit (1-6): ").strip()

        if field_choice == "1":
            new_title = input(f"Enter new title [current: {task['title']}]: ").strip()
            if new_title:
                task["title"] = new_title
                print("Task title updated.")
            else:
                print("Title unchanged.")

        elif field_choice == "2":
            task["completed"] = prompt_status(task["completed"])
            updated_label = "Completed" if task["completed"] else "Pending"
            print(f"Task status set to {updated_label}.")

        elif field_choice == "3":
            task["importance"] = prompt_importance(task["importance"])
            print(f"Priority level set to {task['importance']}/5.")

        elif field_choice == "4":
            task["due_date"] = prompt_due_date(task["due_date"])
            print(f"Due date set to {task['due_date']}.")

        elif field_choice == "5":
            new_title = input(f"Enter new title [current: {task['title']}, Enter to keep]: ").strip()
            if new_title:
                task["title"] = new_title
            task["completed"] = prompt_status(task["completed"])
            task["importance"] = prompt_importance(task["importance"])
            task["due_date"] = prompt_due_date(task["due_date"])
            print("All selected fields updated.")

        elif field_choice == "6":
            save_tasks(tasks)
            print("Changes saved to CSV!")
            break

        else:
            print("Invalid choice! Please select 1-6.")


def delete_task(tasks):
    """Deletes a selected task after confirmation and updates the CSV file."""
    if not tasks:
        print("\nNo tasks available to delete.")
        return

    print("\n--- DELETE TASK ---")
    task_idx = select_task_index(tasks, "delete")
    if task_idx is None:
        print("Deletion cancelled.")
        return

    target = tasks[task_idx]
    confirm = input(f"Delete '{target['title']}'? (y/n): ").strip().lower()
    if confirm in ("y", "yes"):
        removed = tasks.pop(task_idx)
        save_tasks(tasks)
        print(f"Task '{removed['title']}' deleted successfully!")
    else:
        print("Deletion cancelled.")


def sort_display_tasks(display_tasks, sort_choice):
    """Sorts prepared display task dictionaries based on Status or Priority Level."""
    if sort_choice == "2":
        return sorted(
            display_tasks,
            key=lambda t: (
                1 if t["completed"] else 0,
                -t["priority_score"],
                -t["importance"],
                t["days_left"]
            )
        )

    return sorted(
        display_tasks,
        key=lambda t: (
            -t["importance"],
            -t["priority_score"],
            t["days_left"]
        )
    )


def show_all_tasks(tasks):
    """Displays all tasks at once without filter or sort prompts."""
    if not tasks:
        print("\nNo tasks registered yet. Choose Option 1 to add a task!")
        return

    enriched = enrich_tasks(tasks)
    enriched.sort(key=lambda t: t["priority_score"], reverse=True)
    print_tasks_table("ALL TASKS", enriched)


def search_tasks(tasks):
    """Finds tasks whose title contains the entered keyword."""
    if not tasks:
        print("\nNo tasks registered yet.")
        return

    keyword = input("\nEnter keyword to search: ").strip().lower()
    if not keyword:
        print("Search cancelled.")
        return

    matched_raw = [t for t in tasks if keyword in t["title"].lower()]
    if not matched_raw:
        print(f"No tasks found matching '{keyword}'.")
        return

    enriched = enrich_tasks(matched_raw)
    enriched.sort(key=lambda t: t["priority_score"], reverse=True)
    print_tasks_table(f"SEARCH: '{keyword}'", enriched)


def view_tasks(tasks):
    """Filters tasks by status, sorts by priority level or status, and prints a table."""
    if not tasks:
        print("\nNo tasks registered yet. Choose Option 1 to add a task!")
        return

    print("\n--- FILTER & SORT ---")
    print("Filter: [1] Pending   [2] Completed   [3] All (Default)")
    filter_choice = input("Choose filter (1-3, or Enter): ").strip()

    if filter_choice == "1":
        filtered_tasks = [t for t in tasks if not t["completed"]]
        filter_label = "PENDING"
    elif filter_choice == "2":
        filtered_tasks = [t for t in tasks if t["completed"]]
        filter_label = "COMPLETED"
    else:
        filtered_tasks = list(tasks)
        filter_label = "ALL"

    if not filtered_tasks:
        print(f"\nNo tasks found under '{filter_label}'.")
        return

    print("Sort:   [1] Priority Level (Default)   [2] Status")
    while True:
        sort_choice = input("Choose sort (1-2, or Enter): ").strip()
        if sort_choice in ("", "1", "2"):
            break
        print("Invalid choice! Enter 1, 2, or press Enter.")

    sort_label = "STATUS" if sort_choice == "2" else "PRIORITY LEVEL"
    display_tasks = enrich_tasks(filtered_tasks)
    sorted_tasks = sort_display_tasks(display_tasks, sort_choice or "1")
    print_tasks_table(f"{filter_label} | BY {sort_label}", sorted_tasks)


def main():
    tasks = load_tasks()

    while True:
        print("\n==================================")
        print("      STUDY PULSE - MAIN MENU     ")
        print("==================================")
        print("  1. Add New Task")
        print("  2. Show All Tasks")
        print("  3. Filter & Sort Tasks")
        print("  4. Search Tasks")
        print("  5. Quick Toggle Status")
        print("  6. Edit Task")
        print("  7. Delete Task")
        print("  8. Exit")
        print("----------------------------------")

        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            show_all_tasks(tasks)
        elif choice == "3":
            view_tasks(tasks)
        elif choice == "4":
            search_tasks(tasks)
        elif choice == "5":
            toggle_task_status(tasks)
        elif choice == "6":
            edit_task(tasks)
        elif choice == "7":
            delete_task(tasks)
        elif choice == "8":
            print("Exiting Study Pulse. Good luck with your studies!")
            break
        else:
            print("Invalid choice! Please type a number from 1 to 8.")


if __name__ == "__main__":
    main()
