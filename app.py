import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os, random
from datetime import datetime
import matplotlib.pyplot as plt

FILE = "habits.json"
QUOTES = [
    "Believe in yourself!",
    "Small steps every day!",
    "You are capable of great things!",
    "Stay consistent. Results will follow.",
    "Discipline = Freedom",
    "Make progress, not excuses."
]

def load_data():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Failed to load habits.json.")
    return []

def save_data():
    with open(FILE, "w") as f:
        json.dump(habits, f, indent=2)

def add_habit():
    habit = habit_var.get().strip()
    category = category_var.get()
    if habit:
        habits.append({
            "habit": habit,
            "status": "Not Done",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": category,
            "streak": 0,
            "last_done_date": "",
            "log": []
        })
        save_data()
        refresh_table()
        habit_var.set("")
    else:
        messagebox.showwarning("Input", "Enter habit name.")

def mark_done():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        today = datetime.now().strftime("%Y-%m-%d")
        last = habits[idx].get("last_done_date")
        if last:
            diff = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(last, "%Y-%m-%d")).days
            if diff == 1:
                habits[idx]["streak"] += 1
            elif diff > 1:
                habits[idx]["streak"] = 1
        else:
            habits[idx]["streak"] = 1

        habits[idx]["last_done_date"] = today
        habits[idx]["status"] = "✅ Done"
        habits[idx].setdefault("log", []).append(today)

        if habits[idx]["streak"] == 5:
            messagebox.showinfo("🏅 Reward!", f"You earned a 5-day streak badge for '{habits[idx]['habit']}'!")

        save_data()
        refresh_table()
    else:
        messagebox.showwarning("Select", "Select a habit to mark done.")

def delete_habit():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        habits.pop(idx)
        save_data()
        refresh_table()

def edit_habit():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        new_name = simpledialog.askstring("Edit Habit", "Enter new habit name:", initialvalue=habits[idx]["habit"])
        if new_name:
            habits[idx]["habit"] = new_name.strip()
            save_data()
            refresh_table()

def show_stats():
    total = len(habits)
    done = sum(1 for h in habits if h["status"] == "✅ Done")
    not_done = total - done
    messagebox.showinfo("Stats", f"📊 Habit Summary:\n\nTotal Habits: {total}\n✅ Done: {done}\n❌ Not Done: {not_done}")

def refresh_table():
    tree.delete(*tree.get_children())
    search = search_var.get().lower()
    for i, h in enumerate(habits):
        if search in h["habit"].lower():
            tree.insert("", "end", iid=i, values=(h["habit"], h["status"], h.get("date", ""), h.get("category", ""), h.get("streak", 0)))
    update_progress()

def update_progress():
    total = len(habits)
    done = sum(1 for h in habits if h["status"] == "✅ Done")
    progress = int((done / total) * 100) if total > 0 else 0
    progress_var.set(progress)
    progress_label.config(text=f"Progress: {progress}%")

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    bg = "#2e2e2e" if dark_mode else "white"
    fg = "white" if dark_mode else "black"
    root.config(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.config(bg=bg, fg=fg)
        except:
            pass

def open_journal():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        entry = simpledialog.askstring("Daily Log", "Write your reflection for today:")
        if entry:
            date = datetime.now().strftime("%Y-%m-%d")
            habits[idx].setdefault("journal", {})[date] = entry
            save_data()

def show_chart():
    counts = {}
    for h in habits:
        for date in h.get("log", []):
            counts[date] = counts.get(date, 0) + 1
    if not counts:
        messagebox.showinfo("No Data", "No habit data to show graph.")
        return
    dates = sorted(counts.keys())
    values = [counts[d] for d in dates]
    plt.figure(figsize=(6, 4))
    plt.bar(dates, values)
    plt.xticks(rotation=45)
    plt.title("Habit Completion Over Time")
    plt.xlabel("Date")
    plt.ylabel("Habits Done")
    plt.tight_layout()
    plt.show()

# GUI Setup
root = tk.Tk()
root.title("Advanced Habit Tracker")
root.geometry("800x550")
messagebox.showinfo("Daily Motivation", random.choice(QUOTES))

habit_var = tk.StringVar()
category_var = tk.StringVar(value="Health")
search_var = tk.StringVar()
progress_var = tk.IntVar()
habits = load_data()
dark_mode = False

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Enter Habit:").grid(row=0, column=0)
tk.Entry(input_frame, textvariable=habit_var, width=30).grid(row=0, column=1, padx=5)
tk.Label(input_frame, text="Category:").grid(row=0, column=2)
ttk.Combobox(input_frame, textvariable=category_var, values=["Health", "Study", "Skill", "Work"]).grid(row=0, column=3)
tk.Button(input_frame, text="Add", command=add_habit).grid(row=0, column=4, padx=5)

tk.Label(input_frame, text="Search:").grid(row=1, column=0, pady=5)
tk.Entry(input_frame, textvariable=search_var, width=30).grid(row=1, column=1, padx=5)
tk.Button(input_frame, text="Refresh", command=refresh_table).grid(row=1, column=2)

# Treeview
tree = ttk.Treeview(root, columns=("Habit", "Status", "Date", "Category", "Streak"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Action Buttons
action_frame = tk.Frame(root)
action_frame.pack(pady=5)


tk.Button(action_frame, text="Delete", command=delete_habit).grid(row=0, column=1, padx=5)
tk.Button(action_frame, text="Edit", command=edit_habit).grid(row=0, column=2, padx=5)
tk.Button(action_frame, text="Stats", command=show_stats).grid(row=0, column=3, padx=5)
tk.Button(action_frame, text="Dark Mode", command=toggle_theme).grid(row=0, column=4, padx=5)
tk.Button(action_frame, text="Journal", command=open_journal).grid(row=0, column=5, padx=5)
tk.Button(action_frame, text="📊 Chart", command=show_chart).grid(row=0, column=6, padx=5)

# Progress Bar
progress_frame = tk.Frame(root)
progress_frame.pack(pady=5)
tk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT)
progress_label = tk.Label(progress_frame, text="0%")
progress_label.pack(side=tk.LEFT, padx=5)
progressbar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=200)
progressbar.pack(side=tk.LEFT, padx=5)

refresh_table()
root.mainloop()

