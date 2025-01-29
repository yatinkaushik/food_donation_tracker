import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import random
import string

# Database setup
def connect_db():
    conn = sqlite3.connect("food_donation.db")
    cursor = conn.cursor()
    
    # Drop the table if it exists to ensure a fresh start
    cursor.execute("DROP TABLE IF EXISTS donations")
    
    cursor.execute("""
        CREATE TABLE donations (
            id TEXT PRIMARY KEY,
            donor_name TEXT,
            food_item TEXT,
            quantity INTEGER,
            expiry_date TEXT,
            status TEXT DEFAULT 'Pending',
            claimer_name TEXT DEFAULT NULL,
            claimer_contact TEXT DEFAULT NULL
        )
    """)
    conn.commit()
    conn.close()

# Function to generate a random 6-character ID
def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Function to validate if the date is in the future and in the correct format
def validate_expiry_date(date_str):
    try:
        # Check if date format is dd-mm-yyyy
        expiry_date = datetime.strptime(date_str, "%d-%m-%Y")
        
        # Ensure the expiry date is in the future
        if expiry_date > datetime.now():
            return True
        else:
            messagebox.showwarning("Date Error", "Expiry date must be a future date.")
            return False
    except ValueError:
        messagebox.showwarning("Date Format Error", "Please enter a valid date in the format dd-mm-yyyy.")
        return False

# Function to add donation
def add_donation():
    donor = donor_entry.get()
    food = food_entry.get()
    qty = qty_entry.get()
    expiry = expiry_entry.get()
    
    if donor and food and qty and expiry:
        if validate_expiry_date(expiry):  # Check expiry date validity
            donor_id = generate_id()  # Generate a random 6-character ID for every donor
            
            # Insert donation into database
            conn = sqlite3.connect("food_donation.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO donations (id, donor_name, food_item, quantity, expiry_date, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                           (donor_id, donor, food, qty, expiry))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Donation added successfully!")
            load_donations()
            reset_donor_form()
        else:
            messagebox.showwarning("Invalid Expiry", "Please enter a valid future expiry date.")
    else:
        messagebox.showwarning("Input Error", "Please fill all fields.")

# Function to load donations and sort them by expiry date
def load_donations():
    conn = sqlite3.connect("food_donation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, donor_name, food_item, quantity, expiry_date, status, claimer_name FROM donations WHERE status = 'Pending' ORDER BY expiry_date ASC")
    rows = cursor.fetchall()
    conn.close()
    
    tree.delete(*tree.get_children())
    for row in rows:
        donation_id, donor_name, food_item, quantity, expiry_date, status, claimer_name = row
        # If a claimer exists, show their name, otherwise show "None"
        claimer_display = claimer_name if claimer_name else "None"
        tree.insert("", tk.END, values=(donation_id, donor_name, food_item, quantity, expiry_date, status, claimer_display))

# Function to reset the donor form
def reset_donor_form():
    donor_entry.delete(0, tk.END)
    food_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    expiry_entry.delete(0, tk.END)

# Function to show claimer section
def show_claimer_section():
    claimer_frame.pack(pady=5)

