import os
import sys
import pandas as pd
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import select
from app.database import db
from app.models import (
    Role, Supplier, Manufacturer, Category,
    PickupPoint, OrderStatus, User, Product, Order, OrderItem
)

# корень проекта pract1
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)


def debug_log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def safe_str(value):
    if pd.isna(value):
        return None
    return str(value).strip()


def safe_int(value):
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def safe_float(value):
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# чтение CSV с разделителем ';' и кодировкой utf-8
def read_csv(file_path):
    debug_log(f"Чтение {os.path.basename(file_path)}")
    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    df.columns = df.columns.str.strip()
    debug_log(f"Колонки: {list(df.columns)}")
    return df


@contextmanager
def session_scope():
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# загрузка справочников
def load_roles():
    roles = ['Администратор', 'Менеджер', 'Авторизированный клиент']
    with session_scope() as session:
        for name in roles:
            existing_role = session.execute(
                            select(Role).where(Role.name == name)
                            ).scalar_one_or_none()
            if not existing_role:
                session.add(Role(name=name))
    debug_log("Роли загружены")


def load_order_statuses():
    statuses = ['Новый', 'Завершен']
    with session_scope() as session:
        for name in statuses:
            existing_statuses = session.execute(
                select(OrderStatus).where(OrderStatus.name == name)
                ).scalar_one_or_none()
            if not existing_statuses:
                session.add(OrderStatus(name=name))
    debug_log("Статусы заказов загружены")


def load_pickup_points(csv_path):
    df = read_csv(csv_path)
    col = 'Адрес'
    if not col:
        debug_log("Не найдена колонка с адресом")
        return
    addresses = df[col].dropna().unique()
    with session_scope() as session:
        for addr in addresses:
            addr = safe_str(addr)
            if addr:
                existing = session.execute(
                    select(PickupPoint).where(PickupPoint.address == addr)
                ).scalar_one_or_none()
                if not existing:
                    session.add(PickupPoint(address=addr))
    debug_log(f"Пункты выдачи загружены ({len(addresses)})")


def load_suppliers(csv_path):
    df = read_csv(csv_path)
    col = 'Поставщик'
    if not col:
        debug_log("Не найдена колонка с поставщиками")
        return
    names = df[col].dropna().unique()
    with session_scope() as session:
        for name in names:
            name = safe_str(name)
            if name:
                existing = session.execute(
                    select(Supplier).where(Supplier.name == name)
                ).scalar_one_or_none()
                if not existing:
                    session.add(Supplier(name=name))
    debug_log(f"Поставщики загружены ({len(names)})")


def load_manufacturers(csv_path):
    df = read_csv(csv_path)
    col = 'Производитель'
    if not col:
        debug_log("Не найдена колонка с производителями")
        return
    names = df[col].dropna().unique()
    with session_scope() as session:
        for name in names:
            name = safe_str(name)
            if name:
                existing = session.execute(
                    select(Manufacturer).where(Manufacturer.name == name)
                ).scalar_one_or_none()
                if not existing:
                    session.add(Manufacturer(name=name))
    debug_log(f"Производители загружены ({len(names)})")


def load_categories(csv_path):
    df = read_csv(csv_path)
    col = 'Категория товара'
    if not col:
        debug_log("Не найдена колонка с категориями")
        return
    names = df[col].dropna().unique()
    with session_scope() as session:
        for name in names:
            name = safe_str(name)
            if name:
                existing = session.execute(
                    select(Category).where(Category.name == name)
                    ).scalar_one_or_none()
                if not existing:
                    session.add(Category(name=name))
    debug_log(f"Категории загружены ({len(names)})")


# загрузка основных таблиц
def load_users(csv_path, role_dict):
    df = read_csv(csv_path)
    role_col = 'Роль сотрудника'
    fio_col = 'ФИО'
    login_col = 'Логин'
    password_col = 'Пароль'
    if not all([role_col, fio_col, login_col, password_col]):
        debug_log("Не найдены все необходимые колонки для пользователей")
        return
    with session_scope() as session:
        for idx, row in df.iterrows():
            role_name = safe_str(row[role_col])
            full_name = safe_str(row[fio_col])
            login = safe_str(row[login_col])
            password = safe_str(row[password_col])
            if not all([role_name, full_name, login, password]):
                debug_log(f"Строка {idx+2}: пропущена из-за отсутствия данных")
                continue
            role_id = role_dict.get(role_name)
            if not role_id:
                debug_log(f"Строка {idx+2}: роль '{role_name}' не найдена")
                continue
            existing = session.execute(
                select(User).where(User.login == login)
                ).scalar_one_or_none()
            if existing:
                existing.full_name = full_name
                existing.password = password
                existing.role_id = role_id
                debug_log(f"Обновлен пользователь: {login}")
            else:
                session.add(
                    User(role_id=role_id, full_name=full_name,
                         login=login, password=password)
                    )
                debug_log(f"Добавлен пользователь: {login}")
    debug_log("Пользователи загружены")


