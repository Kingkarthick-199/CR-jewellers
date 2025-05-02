import sqlite3
import pyttsx3
import customtkinter as ctk
from tkinter import messagebox
from tkinter import simpledialog
import datetime
import tkinter as tk
import matplotlib.pyplot as plt
import csv
from tkinter import PhotoImage
from PIL import Image, ImageTk
import time
import win32print
import win32ui
from PIL import ImageWin
import speech_recognition as sr
from tkcalendar import DateEntry
import re
import base64
from word2number import w2n
import inflect
from tkinter import ttk
import os
import sys


# Initialize text-to-speech engine
engine = pyttsx3.init()


# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Database connection
conn = sqlite3.connect("jewellery_shop.db", check_same_thread=False)
cursor = conn.cursor()



cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS inventory (
        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        quantity INTEGER,
        low_stock_threshold INTEGER DEFAULT 5,
        brand TEXT,
        supplier TEXT,
        purchase_date TEXT,
        description TEXT
    );
''')

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    );
''')


# Create Customers Table
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        contact_number TEXT NOT NULL
    );
''')

# Create Purchases Table
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        item_id TEXT,
        item_name TEXT,
        quantity INTEGER,
        item_price REAL,
        subtotal REAL,
        tax REAL,
        total_price REAL,
        purchase_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
''')

# Create a View for Customer Purchases
cursor.execute(''' 
    CREATE VIEW IF NOT EXISTS customer_purchases AS
    SELECT 
        c.customer_id,
        c.customer_name,
        c.contact_number,
        p.item_name,
        p.quantity,
        p.item_price,
        p.subtotal,
        p.tax,
        p.total_price,
        p.purchase_date
    FROM customers c
    JOIN purchases p ON c.customer_id = p.customer_id;
''')

conn.commit()


cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        item_name TEXT,  -- Added item_name column
        quantity INTEGER,
        sale_date TEXT,
        FOREIGN KEY (item_id) REFERENCES inventory(stock_id)
    );
''')
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        total_amount REAL,
        tax REAL,
        purchase_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
''')

cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS bill_items (
        bill_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        item_id INTEGER,
        item_name TEXT,
        quantity INTEGER,
        price_per_item REAL,
        subtotal REAL,
        FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
        FOREIGN KEY (item_id) REFERENCES inventory(stock_id)
    );
