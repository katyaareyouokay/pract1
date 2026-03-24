import os
import tkinter as tk
from PIL import Image, ImageTk

from app.database import db
from app.services.product_service import ProductService
from app.ui.product_form import ProductForm
from app.ui.order_list import OrderList


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

IMAGES_DIR = os.path.join(BASE_DIR, "resources")

PLACEHOLDER = os.path.join(IMAGES_DIR, "picture.png")

FONT = ("Times New Roman", 10)
FONT_BOLD = ("Times New Roman", 11, "bold")


class ProductList:
    def __init__(self, root, user):
        self.user = user
        self.form_opened = False

        self.session = db.get_session()
        self.service = ProductService(self.session)

        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="none")
        self.supplier_var = tk.StringVar(value="Все поставщики")

        if self.is_staff():
            self.create_filters(root)

        self.setup_scroll(root)
        self.load_products()

    def setup_scroll(self, root):
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

    def is_staff(self):
        if not self.user:
            return False

        return self.user.role_id in (1, 2)

    def load_products(self):
        try:
            for widget in self.container.winfo_children():
                widget.destroy()

            products = self.apply_filters(self.service.get_all())

            for product in products:
                self.create_card(product)

        except Exception as error:
            print("Ошибка загрузки товаров:", error)

            tk.messagebox.showerror(
                "Ошибка",
                "Не удалось загрузить список товаров.\n"
                "Попробуйте перезапустить приложение."
            )

    def create_card(self, product):
        bg_color = self.get_bg(product)

        outer = tk.Frame(self.container, bg="black")
        outer.pack(fill=tk.X, padx=10, pady=5)

        frame = tk.Frame(outer, bg=bg_color)
        frame.pack(fill=tk.X, padx=2, pady=2)

        self.create_left(frame, product)
        self.create_center(frame, product)
        self.create_right(frame, product)

        if self.user and self.user.role_id == 1:
            frame.bind(
                "<Button-1>",
                lambda e, p=product: self.open_edit(p)
            )

    def create_left(self, frame, product):
        left_box = tk.Frame(frame, bg="black")
        left_box.pack(side=tk.LEFT, padx=10, pady=10)

        left = tk.Frame(left_box, bg="white", width=150, height=120)
        left.pack_propagate(False)
        left.pack(padx=1, pady=1)

        image_path = self.get_image_path(product)

        try:
            img = Image.open(image_path)

            img = img.resize((140, 100))

            img = ImageTk.PhotoImage(img)

        except Exception as error:
            print("Ошибка загрузки изображения:", error)

            img = Image.open(PLACEHOLDER)
            img = img.resize((140, 100))
            img = ImageTk.PhotoImage(img)

        label = tk.Label(left, image=img, bg="white")
        label.image = img
        label.pack(expand=True)

    def create_center(self, frame, product):
        center_box = tk.Frame(frame, bg="black")
        center_box.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        center = tk.Frame(center_box, bg="white")
        center.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        tk.Label(
            center,
            text=f"{product.category.name} | {product.name}",
            font=FONT_BOLD,
            bg="white"
        ).pack(anchor="w")

        tk.Label(
            center,
            text=f"Описание: {product.description or ''}",
            font=FONT,
            bg="white"
        ).pack(anchor="w")

        tk.Label(
            center,
            text=f"Производитель: {product.manufacturer.name}",
            font=FONT,
            bg="white"
        ).pack(anchor="w")

        tk.Label(
            center,
            text=f"Поставщик: {product.supplier.name}",
            font=FONT,
            bg="white"
        ).pack(anchor="w")

        self.create_price(center, product)

        tk.Label(
            center,
            text=f"Ед. изм.: {product.unit}",
            font=FONT,
            bg="white"
        ).pack(anchor="w")

        tk.Label(
            center,
            text=f"Количество: {product.stock_quantity}",
            font=FONT,
            bg="white"
        ).pack(anchor="w")

    def create_price(self, parent, product):
        price_frame = tk.Frame(parent, bg="white")
        price_frame.pack(anchor="w")

        price = float(product.price)

        if product.discount and product.discount > 0:
            new_price = price * (1 - product.discount / 100)

            tk.Label(
                price_frame,
                text=str(price),
                fg="red",
                font=("Times New Roman", 10, "overstrike"),
                bg="white"
            ).pack(side=tk.LEFT)

            tk.Label(
                price_frame,
                text=f" {round(new_price, 2)}",
                font=FONT,
                bg="white"
            ).pack(side=tk.LEFT)
        else:
            tk.Label(
                price_frame,
                text=str(price),
                font=FONT,
                bg="white"
            ).pack(anchor="w")

    def create_right(self, frame, product):
        right_box = tk.Frame(frame, bg="black")
        right_box.pack(side=tk.RIGHT, padx=10, pady=10)

        right = tk.Frame(right_box, bg="white", width=100, height=120)
        right.pack(padx=1, pady=1)

        tk.Label(
            right,
            text="Скидка",
            font=FONT,
            bg="white"
        ).pack()

        tk.Label(
            right,
            text=f"{product.discount}%",
            font=FONT_BOLD,
            bg="white"
        ).pack()

    # использование заглушки для фотографии товара
    def get_image_path(self, product):
        if product.photo:
            file_path = os.path.join(IMAGES_DIR, product.photo)

            if os.path.exists(file_path):
                return file_path

            print("Файл не найден:", file_path)

        return PLACEHOLDER

    def get_bg(self, product):
        if product.stock_quantity == 0:
            return "#87CEFA"
        if product.discount and product.discount > 15:
            return "#2E8B57"
        return "white"

    # блок фильтров
    def create_filters(self, root):
        frame = tk.Frame(root, bg="white")
        frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            frame,
            text="Поиск:",
            bg="white",
            font=FONT
        ).pack(side=tk.LEFT)

        search_entry = tk.Entry(
            frame,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace_add("write", self.update_products)

        tk.Label(
            frame,
            text="Сортировка:",
            bg="white",
            font=FONT
        ).pack(side=tk.LEFT, padx=10)

        sort_menu = tk.OptionMenu(
            frame,
            self.sort_var,
            "none",
            "asc",
            "desc",
            command=lambda _: self.update_products()
        )
        sort_menu.pack(side=tk.LEFT)

        tk.Label(
            frame,
            text="Поставщик:",
            bg="white",
            font=FONT
        ).pack(side=tk.LEFT, padx=10)

        suppliers = ["Все поставщики"] + self.get_suppliers()

        supplier_menu = tk.OptionMenu(
            frame,
            self.supplier_var,
            *suppliers,
            command=lambda _: self.update_products()
        )
        supplier_menu.pack(side=tk.LEFT)

        if self.user and self.user.role_id == 1:
            tk.Button(
                frame,
                text="Добавить товар",
                command=self.open_create,
                bg="#00FA9A"
            ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            frame,
            text="Заказы",
            command=self.open_orders,
            bg="#00FA9A"
        ).pack(side=tk.RIGHT, padx=5)

    # получение поставщиков
    def get_suppliers(self):
        products = self.service.get_all()
        names = {p.supplier.name for p in products}
        return sorted(names)

    def apply_filters(self, products):
        result = products

        # поиск по всем текстовым полям
        search = self.search_var.get().lower()

        if search:
            result = [
                p for p in result
                if search in (p.name or "").lower()
                or search in (p.description or "").lower()
                or search in (p.category.name or "").lower()
                or search in (p.manufacturer.name or "").lower()
                or search in (p.supplier.name or "").lower()
            ]

        # фильтр по поставщику
        supplier = self.supplier_var.get()

        if supplier != "Все поставщики":
            result = [
                p for p in result
                if p.supplier.name == supplier
            ]

        # сортировка
        sort = self.sort_var.get()

        if sort == "asc":
            result = sorted(result, key=lambda p: p.stock_quantity)

        elif sort == "desc":
            result = sorted(
                result,
                key=lambda p: p.stock_quantity,
                reverse=True
            )
        return result

    # форма для добавления/редактирования товара
    # защита от открытия нескольких окон
    def open_create(self):
        if hasattr(self, "editor_open") and self.editor_open:
            tk.messagebox.showwarning(
                "Предупреждение",
                "Уже открыто окно редактирования.\n"
                "Закройте его перед созданием нового товара."
            )
            return

        self.editor_open = True

        ProductForm(
            self.container,
            self.session,
            on_close=self.on_form_close
        )

    def on_form_close(self):
        self.editor_open = False
        self.load_products()

    def open_edit(self, product):
        if hasattr(self, "editor_open") and self.editor_open:
            tk.messagebox.showwarning(
                "Предупреждение",
                "Можно редактировать только один товар за раз."
            )
            return

        self.editor_open = True

        ProductForm(
            self.container,
            self.session,
            product=product,
            on_close=self.on_form_close
        )

    def update_products(self, *args):
        self.load_products()

    def open_orders(self):
        window = tk.Toplevel(self.container)
        window.title("Список заказов")
        OrderList(window, self.user)
