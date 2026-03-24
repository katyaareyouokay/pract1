import os
import tkinter as tk
from tkinter import messagebox, filedialog
import random
import string

from PIL import Image

from app.models import Category, Manufacturer, Supplier, Product


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

IMAGES_DIR = os.path.join(BASE_DIR, "resources")
PLACEHOLDER = os.path.join(IMAGES_DIR, "picture.png")


class ProductForm:
    def __init__(self, parent, session, product=None, on_close=None):
        self.session = session
        self.product = product
        self.on_close = on_close
        self.old_image_path = None

        self.window = tk.Toplevel(parent)
        self.window.title(
            "Редактирование товара"
            if product else "Добавление товара"
        )

        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.image_path = None

        self.create_fields()

        if product:
            self.fill_data()

    def create_fields(self):
        self.entries = {}

        fields = [
            "name",
            "description",
            "price",
            "unit",
            "stock_quantity",
            "discount"
        ]

        for field in fields:
            frame = tk.Frame(self.window)
            frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(frame, text=field).pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

            self.entries[field] = entry

        # категории
        self.category_var = tk.StringVar()
        self.category_menu = tk.OptionMenu(
            self.window,
            self.category_var,
            *self.get_categories()
        )
        self.category_menu.pack(fill=tk.X, padx=10, pady=5)

        # производители
        self.manufacturer_var = tk.StringVar()
        self.manufacturer_menu = tk.OptionMenu(
            self.window,
            self.manufacturer_var,
            *self.get_manufacturers()
        )
        self.manufacturer_menu.pack(fill=tk.X, padx=10, pady=5)

        # поставщики
        self.supplier_var = tk.StringVar()
        self.supplier_menu = tk.OptionMenu(
            self.window,
            self.supplier_var,
            *self.get_suppliers()
        )
        self.supplier_menu.pack(fill=tk.X, padx=10, pady=5)

        # фото
        tk.Button(
            self.window,
            text="Выбрать фото",
            command=self.choose_image
        ).pack(pady=5)

        tk.Button(
            self.window,
            text="Сохранить",
            command=self.save
        ).pack(pady=5)

        if self.product:
            tk.Button(
                self.window,
                text="Удалить",
                command=self.delete
            ).pack(pady=5)

        tk.Button(
            self.window,
            text="Назад",
            command=self.close,
            bg="#00FA9A"
        ).pack(pady=5)

    # данные товара
    def get_categories(self):
        return [c.name for c in self.session.query(Category).all()]

    def get_manufacturers(self):
        return [m.name for m in self.session.query(Manufacturer).all()]

    def get_suppliers(self):
        return [s.name for s in self.session.query(Supplier).all()]

    def fill_data(self):
        self.entries["name"].insert(0, self.product.name)
        self.entries["description"].insert(0, self.product.description or "")
        self.entries["price"].insert(0, str(self.product.price))
        self.entries["unit"].insert(0, self.product.unit)
        self.entries["stock_quantity"].insert(
            0, str(self.product.stock_quantity)
        )
        self.entries["discount"].insert(
            0, str(self.product.discount)
        )

        self.category_var.set(self.product.category.name)
        self.manufacturer_var.set(self.product.manufacturer.name)
        self.supplier_var.set(self.product.supplier.name)

        if self.product.photo:
            self.image_path = os.path.join(
                IMAGES_DIR,
                self.product.photo
            )
        if self.product.photo:
            self.image_path = os.path.join(
                IMAGES_DIR,
                self.product.photo
            )

            # сохранение пути к старому фото для удаления
            self.old_image_path = self.image_path

    def choose_image(self):
        file_path = filedialog.askopenfilename()

        if not file_path:
            return

        try:
            img = Image.open(file_path)
            img = img.resize((300, 200))

            # защита от перезаписывания
            number = random.randint(10, 99)
            filename = f"{number}_{os.path.basename(file_path)}"
            save_path = os.path.join(IMAGES_DIR, filename)

            # удаление старого фото при редактировании
            if self.product and self.old_image_path:
                if os.path.exists(self.old_image_path):
                    try:
                        os.remove(self.old_image_path)
                    except Exception as error:
                        print("Ошибка удаления старого фото:", error)

            img.save(save_path)

            self.image_path = save_path

        except Exception as error:
            print("Ошибка загрузки изображения:", error)

            messagebox.showerror(
                "Ошибка",
                "Не удалось загрузить изображение.\n"
                "Проверьте формат файла."
            )

    # генерация уникального артикула
    def generate_article(self):
        while True:
            part1 = ''.join(random.choices(string.ascii_uppercase, k=1))
            part2 = ''.join(random.choices(string.digits, k=3))
            part3 = ''.join(random.choices(string.ascii_uppercase, k=1))
            part4 = ''.join(random.choices(string.digits, k=1))

            article = f"{part1}{part2}{part3}{part4}"

            exists = self.session.query(Product).filter_by(
                article=article
            ).first()

            if not exists:
                return article

    def save(self):
        try:
            price_str = self.entries["price"].get()
            unit = self.entries["unit"].get()
            quantity_str = self.entries["stock_quantity"].get()
            discount_str = self.entries["discount"].get() or "0"

            # валидация price
            if "." in price_str:
                decimal_part = price_str.split(".")[1]
                if len(decimal_part) not in (1, 2):
                    raise ValueError("price_format")

            price = float(price_str)

            if price < 0:
                raise ValueError("price_negative")

            # валидация unit
            if unit != "шт.":
                raise ValueError("unit_invalid")

            # валидация quantity
            quantity = int(quantity_str)

            if quantity < 0:
                raise ValueError("quantity_negative")

            # валидация discount
            discount = int(discount_str)

            if discount < 0 or discount > 100:
                raise ValueError("discount_invalid")

        except ValueError as error:
            error_type = str(error)

            if error_type == "price_format":
                messagebox.showerror(
                    "Ошибка",
                    "Цена должна содержать 1 или 2 знака после точки.\n"
                    "Пример: 10.5 или 10.55"
                )

            elif error_type == "price_negative":
                messagebox.showerror(
                    "Ошибка",
                    "Цена не может быть отрицательной."
                )

            elif error_type == "unit_invalid":
                messagebox.showerror(
                    "Ошибка",
                    "Единица измерения должна быть строго 'шт.'"
                )

            elif error_type == "quantity_negative":
                messagebox.showerror(
                    "Ошибка",
                    "Количество не может быть отрицательным."
                )

            elif error_type == "discount_invalid":
                messagebox.showerror(
                    "Ошибка",
                    "Скидка должна быть от 0 до 100."
                )

            else:
                messagebox.showerror(
                    "Ошибка",
                    "Проверьте корректность введенных данных."
                )

            return

        if not self.product:
            product = Product()
            product.article = self.generate_article()
        else:
            product = self.product
        product.name = self.entries["name"].get()
        product.description = self.entries["description"].get()
        product.price = price
        product.unit = self.entries["unit"].get()
        product.stock_quantity = quantity
        product.discount = discount

        product.category = self.session.query(Category).filter_by(
            name=self.category_var.get()
        ).first()

        product.manufacturer = self.session.query(Manufacturer).filter_by(
            name=self.manufacturer_var.get()
        ).first()

        product.supplier = self.session.query(Supplier).filter_by(
            name=self.supplier_var.get()
        ).first()

        if self.image_path:
            product.photo = os.path.basename(self.image_path)

        self.session.add(product)
        self.session.commit()

        messagebox.showinfo("Успех", "Сохранено")

        self.close()

    def delete(self):
        if self.product.order_items:
            messagebox.showerror(
                "Ошибка",
                "Нельзя удалить товар, он есть в заказах"
            )
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            "Удалить товар?"
        )

        if not confirm:
            return

        self.session.delete(self.product)
        self.session.commit()

        messagebox.showinfo("Удалено", "Товар удалён")

        self.close()

    def close(self):
        if self.on_close:
            self.on_close()

        self.window.destroy()
