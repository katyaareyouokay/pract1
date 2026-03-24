import os
import tkinter as tk

from app.ui.product_list import ProductList


FONT = ("Times New Roman", 11, "bold")


class MainWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user

        self.root.title("Список товаров")

        self.base_dir = self.get_base_dir()

        self.set_icon()
        self.create_header()

        ProductList(root, self.user)

    def get_base_dir(self):
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )

    def set_icon(self):
        try:
            icon_path = os.path.join(
                self.base_dir,
                "resources",
                "icon.png"
            )

            icon = tk.PhotoImage(file=icon_path)

            self.root.iconphoto(True, icon)
            self.root.icon = icon

        except Exception as error:
            print("Ошибка иконки:", error)

    def create_header(self):
        header = tk.Frame(self.root, bg="#7FFF00")
        header.pack(fill=tk.X)

        self.add_logo(header)

        tk.Button(
            header,
            text="Выйти",
            command=self.logout,
            bg="#00FA9A"
        ).pack(side=tk.LEFT, padx=10, pady=5)

        self.user_label = tk.Label(
            header,
            font=FONT,
            bg="#7FFF00"
        )
        self.user_label.pack(side=tk.RIGHT, padx=10)

        self.set_user_info()

    def add_logo(self, parent):
        try:
            logo_path = os.path.join(
                self.base_dir,
                "resources",
                "icon.png"
            )

            img = tk.PhotoImage(file=logo_path)

            # уменьшаем (сохраняет пропорции)
            img = img.subsample(4, 4)

            label = tk.Label(parent, image=img, bg="#7FFF00")
            label.image = img
            label.pack(side=tk.LEFT, padx=10, pady=5)

        except Exception as error:
            print("Ошибка логотипа:", error)

    def set_user_info(self):
        if self.user:
            fio = self.user.full_name
        else:
            fio = "Гость"

        self.user_label.config(text=fio)

    def logout(self):
        self.root.destroy()

        from app.ui.login_window import LoginWindow

        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()