''')

conn.commit()

# Function to establish a connection with retry logic to avoid lock issues
def get_db_connection(retries=5, delay=2):
    for i in range(retries):
        try:
            conn = sqlite3.connect("jewellery_shop.db", timeout=10, check_same_thread=False)
            return conn
        except sqlite3.OperationalError:
            if i < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                raise

conn = get_db_connection()
cursor = conn.cursor()




# Authentication functions
# Define static admin username and password
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"

def login_user(username, password):
    
   # Check for the admin credentials
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True
    else:
        return False


# Application UI
def main_interface():

 
# Main interface window
    app = ctk.CTk()
    app.title(" CR Jewellery")
    app.geometry("700x500")


    # Create a black background with a creative infusion of other colors using a canvas
    canvas = tk.Canvas(app, width=700, height=500)
    canvas.pack(fill="both", expand=True)

    # Create gradient-like effect using a series of rectangles with different colors
    colors = ['#000000', '#0a0a0a', '#1f1f1f', '#343434', '#4a4a4a', '#616161']  # Shades of black and gray
    for i, color in enumerate(colors):
        canvas.create_rectangle(0, (i * 80), 700, (i * 80) + 80, fill=color, outline=color)

    # Add some random color splashes for creativity
    canvas.create_oval(500, 50, 600, 150, fill='#f0c100', outline='yellow')  # Yellow splash
    canvas.create_oval(300, 300, 400, 400, fill='#d62c2f', outline='red')    # Red splash
    canvas.create_oval(100, 100, 200, 200, fill='#0f78bc', outline='blue')   # Blue splash
    canvas.create_oval(350, 50, 450, 150, fill='#28a745', outline='green')   # Green splash

    # Add Item button
    def add_item():
        add_item_window = ctk.CTkToplevel()
        add_item_window.title("Add Item")
        add_item_window.geometry("900x700")
        add_item_window.configure(bg="#f5f5dc")  # Unique Background

    # Scrollable Frame
        scrollable_frame = ctk.CTkScrollableFrame(add_item_window)
        scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        categories = [
            "Rings", "Necklaces", "Bracelets", "Earrings", "Watches",
            "Anklets", "Brooches", "Pendants", "Gold", "Silver", "Platinum"
        ]

        fields = [
            ("Item Name", "Enter item name"),
            ("Category", "Select category"),
            ("Price", "Enter price"),
            ("Quantity in Stock", "Enter stock quantity"),
            ("Low Stock Threshold", "Default is 5"),
            ("Brand", "Enter brand"),
            ("Supplier", "Enter supplier"),
            ("Purchase Date", datetime.datetime.now().strftime("%d/%m/%y")),
            ("Description", "Enter description")
        ]

        entries = {}
        for idx, (label_text, placeholder) in enumerate(fields):
            label = ctk.CTkLabel(scrollable_frame, text=f"{label_text}:", fg_color="transparent", font=("Arial", 14))
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            if label_text == "Category":
               entry = ctk.CTkComboBox(scrollable_frame, values=categories)
               entry.set(categories[0])
            elif label_text == "Purchase Date":
                entry = DateEntry(scrollable_frame, date_pattern="dd/MM/yy", width=18, background="darkblue", foreground="white")
            else:
                entry = ctk.CTkEntry(scrollable_frame, placeholder_text=placeholder, font=("Arial", 14), width=250)

            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")
            entries[label_text.lower().replace(" ", "_")] = entry
    
        entries["low_stock_threshold"].insert(0, "5")

        def validate_inputs():
            errors = []
            if not entries["item_name"].get().strip():
                errors.append("Item Name is required.")
            try:
                price = float(entries["price"].get())
                if price < 0:
                   errors.append("Price cannot be negative.")
            except ValueError:
                errors.append("Price must be a valid number.")
            try:
                quantity = int(entries["quantity_in_stock"].get())
                if quantity < 0:
                   errors.append("Quantity cannot be negative.")
            except ValueError:
                errors.append("Quantity must be a valid integer.")
            if errors:
                messagebox.showerror("Validation Errors", "\n".join(errors))
                return False
            return True

        def submit_item():
            if not validate_inputs():
               return
            cursor.execute("SELECT MAX(stock_id) FROM inventory")
            result = cursor.fetchone()
            next_stock_id = 1 if result[0] is None else result[0] + 1
            purchase_date = entries["purchase_date"].get()
            formatted_date = datetime.datetime.strptime(purchase_date, "%d/%m/%y").strftime("%d/%m/%y")
            cursor.execute("""
                INSERT INTO inventory (stock_id, name, category, price, quantity, low_stock_threshold, brand, supplier, purchase_date, description) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                next_stock_id,
                entries["item_name"].get(),
                entries["category"].get(),
                float(entries["price"].get()),
                int(entries["quantity_in_stock"].get()),
                int(entries["low_stock_threshold"].get()),
                entries["brand"].get(),
                entries["supplier"].get(),
                formatted_date,
                entries["description"].get(),
            ))
            conn.commit()
            messagebox.showinfo("Success", f"Item added with Stock ID: {next_stock_id}")
            add_item_window.destroy()
            
       
        def recognize_voice_command():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                engine.say("Listening for your command. Speak now.")
                engine.runAndWait()
                try:
                    voice_input = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(voice_input).lower()
                    engine.say(f"You said: {command}")
                    engine.runAndWait()
                    if "submit" in command:
                        submit_item()
                        return
                    for field_key, entry in entries.items():
                        field_name = field_key.replace("_", " ").lower()
                        if field_name in command:
                            value = command.split(field_name)[-1].strip()
                            if field_name == "price":
                            # Ensure price is a valid number
                                price_value = re.sub(r'\D', '', value)  # Remove any non-numeric characters
                                if price_value:
                                    entry.delete(0, tk.END)
                                    entry.insert(0, price_value)
                                    engine.say(f"Set {field_name} to {price_value}")
                                    engine.runAndWait()
                                else:
                                    engine.say("Price must be a valid number.")
                                    engine.runAndWait()
                            else:
                                entry.delete(0, tk.END)
                                entry.insert(0, value)
                                engine.say(f"Set {field_name} to {value}")
                                engine.runAndWait()
                            return
                    engine.say("Command not recognized. Try again.")
                    engine.runAndWait()
                except sr.UnknownValueError:
                    engine.say("Could not understand. Please try again.")
                    engine.runAndWait()
                except sr.RequestError:
                    engine.say("Voice service unavailable.")
                    engine.runAndWait()

        submit_button = ctk.CTkButton(scrollable_frame, text="Submit", command=submit_item)
        submit_button.grid(row=len(fields), column=0, columnspan=2, pady=20)
    
        voice_button = ctk.CTkButton(scrollable_frame, text="🎤 Voice Input", command=recognize_voice_command)
        voice_button.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)
    
        back_button = ctk.CTkButton(scrollable_frame, text="⬅ Back", command=add_item_window.destroy)
        back_button.grid(row=len(fields) + 2, column=0, pady=10)
    
        logout_button = ctk.CTkButton(scrollable_frame, text="🚪 Logout", command=lambda: messagebox.showinfo("Logout", "Logging out..."))
        logout_button.grid(row=len(fields) + 2, column=1, pady=10)


    def generate_bill():
        generate_bill_window = ctk.CTkToplevel(app)
        generate_bill_window.title("Generate Bill")
        generate_bill_window.geometry("800x600")

        TAX_RATE = 0.10  # 10% tax
        DISCOUNT_PERCENTAGE = 15  # Fixed 15% discount

        fields = [
           ("Customer Name", "Enter customer name"),
           ("Contact Number", "Enter contact number"),
        ]

        entries = {}
        for idx, (label_text, placeholder) in enumerate(fields):
            label = ctk.CTkLabel(generate_bill_window, text=label_text)
            label.grid(row=idx + 1, column=0, padx=10, pady=10, sticky="w")

            entry = ctk.CTkEntry(generate_bill_window, placeholder_text=placeholder)
            entry.grid(row=idx + 1, column=1, padx=10, pady=10, sticky="ew")
            entries[label_text.lower().replace(" ", "_")] = entry

        item_entries = []

        def add_item_fields():
            """Dynamically add new item fields."""
            row = len(fields) + len(item_entries) + 1
            item_fields = [("Item ID", "Enter item ID"), ("Quantity", "Enter quantity")]

            item_entry = {}
            for idx, (label_text, placeholder) in enumerate(item_fields):
                label = ctk.CTkLabel(generate_bill_window, text=label_text)
                label.grid(row=row, column=idx * 2, padx=10, pady=10, sticky="w")

                entry = ctk.CTkEntry(generate_bill_window, placeholder_text=placeholder)
                entry.grid(row=row, column=idx * 2 + 1, padx=10, pady=10, sticky="ew")
                item_entry[label_text.lower().replace(" ", "_")] = entry

            item_entries.append(item_entry)

        
        def submit_bill():
            """Process and generate the bill with a fixed 15% discount applied."""
            error_messages = []
            for field, entry in entries.items():
                if not entry.get().strip():
                    error_messages.append(f"{field.replace('_', ' ').capitalize()} is required.")

            if error_messages:
                messagebox.showerror("Validation Error", "\n".join(error_messages))
                return

            total_subtotal = 0
            total_tax = 0
            total_amount = 0
            items_list = []

            customer_name = entries["customer_name"].get().strip()
            contact_number = entries["contact_number"].get().strip()
            purchase_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("SELECT customer_id FROM customers WHERE contact_number = ?", (contact_number,))
            customer = cursor.fetchone()
            if customer:
                customer_id = customer[0]
            else:
                cursor.execute("INSERT INTO customers (customer_name, contact_number) VALUES (?, ?)",
                                (customer_name, contact_number))
                customer_id = cursor.lastrowid

            for item_entry in item_entries:
                item_id = item_entry["item_id"].get()
                quantity = item_entry["quantity"].get()

                if not item_id or not quantity:
                   continue  # Skip if item fields are incomplete

                try:
                    quantity = int(quantity)
                    if quantity <= 0:
                       raise ValueError("Quantity must be positive.")
                except ValueError:
                    messagebox.showerror("Validation Error", "Quantity must be a valid positive integer.")
                    return

                cursor.execute("SELECT name, price, quantity FROM inventory WHERE stock_id = ?", (item_id,))
                item = cursor.fetchone()

                if not item:
                   messagebox.showerror("Error", f"Item with ID {item_id} not found!")
                   return

                item_name, item_price, available_quantity = item

                if quantity > available_quantity:
                   messagebox.showerror("Error", f"Requested quantity for {item_name} exceeds available stock.")
                   return

                subtotal = item_price * quantity
                tax = subtotal * TAX_RATE
                total_price = subtotal + tax

                total_subtotal += subtotal
                total_tax += tax
                total_amount += total_price

                items_list.append((item_name, quantity, item_price, subtotal, tax, total_price))

                cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE stock_id = ?", (quantity, item_id))
                conn.commit()

                cursor.execute("DELETE FROM inventory WHERE stock_id = ? AND quantity <= 0", (item_id,))
                conn.commit()

                cursor.execute("INSERT INTO sales (item_id, item_name, quantity, sale_date) VALUES (?, ?, ?, ?)",
                                (item_id, item_name, quantity, purchase_date))

                cursor.execute(
                    "INSERT INTO purchases (customer_id, item_id, item_name, quantity, item_price, subtotal, tax, total_price, purchase_date) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (customer_id, item_id, item_name, quantity, item_price, subtotal, tax, total_price, purchase_date))
                conn.commit()

            discount_amount = (DISCOUNT_PERCENTAGE / 100) * total_subtotal
            final_total = (total_subtotal - discount_amount) + total_tax

            bill_window = ctk.CTkToplevel(generate_bill_window)
            bill_window.title("Bill Receipt")
            bill_window.geometry("700x500")

           # Header Information
            header_frame = ctk.CTkFrame(bill_window)
            header_frame.pack(pady=10, padx=10, fill="x")

            ctk.CTkLabel(header_frame, text="BILL RECEIPT", font=("Arial", 18, "bold")).pack()
            ctk.CTkLabel(header_frame, text=f"CUSTOMER: {customer_name}", font=("Arial", 14)).pack()
            ctk.CTkLabel(header_frame, text=f"CONTACT: {contact_number}", font=("Arial", 14)).pack()
            ctk.CTkLabel(header_frame, text=f"DATE: {purchase_date}", font=("Arial", 14)).pack()

        # Table Frame
            table_frame = ctk.CTkFrame(bill_window)
            table_frame.pack(pady=10, padx=10, fill="both", expand=True)

            columns = ("Item Name", "Quantity", "Price", "Subtotal", "Tax", "Total")
            bill_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

            for col in columns:
               bill_table.heading(col, text=col)
               bill_table.column(col, width=100, anchor="center")

            for item in items_list:
               bill_table.insert("", "end", values=item)

            bill_table.pack(fill="both", expand=True)

        # Footer for Totals
            footer_frame = ctk.CTkFrame(bill_window)
            footer_frame.pack(pady=10, padx=10, fill="x")

            ctk.CTkLabel(footer_frame, text=f"Subtotal: ${total_subtotal:,.2f}", font=("Arial", 14)).pack(anchor="e")
            ctk.CTkLabel(footer_frame, text=f"Tax (10%): ${total_tax:,.2f}", font=("Arial", 14)).pack(anchor="e")
            ctk.CTkLabel(footer_frame, text=f"Discount (15%): -${discount_amount:,.2f}", font=("Arial", 14)).pack(anchor="e")

            total_label = ctk.CTkLabel(footer_frame, text=f"Total Amount: ${final_total:,.2f}",
                                       font=("Arial", 18, "bold"), text_color="white")
            total_label.pack(pady=10, anchor="e")

            messagebox.showinfo("Bill Generated", "Bill generated successfully!")


        def recognize_voice_command():
            """Recognize voice input to populate fields."""
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                engine.say("Listening for your command. Please speak now.")
                engine.runAndWait()
                try:
                    voice_input = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(voice_input).lower()
                    engine.say(f"You said: {command}")
                    engine.runAndWait()

                    if "generate bill" in command:
                       engine.say("Generating the bill.")
                       engine.runAndWait()
                       submit_bill()
                       return

                    for field_key, entry in entries.items():
                        field_name = field_key.replace("_", " ").lower()
                        if field_name in command:
                            value = command.split(field_name)[-1].strip()
                            if value:
                                entry.delete(0, tk.END)
                                entry.insert(0, value)
                                engine.say(f"Set {field_name} to {value}")
                                engine.runAndWait()
                                return

                except sr.UnknownValueError:
                    engine.say("Sorry, I could not understand.")
                    engine.runAndWait()
                except sr.RequestError:
                    engine.say("Voice recognition service unavailable.")
                    engine.runAndWait()

    # Create a top frame for menu-style buttons using .grid() instead of .pack()
        menu_frame = ctk.CTkFrame(generate_bill_window)
        menu_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

# Voice Button (🎤) - Left side in menu bar
        voice_button = ctk.CTkButton(menu_frame, text="🎤 Voice Command", command=recognize_voice_command)
        voice_button.grid(row=0, column=0, padx=10, pady=5)

# Add Item Button - Next to voice button
        add_item_button = ctk.CTkButton(menu_frame, text="➕ Add Item", command=add_item_fields)
        add_item_button.grid(row=0, column=1, padx=10, pady=5)

# Generate Bill Button - Next to Add Item
        submit_button = ctk.CTkButton(menu_frame, text="🧾 Generate Bill", command=submit_bill)
        submit_button.grid(row=0, column=2, padx=10, pady=5)



    # Add Update Item button
    def update_item():
        update_item_window = ctk.CTkToplevel(app)
        update_item_window.title("Update Item")
        update_item_window.geometry("500x600")

        # Labels and entry fields for update functionality
        stock_id_label = ctk.CTkLabel(update_item_window, text="Stock ID:")
        stock_id_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        stock_id = ctk.CTkEntry(update_item_window, placeholder_text="Enter stock ID")
        stock_id.grid(row=0, column=1, padx=10, pady=10)

        def fetch_item():
            cursor.execute("SELECT * FROM inventory WHERE stock_id = ?", (stock_id.get(),))
            item = cursor.fetchone()
            if item:
                for idx, value in enumerate(item[1:], start=1):
                    entries[list(entries.keys())[idx - 1]].delete(0, 'end')
                    entries[list(entries.keys())[idx - 1]].insert(0, value)
            else:
                messagebox.showerror("Error", "Item not found!")

        fetch_button = ctk.CTkButton(update_item_window, text="Fetch Item", command=fetch_item)
        fetch_button.grid(row=1, column=0, columnspan=2, pady=10)

        fields = [
            ("Item Name", "Enter item name"),
            ("Category", "Enter category"),
            ("Price", "Enter price"),
            ("Quantity in Stock", "Enter stock quantity"),
            ("Low Stock Threshold", "Low stock threshold"),
            ("Brand", "Enter brand"),
            ("Supplier", "Enter supplier"),
            ("Purchase Date", "Enter purchase date (YYYY-MM-DD)"),
            ("Description", "Enter product description")
        ]

        entries = {}
        for idx, (label_text, placeholder) in enumerate(fields, start=2):
            label = ctk.CTkLabel(update_item_window, text=f"{label_text}:")
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            
            entry = ctk.CTkEntry(update_item_window, placeholder_text=placeholder)
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")
            entries[label_text.lower().replace(" ", "_")] = entry

        def submit_update():
                cursor.execute(
                    '''UPDATE inventory SET name=?, category=?, price=?, quantity=?, low_stock_threshold=?, brand=?, supplier=?, purchase_date=?, description=? WHERE stock_id=?''', 
                    (
                    entries["item_name"].get(), entries["category"].get(), float(entries["price"].get()),
                    int(entries["quantity_in_stock"].get()), int(entries["low_stock_threshold"].get()), 
                    entries["brand"].get(), entries["supplier"].get(), entries["purchase_date"].get(), 
                    entries["description"].get(), stock_id.get()
                    )
                )
                conn.commit()
                messagebox.showinfo("Success", "Item updated successfully.")
                update_item_window.destroy()

        submit_button = ctk.CTkButton(update_item_window, text="Submit", command=submit_update)
        submit_button.grid(row=len(fields) + 2, column=0, columnspan=2, pady=20)
 # Voice Assistant Integration
        def recognize_voice_command():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
               engine.say("Listening for your command. Please speak now.")
               engine.runAndWait()
               try:
                # Listen and process voice input
                    voice_input = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(voice_input).lower()
                    engine.say(f"You said: {command}")
                    engine.runAndWait()

                # Check if the command is "fetch item"
                    if "fetch item" in command:
                        engine.say("Fetching the item.")
                        engine.runAndWait()
                        fetch_item()
                        return

                # Check if the command is "submit update"
                    if "submit update" in command:
                        engine.say("Submitting the update.")
                        engine.runAndWait()
                        submit_update()
                        return

                # Match commands to fields
                    for field_key, entry in entries.items():
                        field_name = field_key.replace("_", " ").lower()
                        if field_name in command:
                        # Extract value
                            value = None
                            if "set to" in command:
                                value = command.split("set to")[-1].strip()
                            elif "is" in command:
                                value = command.split("is")[-1].strip()
                            elif field_name in command:
                                value = command.split(field_name)[-1].strip()

                            if value:
                                entry.delete(0, tk.END)
                                entry.insert(0, value)
                                engine.say(f"Set {field_name} to {value}")
                                engine.runAndWait()
                                return
               except sr.UnknownValueError:
                    engine.say("Sorry, I could not understand your command. Please try again.")
                    engine.runAndWait()
               except sr.RequestError:
                    engine.say("Voice recognition service is unavailable. Please check your connection.")
                    engine.runAndWait()

        voice_button = ctk.CTkButton(update_item_window, text="🎤", command=recognize_voice_command)
        voice_button.grid(row=len(fields) + 3, column=0, columnspan=2, pady=10)

# Main Button to Open Update Item Window
    update_button = ctk.CTkButton(app, text="Update Item", command=update_item)
    update_button.pack(pady=20)

    

    def generate_report():
        report_window = ctk.CTkToplevel(app)
        report_window.title("Generate Report")
        report_window.geometry("500x400")

        report_type_label = ctk.CTkLabel(report_window, text="Select Report Type:")
        report_type_label.pack(pady=10)

        report_type = ctk.CTkComboBox(report_window, values=["Inventory Report", "Sales Report"])
        report_type.pack(pady=10)

        def generate():
            report_choice = report_type.get()

            try:
                if report_choice == "Inventory Report":
                    cursor.execute("SELECT * FROM inventory")
                    rows = cursor.fetchall()

                    if not rows:
                       messagebox.showinfo("No Data", "No inventory data available.")
                       return

                    inventory_report_data = [["Stock ID", "Item Name", "Category", "Price", "Quantity", 
                                            "Low Stock Threshold", "Brand", "Supplier", "Purchase Date", "Description"]]
                    for row in rows:
                        inventory_report_data.append(list(row))

                    with open('inventory_report.csv', 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerows(inventory_report_data)

                    messagebox.showinfo("Success", "Inventory report saved as 'inventory_report.csv'")

                elif report_choice == "Sales Report":
                   cursor.execute("""
                        SELECT s.sale_date, i.name AS item_name, i.category, i.price, s.quantity, 
                            (i.price * s.quantity) AS total_sales
                        FROM sales s
                        JOIN inventory i ON s.item_id = i.stock_id
                        ORDER BY s.sale_date
                    """)
                   rows = cursor.fetchall()

                   if not rows:
                       messagebox.showinfo("No Data", "No sales data available.")
                       return

                       sales_report_data = [["Sale Date", "Item Name", "Category", "Price per Item", "Quantity Sold", "Total Sales"]]
                       for row in rows:
                          sales_report_data.append(list(row))

                          with open('sales_report.csv', 'w', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerows(sales_report_data)

                            messagebox.showinfo("Success", "Sales report saved as 'sales_report.csv'")

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        generate_button = ctk.CTkButton(report_window, text="Generate Report", command=generate)
        generate_button.pack(pady=20)

    def view_inventory():
    # Create a new window to display the inventory
        inventory_window = ctk.CTkToplevel(app)
        inventory_window.title("View Inventory")
        inventory_window.geometry("1000x600")

    # Create a frame for search input and button
        search_frame = ctk.CTkFrame(inventory_window)
        search_frame.pack(pady=10)

    # Create search input field
        search_label = ctk.CTkLabel(search_frame, text="Search by Name or Category:", font=("Arial", 12))
        search_label.pack(side="left", padx=10)
    
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter search term")
        search_entry.pack(side="left", padx=10)

    # Function to search inventory
        def search_inventory():
            search_term = search_entry.get().lower()
            cursor.execute("SELECT * FROM inventory WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?", 
                       ('%' + search_term + '%', '%' + search_term + '%'))
            rows = cursor.fetchall()
            populate_inventory_table(rows)

        def voice_command():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                   messagebox.showinfo("Voice Assistant", "Listening for a stock name or ID...")
                   audio = recognizer.listen(source)
                   command = recognizer.recognize_google(audio).lower()

            # Extract stock name or ID based on a specific command format
                   if command.startswith("search stock"):
                      stock_name = command.replace("search stock", "").strip()
                      search_entry.delete(0, ctk.END)
                      search_entry.insert(0, stock_name)
                      search_inventory()

                   elif command.startswith("search id"):
                       stock_id = command.replace("search id", "").strip()
                       if stock_id.isdigit():  # Ensure it's a valid numeric ID
                           search_entry.delete(0, ctk.END)
                           search_entry.insert(0, stock_id)
                           search_inventory()
                       else:
                            messagebox.showwarning("Voice Assistant", "Invalid stock ID. Please say 'search ID <number>'.")

                   elif "close" in command:
                        inventory_window.destroy()

                   else:
                        messagebox.showinfo("Voice Assistant", f"Command not recognized: {command}\nTry saying 'Search stock <name>' or 'Search ID <number>'.")

                except Exception as e:
                    messagebox.showerror("Voice Assistant", f"Error: {e}")


    # Search button
        search_button = ctk.CTkButton(search_frame, text="Search", command=search_inventory)
        search_button.pack(side="left")

    # Voice Command button
        voice_button = ctk.CTkButton(search_frame, text="🎤", command=voice_command)
        voice_button.pack(side="left", padx=10)
    # Create a scrollable frame for the inventory items
        scrollable_frame = ctk.CTkScrollableFrame(inventory_window)
        scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    # Function to delete an inventory item
        def delete_inventory_item(stock_id):
            try:
                cursor.execute("DELETE FROM inventory WHERE stock_id = ?", (stock_id,))
                conn.commit()

                # Reorganize the stock_id values to remove gaps
                reorganize_stock_ids()
                messagebox.showinfo("Success", "Item deleted successfully.")
                populate_inventory_table(fetch_inventory_data())  # Refresh the inventory after deletion
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {e}")

        def reorganize_stock_ids():
            try:
            # Fetch the inventory items again in sorted order
                cursor.execute("SELECT stock_id FROM inventory ORDER BY stock_id")
                rows = cursor.fetchall()
                for idx, row in enumerate(rows, start=1):
                   cursor.execute("UPDATE inventory SET stock_id = ? WHERE stock_id = ?", (idx, row[0]))
                   conn.commit()
            except Exception as e:
                  messagebox.showerror("Error", f"Failed to reorganize stock IDs: {e}")


    # Function to fetch inventory data
        def fetch_inventory_data():
            cursor.execute("SELECT * FROM inventory")
            return cursor.fetchall()

    # Function to populate the inventory table
        def populate_inventory_table(rows):
        # Clear the existing contents of the scrollable frame
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

        # Add column headers (labels) in the first row
            headers = ["Stock ID", "Item_Name", "Category", "Price", "Quantity", "Low Stock Threshold", "Brand", "Supplier", "Purchase Date", "Description", "Actions"]
            for idx, header in enumerate(headers):
                label = ctk.CTkLabel(scrollable_frame, text=header, font=("Arial", 12, "bold"))
                label.grid(row=0, column=idx, padx=10, pady=5, sticky="w")

        # Display each inventory item in the form
            for row_idx, row in enumerate(rows, start=1):
                for col_idx, value in enumerate(row):
                    label = ctk.CTkLabel(scrollable_frame, text=value, font=("Arial", 10))
                    label.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="w")

            # Delete button for each row
                delete_button = ctk.CTkButton(scrollable_frame, text="Delete", 
                                          command=lambda stock_id=row[0]: delete_inventory_item(stock_id))
                delete_button.grid(row=row_idx, column=len(row), padx=10, pady=5)

                

    # Fetch the inventory data and populate the table
        rows = fetch_inventory_data()
        populate_inventory_table(rows)

    # Add a Close button to close the window
        close_button = ctk.CTkButton(inventory_window, text="Close", command=inventory_window.destroy)
        close_button.pack(pady=10)

    

    def update_customer_record():
        update_customer_window = ctk.CTkToplevel()
        update_customer_window.title("Update Customer Purchase")
        update_customer_window.geometry("400x600")

    # Labels and Input Fields
        customer_name_label = ctk.CTkLabel(update_customer_window, text="Customer Name:")
        customer_name_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        customer_name = ctk.CTkEntry(update_customer_window, placeholder_text="Enter customer name")
        customer_name.grid(row=0, column=1, padx=(5, 10), pady=10)

        contact_number_label = ctk.CTkLabel(update_customer_window, text="Contact Number:")
        contact_number_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="w")
        contact_number = ctk.CTkEntry(update_customer_window, placeholder_text="Enter contact number")
        contact_number.grid(row=1, column=1, padx=(5, 10), pady=10)

        item_name_label = ctk.CTkLabel(update_customer_window, text="Item Name:")
        item_name_label.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="w")
        item_name = ctk.CTkEntry(update_customer_window, placeholder_text="Enter item name")
        item_name.grid(row=2, column=1, padx=(5, 10), pady=10)

        quantity_label = ctk.CTkLabel(update_customer_window, text="Quantity:")
        quantity_label.grid(row=3, column=0, padx=(10, 5), pady=10, sticky="w")
        quantity = ctk.CTkEntry(update_customer_window, placeholder_text="Enter quantity")
        quantity.grid(row=3, column=1, padx=(5, 10), pady=10)

        item_price_label = ctk.CTkLabel(update_customer_window, text="Item Price:")
        item_price_label.grid(row=4, column=0, padx=(10, 5), pady=10, sticky="w") 
        item_price = ctk.CTkEntry(update_customer_window, placeholder_text="Enter item price")
        item_price.grid(row=4, column=1, padx=(5, 10), pady=10)

        subtotal_label = ctk.CTkLabel(update_customer_window, text="Subtotal:")
        subtotal_label.grid(row=5, column=0, padx=(10, 5), pady=10, sticky="w") 
        subtotal = ctk.CTkEntry(update_customer_window, state="readonly")
        subtotal.grid(row=5, column=1, padx=(5, 10), pady=10)

        tax_label = ctk.CTkLabel(update_customer_window, text="Tax (10%):")
        tax_label.grid(row=6, column=0, padx=(10, 5), pady=10, sticky="w") 
        tax = ctk.CTkEntry(update_customer_window, state="readonly")
        tax.grid(row=6, column=1, padx=(5, 10), pady=10)

        total_price_label = ctk.CTkLabel(update_customer_window, text="Total Price:")
        total_price_label.grid(row=7, column=0, padx=(10, 5), pady=10, sticky="w") 
        total_price = ctk.CTkEntry(update_customer_window, state="readonly")
        total_price.grid(row=7, column=1, padx=(5, 10), pady=10)

    # Function to Fetch Existing Purchase Data
        def fetch_customer_data():
            conn = sqlite3.connect("jewellery_shop.db")
            cursor = conn.cursor()

    # Get customer ID using only customer name
            cursor.execute("SELECT customer_id FROM customers WHERE customer_name = ?", (customer_name.get(),))
            customer = cursor.fetchone()

            if customer:
                customer_id = customer[0]  # Extract customer_id

        # Fetch latest purchase details using customer_id
                cursor.execute("SELECT item_name, quantity, item_price, subtotal, tax, total_price FROM purchases WHERE customer_id = ? ORDER BY purchase_date DESC LIMIT 1", 
                               (customer_id,))
                record = cursor.fetchone()

                if record:
                   item_name.delete(0, ctk.END)
                   item_name.insert(0, record[0])

                   quantity.delete(0, ctk.END)
                   quantity.insert(0, str(record[1]))

                   item_price.delete(0, ctk.END)
                   item_price.insert(0, str(record[2]))

                   subtotal.configure(state="normal")
                   subtotal.delete(0, ctk.END)
                   subtotal.insert(0, str(record[3]))
                   subtotal.configure(state="readonly")

                   tax.configure(state="normal")
                   tax.delete(0, ctk.END)
                   tax.insert(0, str(record[4]))
                   tax.configure(state="readonly")

                   total_price.configure(state="normal")
                   total_price.delete(0, ctk.END)
                   total_price.insert(0, str(record[5]))
                   total_price.configure(state="readonly")

                   messagebox.showinfo("Success", "Customer purchase data fetched successfully.")
                else:
                   messagebox.showerror("Error", "No purchases found for this customer.")
            else:
                messagebox.showerror("Error", "Customer not found!")

            conn.close()


        def validate_and_update():
            if not item_name.get().strip() or not quantity.get().strip() or not item_price.get().strip():
                messagebox.showerror("Error", "All fields are required!")
                return  # This should be inside the `if` block

            try:
                qty = int(quantity.get())  # Ensure quantity is a valid integer
                price = float(item_price.get())  # Ensure price is a valid float
                subtotal_value = qty * price
                tax_value = round(subtotal_value * 0.10, 2)  # 10% tax
                total_value = round(subtotal_value + tax_value, 2)

                conn = sqlite3.connect("jewellery_shop.db")
                cursor = conn.cursor()

        # Get customer ID
                cursor.execute("SELECT customer_id FROM customers WHERE customer_name = ?", 
                            (customer_name.get(),))
                customer = cursor.fetchone()

                if customer:
                    customer_id = customer[0]  # Extract customer_id

            # Update the latest purchase record
                    cursor.execute("""
                        UPDATE purchases 
                        SET item_name = ?, quantity = ?, item_price = ?, subtotal = ?, tax = ?, total_price = ? 
                        WHERE customer_id = ? AND purchase_date = (SELECT MAX(purchase_date) FROM purchases WHERE customer_id = ?)
                        """, (item_name.get(), qty, price, subtotal_value, tax_value, total_value, customer_id, customer_id))

                    conn.commit()

                    messagebox.showinfo("Success", "Purchase record updated successfully.")
                    update_customer_window.destroy()
                else:
                    messagebox.showerror("Error", "Customer not found!")

                conn.close()

            except ValueError:
                messagebox.showerror("Error", "Invalid quantity or price. Please enter valid numbers.")



    # Fetch Button
        fetch_button = ctk.CTkButton(update_customer_window, text="Fetch Data", command=fetch_customer_data)
        fetch_button.grid(row=8, column=0, columnspan=2, pady=10)

    # Update Button
        update_button = ctk.CTkButton(update_customer_window, text="Update", command=validate_and_update)
        update_button.grid(row=9, column=0, columnspan=2, pady=10)



    def view_customer_records():
    # Create a new window for displaying records
        view_window = ctk.CTkToplevel()
        view_window.title("Customer Records")
        view_window.geometry("1200x700")  # Increased width for better spacing

    # Title Label
        title_label = ctk.CTkLabel(view_window, text="Customer Purchase Records", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

    # Create a frame for the table with scrollbars
        table_frame = ctk.CTkFrame(view_window)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = ctk.CTkCanvas(table_frame)
        scrollbar = ctk.CTkScrollbar(table_frame, command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Fetch data from the `customer_purchases` view
        cursor.execute("SELECT customer_name, contact_number, item_name, purchase_date, item_price, total_price, customer_id FROM customer_purchases")
        rows = cursor.fetchall()

    # Column Headers
        headers = ["Customer Name", "Contact", "Purchased Item", "Purchase Date", "Item Price", "Total Price Paid", "Actions"]
        col_widths = [180, 120, 180, 150, 120, 120, 120]  # Adjusted column widths

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            header_label = ctk.CTkLabel(scrollable_frame, text=header, font=("Arial", 12, "bold"), width=width)
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

    # Function to delete a customer and their purchases
        def delete_customer_record(customer_id):
            try:
                cursor.execute("DELETE FROM purchases WHERE customer_id = ?", (customer_id,))
                cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
                conn.commit()
                messagebox.showinfo("Success", "Customer record deleted.")
                view_window.destroy()
                view_customer_records()  # Refresh the window
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {e}")

    # Populate data in the grid
        for row_idx, row in enumerate(rows, start=1):
            customer_name, contact, item_name, purchase_date, item_price, total_price, customer_id = row

        # Display each field properly aligned
            ctk.CTkLabel(scrollable_frame, text=customer_name, width=col_widths[0], anchor="w").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(scrollable_frame, text=contact, width=col_widths[1], anchor="w").grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(scrollable_frame, text=item_name, width=col_widths[2], anchor="w").grid(row=row_idx, column=2, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(scrollable_frame, text=purchase_date, width=col_widths[3], anchor="w").grid(row=row_idx, column=3, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(scrollable_frame, text=f"${item_price:.2f}", width=col_widths[4], anchor="w").grid(row=row_idx, column=4, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(scrollable_frame, text=f"${total_price:.2f}", width=col_widths[5], anchor="w").grid(row=row_idx, column=5, padx=5, pady=5, sticky="w")

        # Delete Button (properly aligned)
            delete_button = ctk.CTkButton(scrollable_frame, text="Delete", fg_color="red", width=col_widths[6] - 20,
                                        command=lambda id=customer_id: delete_customer_record(id))
            delete_button.grid(row=row_idx, column=6, padx=5, pady=5, sticky="w")

    # Close button
        close_button = ctk.CTkButton(view_window, text="Close", command=view_window.destroy)
        close_button.pack(pady=20)

    def fetch_sales():
        """ Fetches all sales records from the sales table """
        conn = sqlite3.connect("jewellery_shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT sale_id, item_id, item_name, quantity, sale_date FROM sales ORDER BY sale_date DESC")  
        sales = cursor.fetchall()
        conn.close()
        return sales  
        


    def record_sale():
        record_sale_window = ctk.CTkToplevel()
        record_sale_window.title("Record Sale")
        record_sale_window.geometry("1000x600")
   # Title
        ctk.CTkLabel(record_sale_window, text="Record Sale", font=("Arial", 16, "bold")).pack(pady=10)

    # Frame for displaying sales
        sales_frame = ctk.CTkFrame(record_sale_window)
        sales_frame.pack(pady=5, padx=10, fill="both", expand=True)


    # Table Headers
        columns = ("Sale ID", "Item ID", "Item Name", "Quantity", "Sale Date and time")
        sales_table = ttk.Treeview(sales_frame, columns=columns, show="headings")
    
        for col in columns:
            sales_table.heading(col, text=col)
            sales_table.column(col, width=100, anchor="center")  

        sales_table.pack(fill="both", expand=True, padx=5, pady=5)
     # Populate Table with Sales Data
        def populate_sales_table():
            sales_table.delete(*sales_table.get_children())  # Clear existing entries
            sales_data = fetch_sales()
            for sale in sales_data:
                sales_table.insert("", "end", values=sale)

        populate_sales_table()  # Load sales data into table

        def delete_selected_sale():
            selected_item = sales_table.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a sale to delete.")
                return

            sale_id = sales_table.item(selected_item, "values")[0]  # Get Sale ID from selected row
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Sale ID {sale_id}?")

            if confirm:
                try:
                    conn = sqlite3.connect("jewellery_shop.db")
                    cursor = conn.cursor()

            # Delete the selected sale
                    cursor.execute("DELETE FROM sales WHERE sale_id = ?", (sale_id,))
                    conn.commit()

            # Re-fetch sales ordered by original sale_id
                    cursor.execute("SELECT sale_id FROM sales ORDER BY sale_id ASC")
                    sales = cursor.fetchall()

            # Update Sale IDs sequentially from 1, 2, 3, 4...
                    new_id = 1
                    for old_sale_id, in sales:
                       cursor.execute("UPDATE sales SET sale_id = ? WHERE sale_id = ?", (new_id, old_sale_id))
                       new_id += 1  # Increment new sale_id sequentially

                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success", f"Sale ID {sale_id} deleted successfully and sales re-sequenced.")
                    populate_sales_table()  # Refresh table after deletion

                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")


    # Refresh Button
        refresh_button = ctk.CTkButton(record_sale_window, text="Refresh Sales", command=populate_sales_table)
        refresh_button.pack(pady=5)

        # Delete Selected Sale Button
        delete_button = ctk.CTkButton(record_sale_window, text="Delete Selected Sale", command=delete_selected_sale)
        delete_button.pack(pady=5)


      
    def logout():
        app.destroy()
        login_interface() 

    def view_sales():
        try:
        # Fetch data from the database
            cursor.execute("SELECT item_id, SUM(quantity) FROM sales GROUP BY item_id")
            rows = cursor.fetchall()
        
            if rows:
            # Prepare data for the graph
               item_ids = [str(row[0]) for row in rows]  # Convert item_id to strings for labels
               quantities = [row[1] for row in rows]
           # Plot the data
               plt.figure(figsize=(10, 6))
               plt.bar(item_ids, quantities, color="skyblue")
               plt.xlabel("Item ID")
               plt.ylabel("Total Quantity Sold")
               plt.title("Sales Data by Item ID")
               plt.xticks(rotation=45, ha="right")
               plt.tight_layout()
            # Display the graph
               plt.show()
            else:
            # Show a message if no sales data is available
                messagebox.showinfo("Sales", "No sales data available to display.")
        except Exception as e:
        # Handle exceptions and display error messages
            messagebox.showerror("Error", f"An error occurred: {e}")
# Set dark mode and theme
    ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
    ctk.set_default_color_theme("blue")  # Other themes: "green", "dark-blue"

# Initialize the main application window
    app = ctk.CTk()
    app.title("CR Jewellery")
    app.attributes('-fullscreen', True)  # Full-screen mode
    app.configure(fg_color="#1a1a2e")  # Background color
    app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
# Configure grid layout
    app.grid_columnconfigure((0, 1), weight=1)
    app.grid_rowconfigure(tuple(range(10)), weight=1)

# Title Label
    title_label = ctk.CTkLabel(
    app, 
    text="💎 CR JEWELLERY ",  # Diamond emoji on both sides
    font=("Segoe UI Emoji", 60, "bold"),  # Using emoji-compatible font
    text_color="#F1C40F"
)
    title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")

# Button Styling
    button_style = {
    "height": 70,
    "width": 350,
    "fg_color": "#0f3460",
    "hover_color": "#533483",
    "text_color": "white",
    "corner_radius": 20,
    "font": ("Arial", 40, "bold")  # Set text font, size, and style
}

# Button List
    buttons = [
        ("📊GENERATE REPORT", generate_report),
        ("➕ADD ITEM", add_item),
        ("✏️UPDATE ITEM", update_item),
        ("📦VIEW INVENTORY", view_inventory),
        ("👤UPDATE CUSTOMER", update_customer_record),
        ("📜VIEW CUSTOMER RECORDS", view_customer_records),
        ("💰RECORD SALE", record_sale),
        ("📈VIEW SALES", view_sales),
        ("🧾GENERATE BILL", generate_bill),
        ("🚪LOGOUT", logout),
    ]

# Place Buttons in a Grid Layout Properly
    row, col = 1, 0  # Start placing buttons from row 1
    for text, command in buttons:
       btn = ctk.CTkButton(app, text=text, command=command, **button_style)
       btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
    
    # Switch columns for each button
       col += 1
       if col > 1:  # When column reaches 2, reset to 0 and move to next row
          col = 0
          row += 1  # Move to the next row

# Run the application
    app.mainloop()


# Create and place buttons in grid
    row, col = 2, 0
    for text, command in buttons:
        btn = ctk.CTkButton(app, text=text, command=command, **button_style)
        btn.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
    
    col += 1
    if col > 1:
        col = 0
        row += 1

# Run the application
    app.mainloop()

# Function to check user login
def login_user(username, password):
    conn = sqlite3.connect("jewellery_shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Function to update the password in the database
def reset_password(username, new_password):
    conn = sqlite3.connect("jewellery_shop.db")
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False
# Forgot Password Window
def forgot_password():
    def update_password():
        username = entry_username.get()
        new_password = entry_new_password.get()

        if reset_password(username, new_password):
            speak("Password reset successfully. You can now log in with your new password.")
            messagebox.showinfo("Success", "Password updated successfully!")
            forgot_window.destroy()
        else:
            speak("Username not found. Please enter a valid username.")
            messagebox.showerror("Error", "Username not found!")

    forgot_window = ctk.CTkToplevel()  # Create a pop-up window
    forgot_window.title("Reset Password")
    forgot_window.geometry("400x200")

    ctk.CTkLabel(forgot_window, text="Enter Username:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_username = ctk.CTkEntry(forgot_window)
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(forgot_window, text="New Password:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_new_password = ctk.CTkEntry(forgot_window, show="*")
    entry_new_password.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkButton(forgot_window, text="Update Password", command=update_password).grid(row=2, column=0, columnspan=2, pady=10)

    forgot_window.mainloop()

# Login Interface
def login_interface():
    def attempt_login():
        username = entry_username.get()
        password = entry_password.get()

        if login_user(username, password):
            success_message = "Login successful! Welcome to CR Jeweller! Today is a great day!"
            speak(success_message)
            messagebox.showinfo("Success", success_message)
            login_window.destroy()
            main_interface()  # Open the main interface
        else:
            error_message = "Oops! Invalid username or password. But don't worry, try again!"
            speak(error_message)
            messagebox.showerror("Error", error_message)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    login_window = ctk.CTk()
    login_window.title("Admin Login")
    login_window.geometry("400x280")

    ctk.CTkLabel(login_window, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_username = ctk.CTkEntry(login_window)
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(login_window, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_password = ctk.CTkEntry(login_window, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkButton(login_window, text="Login", command=attempt_login).grid(row=2, column=0, columnspan=2, pady=10)

    # Forgot Password Button
    ctk.CTkButton(login_window, text="Forgot Password?", fg_color="gray", text_color="white", command=forgot_password).grid(row=3, column=0, columnspan=2, pady=10)

    speak("Welcome! Please enter your login details to access CR Jeweller.")

    login_window.mainloop()

# Register default admin user for testing
def register_default_admin():
    conn = sqlite3.connect("jewellery_shop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "12345"))
    conn.commit()
    conn.close()

register_default_admin()  # Ensure default admin exists

# Start the login interface
login_interface()