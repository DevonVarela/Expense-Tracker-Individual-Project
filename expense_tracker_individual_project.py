# Personal Expense Tracker - Devon Varela - BUS472
# Features: expense logging, CSV persistence, budget limits, spending summary

# imports tkinter for the GUI window and all widgets
# Source: https://docs.python.org/3/library/tkinter.html
import tkinter as tk
from tkinter import messagebox, ttk

# pandas reads and writes CSV files to save data between sessions
# Source: https://pandas.pydata.org/docs/
import pandas as pd

# os lets us check if a save file already exists before loading it
import os

EXPENSES_FILE = "expenses.csv"
BUDGETS_FILE = "budgets.csv"

# my own list of spending categories
CATEGORIES = ["Food", "Transport", "Entertainment", "Shopping", "Health", "Other"]

# creates the main application window
# Source: https://www.geeksforgeeks.org/python-gui-tkinter/
root = tk.Tk()
root.title("Personal Expense Tracker")
root.geometry("520x620")
root.resizable(False, False)
root.configure(bg="white")

# my own list to store expense dictionaries
expenses = []

# my own dictionary to store budget limits, one entry per category
budgets = {}
for cat in CATEGORIES:
    budgets[cat] = 0.0

# StringVar variables link input fields to Python so we can read their values
desc_var = tk.StringVar()
amount_var = tk.StringVar()
category_var = tk.StringVar(value=CATEGORIES[0])


# MY CODE: reads expenses.csv on startup and restores the last session
def load_expenses():
    if not os.path.exists(EXPENSES_FILE):
        return
    # Source: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    df = pd.read_csv(EXPENSES_FILE)
    for _, row in df.iterrows():
        expense = {"desc": row["desc"], "amount": float(row["amount"]), "category": row["category"]}
        expenses.append(expense)
        display_text = f"  {row['category']:<14}  ${float(row['amount']):>7.2f}   {row['desc']}"
        expense_listbox.insert(tk.END, display_text)
        if len(expenses) % 2 == 0:
            expense_listbox.itemconfig(tk.END, bg="lightblue")
        else:
            expense_listbox.itemconfig(tk.END, bg="white")
    update_total()
    update_summary()


# MY CODE: saves all current expenses to CSV using pandas
def save_expenses():
    # Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
    if expenses:
        df = pd.DataFrame(expenses)
    else:
        df = pd.DataFrame(columns=["desc", "amount", "category"])
    df.to_csv(EXPENSES_FILE, index=False)


# MY CODE: reads budgets.csv on startup and restores saved budget limits
def load_budgets():
    if not os.path.exists(BUDGETS_FILE):
        return
    # Source: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    df = pd.read_csv(BUDGETS_FILE)
    for _, row in df.iterrows():
        if row["category"] in budgets:
            budgets[row["category"]] = float(row["amount"])
    for cat in budget_vars:
        if budgets[cat] > 0:
            budget_vars[cat].set(str(budgets[cat]))
        else:
            budget_vars[cat].set("")


# MY CODE: writes current budget limits to CSV
def save_budgets():
    # Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
    rows = []
    for cat, amt in budgets.items():
        rows.append({"category": cat, "amount": amt})
    df = pd.DataFrame(rows)
    df.to_csv(BUDGETS_FILE, index=False)


# MY CODE: validates input, adds the expense, saves to CSV, checks budget
def add_expense():
    desc = desc_var.get().strip()
    amount_text = amount_var.get().strip()
    category = category_var.get()

    # show a warning if either field is empty
    if not desc or not amount_text:
        messagebox.showwarning("Missing Info", "Please enter both a description and an amount.")
        return

    # try to convert amount to a number, show error if it fails
    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Amount", "Amount must be a positive number.")
        return

    expenses.append({"desc": desc, "amount": amount, "category": category})

    # formats the row so columns line up neatly in the listbox
    # Source: https://www.tutorialspoint.com/python/tk_listbox.htm
    display_text = f"  {category:<14}  ${amount:>7.2f}   {desc}"
    expense_listbox.insert(tk.END, display_text)
    if len(expenses) % 2 == 0:
        expense_listbox.itemconfig(tk.END, bg="lightblue")
    else:
        expense_listbox.itemconfig(tk.END, bg="white")

    save_expenses()
    update_total()
    update_summary()
    check_budget(category)
    desc_var.set("")
    amount_var.set("")


# MY CODE: checks spending vs limit and warns at 80% and 100%
def check_budget(category):
    limit = budgets.get(category, 0)
    if limit <= 0:
        return
    spent = 0
    for e in expenses:
        if e["category"] == category:
            spent += e["amount"]
    percent = (spent / limit) * 100
    if percent >= 100:
        messagebox.showwarning("Over Budget!", f"You exceeded your {category} budget!\nSpent: ${spent:.2f} / Limit: ${limit:.2f}")
    elif percent >= 80:
        messagebox.showinfo("Budget Warning", f"{percent:.0f}% of your {category} budget used.\nSpent: ${spent:.2f} / Limit: ${limit:.2f}")


