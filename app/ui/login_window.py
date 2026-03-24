import tkinter as tk
from tkinter import messagebox

from app.database import db
from app.services.auth_service import AuthService


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация")

        self.session = db.get_session()
        self.auth_service = AuthService(self.session)

        tk.Label(root, text="Логин").pack()
        self.login_entry = tk.Entry(root)
        self.login_entry.pack()

        tk.Label(root, text="Пароль").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Войти",
                  command=self.login).pack()

        tk.Button(root, text="Гость",
                  command=self.login_as_guest).pack()

    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        user = self.auth_service.authenticate(login, password)

        if not user:
            messagebox.showerror("Ошибка", "Неверные данные")
            return

        self.open_main(user)

    def login_as_guest(self):
        self.open_main(None)

    def open_main(self, user):
        self.root.destroy()

        from app.ui.main_window import MainWindow

        root = tk.Tk()
        MainWindow(root, user)
        root.mainloop()
