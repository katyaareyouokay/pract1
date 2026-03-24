import tkinter as tk

from app.database import db
from app.models import Order
from app.ui.order_form import OrderForm


FONT = ("Times New Roman", 10)
FONT_BOLD = ("Times New Roman", 11, "bold")


class OrderList:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.session = db.get_session()
        self.editor_open = False

        canvas = tk.Canvas(root, bg="white")

        scrollbar = tk.Scrollbar(
            root,
            orient="vertical",
            command=canvas.yview
        )

        self.container = tk.Frame(canvas, bg="white")

        self.container.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=self.container,
            anchor="nw"
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if self.is_admin():
            tk.Button(
                root,
                text="Добавить заказ",
                command=self.open_create,
                bg="#00FA9A"
            ).pack(pady=5)

        self.load_orders()

        tk.Button(
            root,
            text="Назад",
            command=self.go_back,
            bg="#00FA9A"
        ).pack(pady=5)

    def is_admin(self):
        return self.user and self.user.role_id == 1

    def load_orders(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        orders = self.session.query(Order).all()

        for order in orders:
            self.create_card(order)

    def create_card(self, order):
        outer = tk.Frame(self.container, bg="black")
        outer.pack(fill=tk.X, padx=10, pady=5)

        frame = tk.Frame(outer, bg="white")
        frame.pack(fill=tk.X, padx=2, pady=2)

        # левая часть с информацией по заказу
        left = tk.Frame(
            frame,
            bg="white",
            highlightbackground="black",
            highlightthickness=1
        )
        left.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        items_text = ", ".join(
            f"{i.product_article}, {i.quantity}"
            for i in order.items
        )

        tk.Label(
            left,
            text=f"Артикулы: {items_text}",
            font=FONT
        ).pack(anchor="w")

        tk.Label(
            left,
            text=f"Статус: {order.status.name}",
            font=FONT
        ).pack(anchor="w")

        tk.Label(
            left,
            text=f"Пункт выдачи: {order.pickup_point.address}",
            font=FONT
        ).pack(anchor="w")

        tk.Label(
            left,
            text=f"Дата заказа: {order.order_date}",
            font=FONT
        ).pack(anchor="w")

        # правая часть с датой доставки
        right = tk.Frame(
            frame,
            bg="white",
            width=150,
            highlightbackground="black",
            highlightthickness=1
        )
        right.pack(
            side=tk.RIGHT,
            padx=10,
            pady=10
        )

        tk.Label(
            right,
            text="Дата доставки",
            font=FONT
        ).pack()

        tk.Label(
            right,
            text=str(order.delivery_date),
            font=FONT_BOLD
        ).pack()

        # клик для админа
        if self.is_admin():
            frame.bind(
                "<Button-1>",
                lambda e, o=order: self.open_edit(o)
            )

    # CRUD
    def open_create(self):
        if self.editor_open:
            return

        self.editor_open = True

        OrderForm(
            self.root,
            self.session,
            on_close=self.on_close
        )

    def open_edit(self, order):
        if self.editor_open:
            return

        self.editor_open = True

        OrderForm(
            self.root,
            self.session,
            order=order,
            on_close=self.on_close
        )

    def on_close(self):
        self.editor_open = False
        self.load_orders()

    def go_back(self):
        self.root.destroy()