# MY CODE: adds up all expenses and updates the total label
def update_total():
    total = 0
    for e in expenses:
        total += e["amount"]
    total_label.config(text=f"Total Spent:   ${total:.2f}")


# MY CODE: clears all entries after the user confirms
def clear_expenses():
    if not expenses:
        return
    if messagebox.askyesno("Clear All", "Are you sure you want to clear all expenses?"):
        expenses.clear()
        expense_listbox.delete(0, tk.END)
        save_expenses()
        update_total()
        update_summary()


# MY CODE: reads budget input fields, validates them, saves to CSV
def set_budgets():
    for cat, var in budget_vars.items():
        val = var.get().strip()
        if val == "" or val == "0":
            budgets[cat] = 0.0
        else:
            try:
                budgets[cat] = float(val)
                if budgets[cat] < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Budget", f"Enter a valid number for {cat}.")
                return
    save_budgets()
    update_summary()
    messagebox.showinfo("Budgets Saved", "Your budget limits have been saved.")


# MY CODE: calculates spent vs budget per category and updates the summary labels
def update_summary():
    for cat in CATEGORIES:
        spent = 0
        for e in expenses:
            if e["category"] == cat:
                spent += e["amount"]
        limit = budgets[cat]
        summary_spent_labels[cat].config(text=f"${spent:.2f}")
        if limit > 0:
            percent = (spent / limit) * 100
            remaining = limit - spent
            summary_limit_labels[cat].config(text=f"${limit:.2f}")
            summary_remaining_labels[cat].config(text=f"${remaining:.2f}")
            if percent >= 100:
                color = "red"
            elif percent >= 80:
                color = "orange"
            else:
                color = "green"
            summary_spent_labels[cat].config(fg=color)
            summary_remaining_labels[cat].config(fg=color)
        else:
            summary_limit_labels[cat].config(text="No limit")
            summary_remaining_labels[cat].config(text="-")
            summary_spent_labels[cat].config(fg="black")
            summary_remaining_labels[cat].config(fg="black")


# MY CODE: saves everything when the user closes the window
def on_close():
    save_expenses()
    save_budgets()
    root.destroy()


# bind on_close to the window X button
root.protocol("WM_DELETE_WINDOW", on_close)

# ---- GUI LAYOUT ----

# title label at the top
title_label = tk.Label(root, text="Personal Expense Tracker",
                       font=("Helvetica", 18, "bold"), bg="white", fg="black")
title_label.pack(pady=(16, 6))

# Notebook creates the two tabs
# Source: https://docs.python.org/3/library/tkinter.ttk.html
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=16, pady=(0, 16))

# ---- TAB 1: EXPENSES ----
tab_tracker = tk.Frame(notebook, bg="white")
notebook.add(tab_tracker, text="  Expenses  ")

input_frame = tk.Frame(tab_tracker, bg="white", padx=20)
input_frame.pack(fill="x", pady=(10, 0))