# Function to claim donation
def claim_donation():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a donation to claim.")
        return
    
    donation_id = tree.item(selected_item, "values")[0]
    status = tree.item(selected_item, "values")[5]
    
    if status == "Claimed":
        messagebox.showwarning("Claim Error", "This donation has already been claimed.")
        return
    
    claimer = claimer_entry.get()
    contact = contact_entry.get()
    
    if not claimer or not contact:
        messagebox.showwarning("Input Error", "Please enter claimer's name and contact details.")
        return
    
    conn = sqlite3.connect("food_donation.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE donations SET status='Claimed', claimer_name=?, claimer_contact=? WHERE id=?", (claimer, contact, donation_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Donation claimed successfully!")
    load_donations()
    claimer_frame.pack_forget()

# Function to check the status of a donation
def check_donation_status():
    donor_id = donation_id_entry.get()
    
    if donor_id:
        conn = sqlite3.connect("food_donation.db")
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM donations WHERE id=?", (donor_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            status = result[0]
            if status == 'Claimed':
                messagebox.showinfo("Donation Status", "Your donation has been claimed.")
            else:
                messagebox.showinfo("Donation Status", "Your donation is still pending.")
        else:
            messagebox.showwarning("Donation Not Found", "No donation found with the given ID.")
    else:
        messagebox.showwarning("Input Error", "Please enter a valid donation ID.")

# Function to check donation and claim history by donor's name
def check_donor_history():
    donor_name = donor_history_entry.get()
    
    if donor_name:
        conn = sqlite3.connect("food_donation.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, food_item, quantity, expiry_date, status, claimer_name FROM donations WHERE donor_name=?", (donor_name,))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            # Clear existing table entries
            donor_history_tree.delete(*donor_history_tree.get_children())
            
            # Insert the donor history into the table
            for row in rows:
                donation_id, food_item, quantity, expiry_date, status, claimer_name = row
                claimer_display = claimer_name if claimer_name else "None"
                donor_history_tree.insert("", tk.END, values=(donation_id, food_item, quantity, expiry_date, status, claimer_display))
        else:
            messagebox.showwarning("No History", "No donation history found for this donor.")
    else:
        messagebox.showwarning("Input Error", "Please enter a valid donor name.")

# GUI setup
root = tk.Tk()
root.title("Food Donation Tracker")
root.geometry("800x600")

# Call the function to connect to the database and create the table when the program starts
connect_db()

# Donor Section
tk.Label(root, text="Donor Section", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(root, text="Donor Name:").pack()
donor_entry = tk.Entry(root)
donor_entry.pack()

tk.Label(root, text="Food Item:").pack()
food_entry = tk.Entry(root)
food_entry.pack()

tk.Label(root, text="Quantity:").pack()
qty_entry = tk.Entry(root)
qty_entry.pack()

tk.Label(root, text="Expiry Date (dd-mm-yyyy):").pack()
expiry_entry = tk.Entry(root)
expiry_entry.pack()

tk.Button(root, text="Add Donation", command=add_donation).pack(pady=5)

# Donation Table with Scrollbar
tk.Label(root, text="Donations:", font=("Arial", 12, "bold")).pack(pady=5)

# Frame for Treeview (Donation Table)
donation_frame = tk.Frame(root)
donation_frame.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(donation_frame, columns=("ID", "Donor", "Food", "Quantity", "Expiry Date", "Status", "Claimer"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Donor", text="Donor Name")
tree.heading("Food", text="Food Item")
tree.heading("Quantity", text="Quantity")
tree.heading("Expiry Date", text="Expiry Date")
tree.heading("Status", text="Status")
tree.heading("Claimer", text="Claimer")

tree.pack(fill=tk.BOTH, expand=True)

tk.Button(root, text="Claim Selected Donation", command=show_claimer_section).pack(pady=5)

# Claimer Section (Initially Hidden)
claimer_frame = tk.Frame(root)
tk.Label(claimer_frame, text="Claimer Section", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(claimer_frame, text="Claimer Name:").pack()
claimer_entry = tk.Entry(claimer_frame)
claimer_entry.pack()

tk.Label(claimer_frame, text="Claimer Contact:").pack()
contact_entry = tk.Entry(claimer_frame)
contact_entry.pack()

tk.Button(claimer_frame, text="Confirm Claim", command=claim_donation).pack(pady=5)

# Donation Status Section
tk.Label(root, text="Check Donation Status", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(root, text="Donation ID:").pack()
donation_id_entry = tk.Entry(root)
donation_id_entry.pack()

tk.Button(root, text="Check Status", command=check_donation_status).pack(pady=5)

# Donor History Section
tk.Label(root, text="Check Donor History", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(root, text="Donor Name:").pack()
donor_history_entry = tk.Entry(root)
donor_history_entry.pack()

tk.Button(root, text="Check History", command=check_donor_history).pack(pady=5)

# Initial data load
load_donations()

root.mainloop()
