from tkinter import *
from functools import partial
import sqlite3
import subprocess

class LoginPage:
    
    def __init__(self):
        self.window = Tk()
        self.window.title("Password Manager")
        
        # Load and resize the login image
        self.login_image = PhotoImage(file="login.png") 
        self.login_image = self.login_image.subsample(3)  
        
        # Initialize the user interface
        self.create_login_ui()
    
    def open_main_app(self, user_id):
        subprocess.Popen(["python", "main.py", str(user_id)])  # Pass the user ID to the main page using subprocess

    
    def create_login_ui(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        self.window.geometry("450x500")

        # Use a Label to display the image
        login_image_label = Label(self.window, image=self.login_image)
        login_image_label.pack(pady=10)

        login_frame = Frame(self.window, bg="#CFE8ED")
        login_frame.pack(pady=20)

        label1 = Label(login_frame, text="Enter your master password")
        label1.config(anchor=CENTER)
        label1.pack(pady=10)

        self.password_entry_box = Entry(login_frame, width=20, show="*")
        self.password_entry_box.pack()

        label2 = Label(login_frame, text="Enter your username")
        label2.config(anchor=CENTER)
        label2.pack(pady=10)

        self.username_entry_box = Entry(login_frame, width=20)
        self.username_entry_box.pack()

        self.feedback = Label(self.window, text="", fg="red", bg="#CFE8ED")
        self.feedback.pack(pady=5)

        login_btn = Button(self.window, text="Log In", command=self.check_master_password)
        login_btn.pack(pady=10)

        create_mp_btn = Button(self.window, text="Create Master Password", command=self.create_master_password)
        create_mp_btn.pack(pady=10)
    
    def create_master_password(self):
        new_user_window = Toplevel(self.window)
        new_user_window.title("Create New Master Password")
        new_user_window.geometry("450x250")

        label1 = Label(new_user_window, text="Create New Master Password")
        label1.config(anchor=CENTER)
        label1.pack(pady=10)

        mp_entry_box = Entry(new_user_window, width=20, show="*")
        mp_entry_box.pack()
        mp_entry_box.focus()

        label2 = Label(new_user_window, text="Enter the password again")
        label2.config(anchor=CENTER)
        label2.pack(pady=10)

        rmp_entry_box = Entry(new_user_window, width=20, show="*")
        rmp_entry_box.pack()

        label3 = Label(new_user_window, text="Enter your username")
        label3.config(anchor=CENTER)
        label3.pack(pady=10)

        username_entry_box = Entry(new_user_window, width=20)
        username_entry_box.pack()

        feedback = Label(new_user_window, text="")
        feedback.pack()
        
        save_btn = Button(new_user_window, text="Create Password",
                        command=partial(self.save_master_password, mp_entry_box, rmp_entry_box, username_entry_box, feedback))
        save_btn.pack(pady=5)
        
        # Create a button to close the window
        close_btn = Button(new_user_window, text="Close", command=new_user_window.destroy)
        close_btn.pack(pady=5)

    def save_master_password(self, mp_entry_box, rmp_entry_box, username_entry_box, feedback):
        master_password = mp_entry_box.get()
        repeat_password = rmp_entry_box.get()
        username = username_entry_box.get()

        if master_password == repeat_password:
            conn, cursor = self.init_database()

            cursor.execute("INSERT INTO users (username, master_password) VALUES (?, ?)", (username, master_password))
            conn.commit()
            conn.close()

            feedback.config(text="Master Password created successfully.")
        else:
            feedback.config(text="Passwords do not match. Please try again.")

    '''def check_master_password(self):
        entered_username = self.username_entry_box.get()
        entered_password = self.password_entry_box.get()

        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (entered_username,))
        user = cursor.fetchone()

        conn.close()

        if user and user[2] == entered_password:
            self.open_main_app(user[0])  # Pass only the user id
        else:
            self.feedback.config(text="Incorrect username or password", fg="red")'''
    
    '''def check_master_password(self):
        entered_username = self.username_entry_box.get()
        entered_password = self.password_entry_box.get()

        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (entered_username,))
        user = cursor.fetchone()

        conn.close()

        if user and user[2] == entered_password:
            self.open_main_app()  # No need to pass the user id
        else:
            self.feedback.config(text="Incorrect username or password", fg="red")

    def open_main_app(self):
        subprocess.Popen(["python", "main.py"])  # Open the main page using subprocess

    def open_main_app(self):
        subprocess.Popen(["python", "main.py"])  # Open the main page using subprocess'''
        

    def check_master_password(self):
        entered_username = self.username_entry_box.get()
        entered_password = self.password_entry_box.get()

        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (entered_username,))
        user = cursor.fetchone()

        conn.close()

        if user and user[2] == entered_password:
            self.window.destroy()  # Close the login page
            subprocess.Popen(["python", "main.py"])  # Open the main page using subprocess
        else:
            self.feedback.config(text="Incorrect username or password", fg="red")

    def open_main_app(self):
        pass  # No need to define this function anymore

    
    def init_database(self):
        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()
        return conn, cursor
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = LoginPage()
    app.run()
