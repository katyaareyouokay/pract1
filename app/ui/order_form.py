import tkinter as tk
from tkinter import messagebox

from app.models import (
    Order,
    PickupPoint,
    OrderStatus,
    Product,
    OrderItem,
    User
)


class OrderForm:
    def __init__(self, parent, session, order=None, on_close=None):
        self.session = session
        self.order = order
        self.on_close = on_close

        self.window = tk.Toplevel(parent)
        self.window.title(
            "Редактирование заказа" if order else "Добавление заказа"
        )

        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.entries = {}

        self.create_fields()

        if order:
            self.fill_data()

    def create_fields(self):
        fields = ["order_number", "order_date", "delivery_date"]

        for field in fields:
            frame = tk.Frame(self.window)
            frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(frame, text=field).pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

            self.entries[field] = entry

        # товары
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame, text="Товары (артикул, кол-во)").pack(side=tk.LEFT)

        entry = tk.Entry(frame)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.entries["items"] = entry

        # статус
        self.status_var = tk.StringVar()
        tk.OptionMenu(
            self.window,
            self.status_var,
            *self.get_statuses()
        ).pack(fill=tk.X, padx=10, pady=5)

        # пункт выдачи
        self.pickup_var = tk.StringVar()
        tk.OptionMenu(
            self.window,
            self.pickup_var,
            *self.get_pickups()
        ).pack(fill=tk.X, padx=10, pady=5)

        # пользователь
        self.user_var = tk.StringVar()
        tk.OptionMenu(
            self.window,
            self.user_var,
            *self.get_users()
        ).pack(fill=tk.X, padx=10, pady=5)

        # код получения
        frame_code = tk.Frame(self.window)
        frame_code.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_code, text="pickup_code").pack(side=tk.LEFT)

        self.pickup_code_entry = tk.Entry(frame_code)
        self.pickup_code_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Button(
            self.window,
            text="Сохранить",
            command=self.save
        ).pack(pady=5)

        if self.order:
            tk.Button(
                self.window,
                text="Удалить",
                command=self.delete
            ).pack(pady=5)

        tk.Button(
            self.window,
            text="Назад",
            command=self.close
        ).pack(pady=5)

    def get_statuses(self):
        return [s.name for s in self.session.query(OrderStatus).all()]

    def get_pickups(self):
        return [p.address for p in self.session.query(PickupPoint).all()]

    def get_users(self):
        users = self.session.query(User).where(User.role_id == 3).all()
        return [str(u.id) for u in users]

    def fill_data(self):
        self.entries["order_number"].insert(0, self.order.order_number)
        self.entries["order_date"].insert(0, self.order.order_date)
        self.entries["delivery_date"].insert(0, self.order.delivery_date)
        self.user_var.set(str(self.order.user.id))
        self.pickup_code_entry.insert(0, self.order.pickup_code)
        self.status_var.set(self.order.status.name)
        self.pickup_var.set(self.order.pickup_point.address)

        # заполнение товаров
        items_text = ", ".join(
            f"{i.product_article}, {i.quantity}"
            for i in self.order.items
        )
        self.entries["items"].insert(0, items_text)

    def save(self):
        try:
            number = int(self.entries["order_number"].get())

            if not self.pickup_code_entry.get():
                raise ValueError("pickup_code")

            if not self.user_var.get():
                raise ValueError("user")

            if not self.pickup_var.get():
                raise ValueError("pickup")

            if not self.status_var.get():
                raise ValueError("status")

            items_raw = self.entries["items"].get()

            if not items_raw:
                raise ValueError("items")

            # парсинг товаров
            parts = [x.strip() for x in items_raw.split(",")]

            if len(parts) % 2 != 0:
                raise ValueError("items_format")

            items = []

            for i in range(0, len(parts), 2):
                article = parts[i]
                quantity = int(parts[i + 1])

                product = self.session.query(Product).filter_by(
                    article=article
                ).first()

                if not product:
                    raise ValueError("article")

                items.append((article, quantity))

        except ValueError as error:
            if str(error) == "pickup_code":
                messagebox.showerror(
                    "Ошибка",
                    "Введите код получения"
                )
            elif str(error) == "user":
                messagebox.showerror(
                    "Ошибка",
                    "Выберите пользователя"
                )

            elif str(error) == "pickup":
                messagebox.showerror(
                    "Ошибка",
                    "Выберите пункт выдачи"
                )

            elif str(error) == "status":
                messagebox.showerror(
                    "Ошибка",
                    "Выберите статус заказа"
                )
            elif str(error) == "items":
                messagebox.showerror(
                    "Ошибка",
                    "Введите товары"
                )
            elif str(error) == "items_format":
                messagebox.showerror(
                    "Ошибка",
                    "Неверный формат товаров\n"
                    "Пример: A123B1, 2, C456D2, 1"
                )
            elif str(error) == "article":
                messagebox.showerror(
                    "Ошибка",
                    "Один из артикулов не найден"
                )
            else:
                messagebox.showerror(
                    "Ошибка",
                    "Номер заказа должен быть числом"
                )
            return

        except Exception:
            messagebox.showerror("Ошибка", "Некорректные данные")
            return

        try:
            if not self.order:
                order = Order()
            else:
                order = self.order
                order.items.clear()

            order.order_number = number
            order.order_date = self.entries["order_date"].get()
            order.delivery_date = self.entries["delivery_date"].get()

            order.status = self.session.query(OrderStatus).filter_by(
                name=self.status_var.get()
            ).first()

            order.pickup_point = self.session.query(PickupPoint).filter_by(
                address=self.pickup_var.get()
            ).first()

            order.user = self.session.query(User).filter_by(
                id=int(self.user_var.get())
            ).first()

            order.pickup_code = self.pickup_code_entry.get()

            # добавление товаров
            for article, quantity in items:
                item = OrderItem(
                    product_article=article,
                    quantity=quantity
                )
                order.items.append(item)

            self.session.add(order)
            self.session.commit()

            messagebox.showinfo("Успех", "Сохранено")
            self.close()

        except Exception as error:
            self.session.rollback()

            messagebox.showerror(
                "Ошибка",
                f"Ошибка сохранения:\n{error}"
            )

    def delete(self):
        confirm = messagebox.askyesno(
            "Подтверждение",
            "Удалить заказ?"
        )

        if not confirm:
            return

        self.session.delete(self.order)
        self.session.commit()

        messagebox.showinfo("Удалено", "Заказ удалён")

        self.close()

    def close(self):
        if self.on_close:
            self.on_close()

        self.window.destroy()