def load_products(csv_path, supplier_dict, manufacturer_dict, category_dict):
    df = read_csv(csv_path)

    col_article = 'Артикул'
    col_name = 'Наименование товара'
    col_unit = 'Единица измерения'
    col_price = 'Цена'
    col_supplier = 'Поставщик'
    col_manufacturer = 'Производитель'
    col_category = 'Категория товара'
    col_discount = 'Действующая скидка'
    col_stock = 'Кол-во на складе'
    col_description = 'Описание товара'
    col_photo = 'Фото'

    required = [col_article, col_name, col_unit, col_price,
                col_supplier, col_manufacturer, col_category]
    if not all(required):
        debug_log("Отсутствуют обязательные колонки для товаров")
        return
    with session_scope() as session:
        for idx, row in df.iterrows():
            article = safe_str(row[col_article])
            name = safe_str(row[col_name])
            unit = safe_str(row[col_unit])
            price = safe_float(row[col_price])
            supplier_name = safe_str(row[col_supplier])
            manufacturer_name = safe_str(row[col_manufacturer])
            category_name = safe_str(row[col_category])
            discount = safe_int(row[col_discount]) if col_discount else 0
            stock = safe_int(row[col_stock]) if col_stock else 0
            desc = safe_str(row[col_description]) if col_description else None
            photo = safe_str(row[col_photo]) if col_photo else None

            if not all([article, name, unit, price,
                        supplier_name, manufacturer_name, category_name]):
                debug_log(f"Товар строка {idx+2}: пропущен, нет нужных данных")
                continue

            supplier_id = supplier_dict.get(supplier_name)
            manufacturer_id = manufacturer_dict.get(manufacturer_name)
            category_id = category_dict.get(category_name)

            if None in (supplier_id, manufacturer_id, category_id):
                missing = []
                if supplier_id is None:
                    missing.append('поставщик')
                if manufacturer_id is None:
                    missing.append('производитель')
                if category_id is None:
                    missing.append('категория')
                debug_log(f"Товар {article}:пропущен, нет{', '.join(missing)}")
                continue

            existing = session.execute(
                select(Product).where(Product.article == article)
                ).scalar_one_or_none()
            if existing:
                existing.name = name
                existing.unit = unit
                existing.price = price
                existing.supplier_id = supplier_id
                existing.manufacturer_id = manufacturer_id
                existing.category_id = category_id
                existing.discount = discount
                existing.stock_quantity = stock
                existing.description = desc
                existing.photo = photo
                debug_log(f"Обновлен товар: {article}")
            else:
                session.add(Product(
                    article=article, name=name, unit=unit, price=price,
                    supplier_id=supplier_id, manufacturer_id=manufacturer_id,
                    category_id=category_id, discount=discount,
                    stock_quantity=stock, description=desc, photo=photo
                ))
                debug_log(f"Добавлен товар: {article}")
    debug_log("Товары загружены")


# парсинг строки вида 'А112Т4, 2, F635R4, 2' в заказах
def parse_order_items(article_string):
    if pd.isna(article_string):
        return []
    parts = [p.strip() for p in str(article_string).split(',')]
    items = []
    for i in range(0, len(parts), 2):
        if i+1 < len(parts):
            try:
                qty = int(float(parts[i+1]))
                items.append((parts[i], qty))
            except (ValueError, TypeError):
                pass
    return items