# Description field
tk.Label(input_frame, text="Description:", bg="white", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", pady=4)
desc_entry = tk.Entry(input_frame, textvariable=desc_var, font=("Helvetica", 11), width=30)
desc_entry.grid(row=0, column=1, pady=4, padx=(8, 0))

# Amount field
tk.Label(input_frame, text="Amount ($):", bg="white", font=("Helvetica", 11)).grid(row=1, column=0, sticky="w", pady=4)
amount_entry = tk.Entry(input_frame, textvariable=amount_var, font=("Helvetica", 11), width=30)
amount_entry.grid(row=1, column=1, pady=4, padx=(8, 0))

# Category dropdown
tk.Label(input_frame, text="Category:", bg="white", font=("Helvetica", 11)).grid(row=2, column=0, sticky="w", pady=4)

# OptionMenu creates the dropdown
# Source: https://www.tutorialspoint.com/python/tk_optionmenu.htm
category_menu = tk.OptionMenu(input_frame, category_var, *CATEGORIES)
category_menu.config(font=("Helvetica", 11), width=26, bg="white")
category_menu.grid(row=2, column=1, pady=4, padx=(8, 0), sticky="w")

btn_frame = tk.Frame(tab_tracker, bg="white")
btn_frame.pack(pady=10)

# Add Expense button
add_btn = tk.Button(btn_frame, text="Add Expense", command=add_expense,
                    font=("Helvetica", 11, "bold"), bg="blue", fg="white",
                    padx=14, pady=6, relief="flat")
add_btn.grid(row=0, column=0, padx=8)

# Clear All button - red means destructive action
clear_btn = tk.Button(btn_frame, text="Clear All", command=clear_expenses,
                      font=("Helvetica", 11), bg="red", fg="white",
                      padx=14, pady=6, relief="flat")
clear_btn.grid(row=0, column=1, padx=8)

# column header bar above the list
header_label = tk.Label(tab_tracker, text=f"  {'Category':<14}  {'Amount':>9}   Description",
                        font=("Courier", 10, "bold"), bg="gray", fg="white", anchor="w", padx=10)
header_label.pack(fill="x", padx=20)

list_frame = tk.Frame(tab_tracker, bg="white")
list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

# listbox shows all expense entries
# Source: https://www.tutorialspoint.com/python/tk_listbox.htm
expense_listbox = tk.Listbox(list_frame, font=("Courier", 11), yscrollcommand=scrollbar.set,
                              selectbackground="blue", height=10, relief="flat", bd=0)
expense_listbox.pack(fill="both", expand=True)
scrollbar.config(command=expense_listbox.yview)

# footer bar showing the running total
total_label = tk.Label(tab_tracker, text="Total Spent:   $0.00",
                       font=("Helvetica", 13, "bold"), bg="gray", fg="green", pady=8)
total_label.pack(fill="x", padx=20, pady=(0, 10))

# ---- TAB 2: BUDGET ----
tab_budget = tk.Frame(notebook, bg="white")
notebook.add(tab_budget, text="  Budget  ")

# one StringVar per category for the budget input fields
budget_vars = {}
for cat in CATEGORIES:
    budget_vars[cat] = tk.StringVar()

tk.Label(tab_budget, text="Set Monthly Budget Limits",
         font=("Helvetica", 13, "bold"), bg="white", fg="black").pack(pady=(14, 6))

budget_input_frame = tk.Frame(tab_budget, bg="white", padx=30)
budget_input_frame.pack(fill="x")

# create a label and entry for each category
for i, cat in enumerate(CATEGORIES):
    tk.Label(budget_input_frame, text=f"{cat}:", bg="white", font=("Helvetica", 11),
             width=14, anchor="w").grid(row=i, column=0, pady=3, sticky="w")
    tk.Entry(budget_input_frame, textvariable=budget_vars[cat],
             font=("Helvetica", 11), width=12).grid(row=i, column=1, pady=3, padx=(8, 0), sticky="w")
    tk.Label(budget_input_frame, text="(leave blank = no limit)", bg="white",
             font=("Helvetica", 9), fg="gray").grid(row=i, column=2, padx=(8, 0), sticky="w")

tk.Button(tab_budget, text="Save Budget Limits", command=set_budgets,
          font=("Helvetica", 11, "bold"), bg="blue", fg="white",
          padx=14, pady=6, relief="flat").pack(pady=10)

tk.Frame(tab_budget, bg="gray", height=1).pack(fill="x", padx=20, pady=(0, 8))

tk.Label(tab_budget, text="Spending Summary",
         font=("Helvetica", 13, "bold"), bg="white", fg="black").pack(pady=(0, 6))

# column headers for the summary table
summary_header = tk.Frame(tab_budget, bg="gray")
summary_header.pack(fill="x", padx=20)
for col, w in [("Category", 14), ("Spent", 10), ("Budget", 10), ("Remaining", 10)]:
    tk.Label(summary_header, text=col, font=("Courier", 10, "bold"),
             bg="gray", fg="white", width=w, anchor="w").pack(side="left", padx=4, pady=4)

# dictionaries to hold the summary labels so update_summary() can update them
summary_spent_labels = {}
summary_limit_labels = {}
summary_remaining_labels = {}

summary_frame = tk.Frame(tab_budget, bg="white")
summary_frame.pack(fill="x", padx=20)

# one row per category with alternating background colors
for i, cat in enumerate(CATEGORIES):
    if i % 2 == 0:
        bg = "white"
    else:
        bg = "lightblue"
    row = tk.Frame(summary_frame, bg=bg)
    row.pack(fill="x")
    tk.Label(row, text=cat, font=("Courier", 10), bg=bg, width=14, anchor="w").pack(side="left", padx=4, pady=3)
    summary_spent_labels[cat] = tk.Label(row, text="$0.00", font=("Courier", 10), bg=bg, width=10, anchor="w", fg="black")
    summary_limit_labels[cat] = tk.Label(row, text="No limit", font=("Courier", 10), bg=bg, width=10, anchor="w", fg="black")
    summary_remaining_labels[cat] = tk.Label(row, text="-", font=("Courier", 10), bg=bg, width=10, anchor="w", fg="black")
    summary_spent_labels[cat].pack(side="left", padx=4)
    summary_limit_labels[cat].pack(side="left", padx=4)
    summary_remaining_labels[cat].pack(side="left", padx=4)

# load saved data when the app starts
load_budgets()
load_expenses()

# starts the event loop - keeps the window open
# Source: https://docs.python.org/3/library/tkinter.html
root.mainloop()
