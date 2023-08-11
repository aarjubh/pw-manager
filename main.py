import random
import string
import sqlite3
import zxcvbn 
from tkinter import *
from tkinter import messagebox
class PasswordManager:
    def __init__(self, db_name):
        self.user_id = None
        self.username = None
        self.master_password = None
        self.db_name = db_name

        self.window = Tk()
        self.window.title("Password Manager")
        self.passwords = []
        self.create_main_ui()
        self.output_text_widget = None
    
    def execute_query(self, query, *params):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(query, params)  # Pass params as-is, no need to unpack or wrap in another tuple
            result = cursor.fetchall()

            conn.commit()
            conn.close()

            return result
        except sqlite3.Error as e:
            print("Error executing query:", e)
            return None

    def save_password(self, user_id, website, username, password_text):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO passwords (user_id, website, username, password) VALUES (?, ?, ?, ?)",
                        (user_id, website, username, password_text))

    def get_passwords(self):
        """Gets all of the passwords for the current user.

        Returns:
            list: A list of tuples containing the website, username, and password for each password.
        """

        query = "SELECT website, username, password FROM passwords WHERE user_id = ?"
        params = (self.user_id,)

        passwords = self.execute_query(query, params)

        if not passwords:
            # No passwords found
            return []

        # Sort passwords by website
        passwords.sort(key=lambda password: password[0])

        return passwords
    
    def run(self):
        self.window.mainloop()
        
    def open_search(self):
        # Create a new window for searching passwords
        search_window = Toplevel(self.window)
        search_window.title("Search Websites for Passwords")

        label_frame = LabelFrame(search_window, text="Enter the website to search")
        label_frame.pack(pady=20)

        website_entry_box = Entry(label_frame, width=50)
        website_entry_box.pack(padx=20, pady=10)

        self.output_text_widget = Text(search_window, wrap=WORD, width=50, height=5)
        self.output_text_widget.pack(pady=20)

        button_frame = Frame(search_window)
        button_frame.pack(pady=20)

        submit_btn = Button(button_frame, text="Submit", command=lambda: self.search_website_password(website_entry_box.get(), self.output_text_widget))
        submit_btn.pack()
        
    def search_website_password(self, website, output_text_widget):
        conn = sqlite3.connect("passwords.db")
        c = conn.cursor()

        c.execute("SELECT password FROM passwords WHERE website = ?", (website,))
        password = c.fetchone()

        conn.close()

        if password:
            output_text_widget.delete('1.0', END)
            output_text_widget.insert(INSERT, f"Password for {website}:\n{password[0]}")
        else:
            output_text_widget.delete('1.0', END)
            output_text_widget.insert(INSERT, f"No password found for {website}")

    def create_main_ui(self):
        self.window.geometry("1024x768")

        # Create a menu bar
        menu_bar = Menu(self.window)
        self.window.config(menu=menu_bar)

        # Create an "Exit" menu
        menu_bar.add_command(label="Exit", command=self.exit_application)

        # Create an "Help" menu
        menu_bar.add_command(label="Help", command=self.show_help)

        # Load and resize the main image
        self.main_image = PhotoImage(file="mainpic.png")
        self.main_image = self.main_image.subsample(2)  # Adjust the subsample value to resize the image

        # Create a frame for the main image
        image_frame = Frame(self.window)
        image_frame.pack(pady=20)

        # Use a Label to display the main image
        main_image_label = Label(image_frame, image=self.main_image)
        main_image_label.image = self.main_image  # Prevent image from being garbage collected
        main_image_label.pack()

        # Create a frame for the menu options
        menu_frame = Frame(self.window)
        menu_frame.pack(pady=20)

        # Create labels with colored boxes for each menu option
        menu_options = [
            ("Password Management", "#BEE6DC", self.open_password_management),
            ("Password Generation", "#B2B2CF", self.open_password_generation),
            ("Check Password Strength", "#CBA188", self.open_password_strength),
            ("Search", "#EFD6B1", self.open_search),
            ("View & Edit", "light gray", lambda: self.view_passwords())
            # Pass passwords data here
        ]

        row = 0
        col = 0
        for option, color, command in menu_options:
            label_frame = Frame(menu_frame, bg=color, highlightbackground="gray", highlightthickness=2)
            label_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

            label = Label(label_frame, text=option, font=("Helvetica", 14), bg=color)
            label.pack(padx=10, pady=10)
            label.bind("<Button-1>", lambda e, cmd=command: cmd())

            col += 1
            if col > 2:
                col = 0
                row += 1

        # Configure row and column weights to center-align the labels
        for i in range(row + 1):
            menu_frame.rowconfigure(i, weight=1)
        for i in range(3):
            menu_frame.columnconfigure(i, weight=1)

    def exit_application(self):
        self.window.destroy()

    def show_help(self):
        messagebox.showinfo("Help", "This is a simple password manager application.\n\nYou can use the various menu options to manage your passwords.")

    def open_password_management(self):
        # Function to handle password management
        password_management_window = Toplevel(self.window)
        password_management_window.title("Password Management")

        # Create input fields
        Label(password_management_window, text="Website:").grid(row=0, column=0, padx=10, pady=10)
        website_entry = Entry(password_management_window)
        website_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(password_management_window, text="Username:").grid(row=1, column=0, padx=10, pady=10)
        username_entry = Entry(password_management_window)
        username_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(password_management_window, text="Password:").grid(row=2, column=0, padx=10, pady=10)
        password_entry = Entry(password_management_window, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=10)

        def save_password():
            website = website_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            
            if self.user_id is not None:
                # Call the save_password method from the current instance
                self.save_password(self.user_id, website, username, password)
                messagebox.showinfo("Success", "Password saved successfully!")
                password_management_window.destroy()
            else:
                messagebox.showerror("Error", "User ID not found.")
            
        # Create a "Submit" button
        submit_button = Button(password_management_window, text="Submit", command=save_password)
        submit_button.grid(row=3, columnspan=2, padx=10, pady=10)

            
    def open_password_generation(self):
        # Create a new window for password generation
        password_gen_window = Toplevel(self.window)
        password_gen_window.title("Password Generation")

        # Create a label frame for password generation options
        label_frame = LabelFrame(password_gen_window, text="Enter the number of characters")
        label_frame.pack(pady=20)

        # Entry box for number of characters
        length_entry_box = Entry(label_frame, width=20)
        length_entry_box.pack(padx=20, pady=20)

        # Feedback label
        self.feedback = Label(password_gen_window, fg="red")
        self.feedback.pack()

        # Entry box for password
        self.password_entry_box = Entry(password_gen_window, text="", width=50)
        self.password_entry_box.pack(pady=20)

        # Frame for buttons
        button_frame = Frame(password_gen_window)
        button_frame.pack(pady=20)

        # Generate Password Button
        generate_btn = Button(button_frame, text="Generate Password", command=lambda: self.generate_password(length_entry_box.get()))
        generate_btn.grid(row=0, column=0, padx=10)

    def generate_password(self, length):
        try:
            length = int(length)
            if length < 8:
                self.feedback.config(text="Invalid length")
                return

            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(characters) for _ in range(length))
            self.password_entry_box.delete(0, END)
            self.password_entry_box.insert(0, password)
            self.feedback.config(text="")
        except ValueError:
            self.feedback.config(text="Please enter a valid number")


    def open_password_strength(self):
        # Function to handle password strength checking
        password_strength_window = Toplevel(self.window)
        password_strength_window.title("Check Password Strength")

        label_frame = LabelFrame(
            password_strength_window, text="Enter the password to check strength")
        label_frame.pack(pady=20)

        password_entry_box = Entry(label_frame, width=50)
        password_entry_box.pack(padx=20, pady=10)

        self.output_text_widget = Text(password_strength_window, wrap=WORD, width=50, height=5)
        self.output_text_widget.pack(pady=20)

        button_frame = Frame(password_strength_window)
        button_frame.pack(pady=20)

        check_btn = Button(button_frame, text="Check", command=lambda: self.check_password_strength(password_entry_box.get(), self.output_text_widget))
        check_btn.grid(row=0, column=0, padx=10)

        self.output_text_widget.delete('1.0', END)
        strength_text = ""
        feedback = ""
        self.output_text_widget.insert(INSERT, f"Strength: {strength_text}\nFeedback:\n{feedback}")
        self.output_text_widget.config(height=5)

    def check_password_strength(self, password, output_text_widget):
        result = zxcvbn.zxcvbn(password)  # Use the zxcvbn library to check password strength
        strength = result['score']

        if strength == 0:
            strength_text = "Very Weak"
        elif strength == 1:
            strength_text = "Weak"
        elif strength == 2:
            strength_text = "Moderate"
        elif strength == 3:
            strength_text = "Strong"
        else:
            strength_text = "Very Strong"

        feedback = result['feedback']['suggestions']
        if not feedback:
            feedback = result['feedback']['warning']
        else:
            feedback = "\n".join(feedback)

        output_text_widget.delete('1.0', END)
        output_text_widget.insert(INSERT, f"Strength: {strength_text}\nFeedback:\n{feedback}")


    def search_website_password(self, website, output_text_widget):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute("SELECT password FROM passwords WHERE website = ?", (website,))
        password = c.fetchone()

        conn.close()

        if password:
            output_text_widget.delete('1.0', END)
            output_text_widget.insert(INSERT, f"Password for {website}:\n{password[0]}")
        else:
            output_text_widget.delete('1.0', END)
            output_text_widget.insert(INSERT, f"No password found for {website}")

    def view_passwords(self):
        self.view_passwords_window = Toplevel(self.window)
        self.view_passwords_window.title("View Passwords")

        passwords = self.get_passwords()

        for password in passwords:
            website, username, password_text = password

            password_frame = Frame(self.view_passwords_window, bg="#CFE8ED")
            password_frame.pack(pady=10)

            password_text_widget = Text(password_frame, wrap=WORD, width=50, height=4)
            password_text_widget.insert(INSERT, f"Website: {website}\nUsername: {username}\nPassword: {password_text}\n")
            password_text_widget.config(state=DISABLED)  # Disable text editing


            edit_btn = Button(password_frame, text="Edit", command=lambda pw_widget=password_text_widget, web=website, user=username: self.edit_password(pw_widget, website, username, password_frame))
            edit_btn.pack(side="left")

            delete_btn = Button(password_frame, text="Delete", command=lambda web=website, user=username: self.delete_password(website, username, password_frame))
            delete_btn.pack(side="right")

    def edit_password(self, password_text_widget, website, username, password_frame):
        password_text_widget.config(state=NORMAL)  # Enable text editing
        save_button = Button(password_frame, text="Save", command=lambda: self.save_edited_password(password_text_widget, website, username, password_frame))
        save_button.pack()

    def save_edited_password(self, password_text_widget, website, username, password_frame):
        new_password = password_text_widget.get("1.0", END).strip()
        self.update_password(website, username, new_password)  # Call the update_password method
        messagebox.showinfo("Success", "Password updated successfully!")
        password_text_widget.config(state=DISABLED)  # Disable text editing
        password_frame.destroy()


    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        user = self.execute_query(query, user_id)  # No need to wrap user_id in a tuple
        return user
    
    def update_password(self, website, username, new_password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("UPDATE passwords SET password = ? WHERE user_id = ? AND website = ? AND username = ?",
                    (new_password, self.user_id, website, username))

        conn.commit()
        conn.close()

    def open_main_app(user_id):
        user = password_manager.get_user_by_id(user_id)
        if user:
            password_manager.user_id = user_id  # Updates the user_id
            password_manager.window.destroy()   # Closes the current window
            password_manager.create_main_ui()

if __name__ == "__main__":
    db_name = "passwords.db"  # Provide the actual database name
    password_manager = PasswordManager(db_name)
    password_manager.run()
    
    desired_user_id = 1  # For example
    user = password_manager.get_user_by_id(desired_user_id)
    if user:
        password_manager.user_id = desired_user_id
        password_manager.open_main_app()
    else:
        print("User not found")