def load_orders(csv_path, pickup_dict, user_dict, status_dict, product_dict):
    df = read_csv(csv_path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    col_order_num = 'Номер заказа'
    col_article_str = 'Артикул заказа'
    col_order_date = 'Дата заказа'
    col_delivery_date = 'Дата доставки'
    col_address = 'Адрес пункта выдачи'
    col_full_name = 'ФИО авторизированного клиента'
    col_pickup_code = 'Код для получения'
    col_status = 'Статус заказа'
    if not all([col_order_num, col_article_str, col_order_date,
                col_delivery_date, col_address, col_full_name,
                col_pickup_code, col_status]):
        debug_log("Не найдены все необходимые колонки для заказов")
        return

    # словарь для сопоставления номеров пунктов выдачи с адресами
    points_df = read_csv(os.path.join('data', 'Пункты_выдачи_import.csv'))
    points_df.columns = points_df.columns.str.strip()
    address_col = 'Адрес'
    num_to_address = {}
    for idx, row in points_df.iterrows():
        num_to_address[idx + 1] = safe_str(row[address_col])
    debug_log(f"Создан словарь пунктов выдачи: {len(num_to_address)} записей")

    with session_scope() as session:
        for idx, row in df.iterrows():
            order_num = safe_int(row[col_order_num])
            article_string = row[col_article_str]
            order_date_str = row[col_order_date]
            delivery_date_str = row[col_delivery_date]
            address_num = safe_int(row[col_address])
            full_name = safe_str(row[col_full_name])
            pickup_code = safe_str(row[col_pickup_code])
            status_name = safe_str(row[col_status])

            if not all([order_num, address_num, full_name,
                        pickup_code, status_name]):
                debug_log(f"Заказ строка {idx+2}: пропущен, нет нужных данных")
                continue

            # преобразование номера в адрес
            address = num_to_address.get(address_num)
            if not address:
                debug_log(f"Заказ №{order_num}:")
                debug_log(f"номер пункта выдачи {address_num} не найден")
                continue

            pickup_id = pickup_dict.get(address)
            user_id = user_dict.get(full_name)
            status_id = status_dict.get(status_name)

            if None in (pickup_id, user_id, status_id):
                missing = []
                if pickup_id is None:
                    missing.append(f'пункт выдачи (адрес: {address})')
                if user_id is None:
                    missing.append(f'пользователь ({full_name})')
                if status_id is None:
                    missing.append(f'статус ({status_name})')
                debug_log(f"Заказ №{order_num}: нет{', '.join(missing)}")
                continue

            if session.execute(
                select(Order).where(Order.order_number == order_num)
            ).scalar_one_or_none():
                debug_log(f"Заказ №{order_num} уже существует")
                continue

            try:
                order_date = pd.to_datetime(order_date_str, errors='coerce')
                delivery_date = pd.to_datetime(delivery_date_str,
                                               errors='coerce')
                if pd.isna(order_date) or pd.isna(delivery_date):
                    debug_log(f"Заказ №{order_num}: пропущен из-за дат")
                    continue
            except Exception as e:
                debug_log(f"Заказ №{order_num}: ошибка в датах: {e}")
                continue

            order = Order(
                order_number=order_num,
                order_date=order_date.date(),
                delivery_date=delivery_date.date(),
                pickup_point_id=pickup_id,
                user_id=user_id,
                pickup_code=pickup_code,
                status_id=status_id
            )
            session.add(order)
            session.flush()

            items = parse_order_items(article_string)
            if not items:
                debug_log(f"Заказ №{order_num}: отсутствие позиций/формат")
                continue

            for article, qty in items:
                if article in product_dict and qty > 0:
                    session.add(
                        OrderItem(order_id=order.id, product_article=article,
                                  quantity=qty))
                else:
                    debug_log(f"Заказ №{order_num}: товар {article} не найден")
    debug_log("Заказы и позиции загружены")


# процесс загрузки
def main():
    data_dir = os.path.join(BASE_DIR, 'data')
    if not os.path.exists(data_dir):
        debug_log(f"Папка {data_dir} не найдена")
        return

    tovar_path = os.path.join(data_dir, 'Tovar.csv')
    users_path = os.path.join(data_dir, 'user_import.csv')
    orders_path = os.path.join(data_dir, 'Заказ_import.csv')
    points_path = os.path.join(data_dir, 'Пункты_выдачи_import.csv')

    for p in [tovar_path, users_path, orders_path, points_path]:
        if not os.path.exists(p):
            debug_log(f"Файл {p} не найден")
            return

    # справочники
    load_roles()
    load_order_statuses()
    load_pickup_points(points_path)
    load_suppliers(tovar_path)
    load_manufacturers(tovar_path)
    load_categories(tovar_path)

    # словари
    with session_scope() as session:
        role_dict = {r.name: r.id for r in session.execute(
            select(Role)).scalars()}
        supplier_dict = {s.name: s.id for s in session.execute(
            select(Supplier)).scalars()}
        manufacturer_dict = {m.name: m.id for m in session.execute(
            select(Manufacturer)).scalars()}
        category_dict = {c.name: c.id for c in session.execute(
            select(Category)).scalars()}
        pickup_dict = {p.address: p.id for p in session.execute(
            select(PickupPoint)).scalars()}
        status_dict = {st.name: st.id for st in session.execute(
            select(OrderStatus)).scalars()}
        debug_log(f"Загружено словарей: поставщиков={len(supplier_dict)}, "
                  f"производителей={len(manufacturer_dict)}, "
                  f"категорий={len(category_dict)}, "
                  f"пунктов выдачи={len(pickup_dict)}")

    # пользователи
    load_users(users_path, role_dict)
    with session_scope() as session:
        user_dict = {u.full_name: u.id for u in session.execute(
            select(User)).scalars()}
        debug_log(f"Загружено пользователей: {len(user_dict)}")

    # товары
    load_products(tovar_path, supplier_dict, manufacturer_dict, category_dict)
    with session_scope() as session:
        product_dict = {p.article: p.article for p in session.execute(
            select(Product)).scalars()}
        debug_log(f"Загружено товаров: {len(product_dict)}")

    # заказы
    load_orders(orders_path, pickup_dict, user_dict, status_dict, product_dict)

    print("Импорт данных успешно завершен")


if __name__ == "__main__":
    main()
